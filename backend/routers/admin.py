"""
SiteMind Admin Router
Admin endpoints for managing builders, projects, blueprints, and site engineers
"""

import time
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from config import settings
from utils.logger import logger
from utils.database import get_async_session
from models.database import Builder, Project, Blueprint, SiteEngineer, ChatLog
from models.schemas import (
    BuilderCreate, BuilderUpdate, BuilderResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    BlueprintCreate, BlueprintResponse,
    SiteEngineerCreate, SiteEngineerResponse,
)
from services.storage_service import storage_service
from services.gemini_service import gemini_service
from services.memory_service import memory_service
from services.whatsapp_client import whatsapp_client


router = APIRouter(prefix="/admin", tags=["Admin"])


# ===========================================
# Builder Endpoints
# ===========================================

@router.post("/builders", response_model=BuilderResponse)
async def create_builder(
    builder: BuilderCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new builder/client"""
    db_builder = Builder(**builder.model_dump())
    db.add(db_builder)
    await db.commit()
    await db.refresh(db_builder)
    
    logger.info(f"Builder created: {db_builder.name} ({db_builder.id})")
    return db_builder


@router.get("/builders", response_model=List[BuilderResponse])
async def list_builders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
):
    """List all builders"""
    result = await db.execute(
        select(Builder)
        .order_by(Builder.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/builders/{builder_id}", response_model=BuilderResponse)
async def get_builder(
    builder_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """Get a specific builder"""
    result = await db.execute(
        select(Builder).where(Builder.id == builder_id)
    )
    builder = result.scalar_one_or_none()
    
    if not builder:
        raise HTTPException(status_code=404, detail="Builder not found")
    
    return builder


@router.patch("/builders/{builder_id}", response_model=BuilderResponse)
async def update_builder(
    builder_id: UUID,
    builder_update: BuilderUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """Update a builder"""
    result = await db.execute(
        select(Builder).where(Builder.id == builder_id)
    )
    builder = result.scalar_one_or_none()
    
    if not builder:
        raise HTTPException(status_code=404, detail="Builder not found")
    
    for field, value in builder_update.model_dump(exclude_unset=True).items():
        setattr(builder, field, value)
    
    await db.commit()
    await db.refresh(builder)
    
    logger.info(f"Builder updated: {builder.name}")
    return builder


# ===========================================
# Project Endpoints
# ===========================================

@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new project/site"""
    # Verify builder exists
    result = await db.execute(
        select(Builder).where(Builder.id == project.builder_id)
    )
    builder = result.scalar_one_or_none()
    if not builder:
        raise HTTPException(status_code=404, detail="Builder not found")
    
    # Create project
    db_project = Project(**project.model_dump())
    db_project.supermemory_namespace = str(db_project.id)  # Use project ID as namespace
    db.add(db_project)
    
    # Update builder's site count
    builder.sites_count += 1
    
    await db.commit()
    await db.refresh(db_project)
    
    logger.info(f"Project created: {db_project.name} ({db_project.id})")
    return db_project


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    builder_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
):
    """List all projects, optionally filtered by builder or status"""
    query = select(Project)
    
    if builder_id:
        query = query.where(Project.builder_id == builder_id)
    if status:
        query = query.where(Project.status == status)
    
    query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """Get a specific project with details"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get blueprint count
    count_result = await db.execute(
        select(func.count(Blueprint.id))
        .where(Blueprint.project_id == project_id)
    )
    blueprint_count = count_result.scalar()
    
    response = ProjectResponse.model_validate(project)
    response.blueprints_count = blueprint_count
    
    return response


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """Update a project"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for field, value in project_update.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    logger.info(f"Project updated: {project.name}")
    return project


# ===========================================
# Blueprint Endpoints
# ===========================================

@router.post("/projects/{project_id}/blueprints", response_model=BlueprintResponse)
async def upload_blueprint(
    project_id: UUID,
    file: UploadFile = File(...),
    category: str = Form("other"),
    revision: Optional[str] = Form(None),
    drawing_number: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Upload a blueprint PDF to a project
    
    This will:
    1. Upload the file to S3
    2. Upload to Gemini for AI analysis
    3. Store metadata in database
    """
    start_time = time.time()
    
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Read file content
    content = await file.read()
    
    # Upload to S3
    storage_result = await storage_service.upload_file(
        file_content=content,
        filename=file.filename,
        project_id=str(project_id),
        category=category,
    )
    
    if storage_result.get("error"):
        raise HTTPException(status_code=400, detail=storage_result["error"])
    
    # Create blueprint record
    blueprint = Blueprint(
        project_id=project_id,
        filename=file.filename,
        file_url=storage_result["file_url"],
        file_size=storage_result["file_size"],
        category=category,
        revision=revision,
        drawing_number=drawing_number,
    )
    db.add(blueprint)
    await db.commit()
    await db.refresh(blueprint)
    
    # Upload to Gemini (in background-ish, but we wait for it)
    try:
        # Save temp file for Gemini upload
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            gemini_result = await gemini_service.upload_blueprint(
                file_path=tmp_path,
                display_name=f"{project.name} - {file.filename}",
            )
            
            if gemini_result:
                blueprint.gemini_file_id = gemini_result["file_id"]
                blueprint.gemini_file_uri = gemini_result["uri"]
                blueprint.is_processed = True
                await db.commit()
                
                logger.info(f"Blueprint uploaded and processed: {file.filename}")
        finally:
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Failed to process blueprint with Gemini: {e}")
        blueprint.processing_error = str(e)
        await db.commit()
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info(f"Blueprint upload completed in {elapsed_ms}ms")
    
    return blueprint


@router.get("/projects/{project_id}/blueprints", response_model=List[BlueprintResponse])
async def list_blueprints(
    project_id: UUID,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """List all blueprints for a project"""
    query = select(Blueprint).where(Blueprint.project_id == project_id)
    
    if category:
        query = query.where(Blueprint.category == category)
    
    query = query.order_by(Blueprint.uploaded_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.delete("/blueprints/{blueprint_id}")
async def delete_blueprint(
    blueprint_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a blueprint"""
    result = await db.execute(
        select(Blueprint).where(Blueprint.id == blueprint_id)
    )
    blueprint = result.scalar_one_or_none()
    
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")
    
    # Delete from Gemini
    if blueprint.gemini_file_id:
        await gemini_service.delete_file(blueprint.gemini_file_id)
    
    # Delete from S3 (would need to extract key from URL)
    # For now, just delete from DB
    
    await db.delete(blueprint)
    await db.commit()
    
    logger.info(f"Blueprint deleted: {blueprint.filename}")
    return {"status": "deleted"}


# ===========================================
# Site Engineer Endpoints
# ===========================================

@router.post("/projects/{project_id}/engineers", response_model=SiteEngineerResponse)
async def add_site_engineer(
    project_id: UUID,
    engineer: SiteEngineerCreate,
    send_welcome: bool = Query(True, description="Send welcome message via WhatsApp"),
    db: AsyncSession = Depends(get_async_session),
):
    """Add a site engineer to a project"""
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if phone number already registered
    existing = await db.execute(
        select(SiteEngineer).where(SiteEngineer.phone_number == engineer.phone_number)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400, 
            detail="Phone number already registered to another project"
        )
    
    # Create engineer
    db_engineer = SiteEngineer(
        project_id=project_id,
        name=engineer.name,
        phone_number=engineer.phone_number,
        role=engineer.role,
    )
    db.add(db_engineer)
    await db.commit()
    await db.refresh(db_engineer)
    
    # Send welcome message
    if send_welcome:
        await whatsapp_client.send_welcome_message(
            to=engineer.phone_number,
            project_name=project.name,
        )
    
    logger.info(f"Site engineer added: {engineer.name} to {project.name}")
    return db_engineer


@router.get("/projects/{project_id}/engineers", response_model=List[SiteEngineerResponse])
async def list_site_engineers(
    project_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """List all site engineers for a project"""
    result = await db.execute(
        select(SiteEngineer)
        .where(SiteEngineer.project_id == project_id)
        .order_by(SiteEngineer.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/engineers/{engineer_id}")
async def remove_site_engineer(
    engineer_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """Remove a site engineer (deactivate)"""
    result = await db.execute(
        select(SiteEngineer).where(SiteEngineer.id == engineer_id)
    )
    engineer = result.scalar_one_or_none()
    
    if not engineer:
        raise HTTPException(status_code=404, detail="Engineer not found")
    
    engineer.is_active = False
    await db.commit()
    
    logger.info(f"Site engineer deactivated: {engineer.name}")
    return {"status": "deactivated"}


# ===========================================
# Memory Endpoints
# ===========================================

@router.post("/projects/{project_id}/memory")
async def add_project_memory(
    project_id: UUID,
    content: str = Form(...),
    doc_type: str = Form("note"),
    drawing: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Add a memory to the project's knowledge base
    
    Use this to add:
    - RFIs (Request for Information)
    - Change Orders
    - Meeting Notes
    - Important Decisions
    """
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Add to memory
    metadata = {"drawing": drawing} if drawing else {}
    result = await memory_service.add_document(
        project_id=str(project_id),
        content=content,
        doc_type=doc_type,
        metadata=metadata,
    )
    
    logger.info(f"Memory added to project {project.name}: {doc_type}")
    return result


@router.get("/projects/{project_id}/memory")
async def get_project_memories(
    project_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
):
    """Get all memories for a project"""
    memories = await memory_service.get_project_memories(
        project_id=str(project_id),
        limit=limit,
    )
    return {"memories": memories, "count": len(memories)}


@router.get("/projects/{project_id}/memory/search")
async def search_project_memory(
    project_id: UUID,
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
):
    """Search project memory"""
    result = await memory_service.search_memory(
        project_id=str(project_id),
        query=query,
        limit=limit,
    )
    return result

