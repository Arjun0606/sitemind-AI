"""
Admin API Router
Onboarding, billing, configuration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from services import billing_service, pricing_service
from database import db
from utils.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================================
# SCHEMAS
# ============================================================================

class CreateCompanyRequest(BaseModel):
    name: str
    gstin: Optional[str] = None
    billing_email: Optional[str] = None
    is_pilot: bool = False


class CreateUserRequest(BaseModel):
    company_id: str
    name: str
    phone: str
    email: Optional[str] = None
    role: str = "site_engineer"


class CreateProjectRequest(BaseModel):
    company_id: str
    name: str
    location: Optional[str] = None
    project_type: str = "residential"


# ============================================================================
# ONBOARDING
# ============================================================================

@router.post("/companies")
async def create_company(request: CreateCompanyRequest):
    """Create a new company"""
    company = await db.create_company(
        name=request.name,
        gstin=request.gstin,
        billing_email=request.billing_email,
        is_pilot=request.is_pilot,
    )
    
    if not company:
        raise HTTPException(status_code=500, detail="Failed to create company")
    
    logger.info(f"🏢 Created company: {request.name}")
    
    return company


@router.post("/users")
async def create_user(request: CreateUserRequest):
    """Create a new user"""
    # Check if phone already exists
    existing = await db.get_user_by_phone(request.phone)
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    user = await db.create_user(
        company_id=request.company_id,
        name=request.name,
        phone=request.phone,
        email=request.email,
        role=request.role,
    )
    
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    logger.info(f"👤 Created user: {request.name} ({request.phone})")
    
    return user


@router.post("/projects")
async def create_project(request: CreateProjectRequest):
    """Create a new project"""
    project = await db.create_project(
        company_id=request.company_id,
        name=request.name,
        location=request.location,
        project_type=request.project_type,
    )
    
    if not project:
        raise HTTPException(status_code=500, detail="Failed to create project")
    
    logger.info(f"🏗️ Created project: {request.name}")
    
    return project


# ============================================================================
# LOOKUP
# ============================================================================

@router.get("/companies/{company_id}")
async def get_company(company_id: str):
    """Get company by ID"""
    company = await db.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/companies/{company_id}/users")
async def get_company_users(company_id: str):
    """Get all users for a company"""
    users = await db.get_company_users(company_id)
    return users


@router.get("/companies/{company_id}/projects")
async def get_company_projects(company_id: str):
    """Get all projects for a company"""
    projects = await db.get_company_projects(company_id)
    return projects


@router.get("/users/phone/{phone}")
async def get_user_by_phone(phone: str):
    """Get user by phone number"""
    user = await db.get_user_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============================================================================
# BILLING
# ============================================================================

@router.get("/billing/usage/{company_id}")
async def get_usage(company_id: str):
    """Get current usage for company"""
    usage = billing_service.get_usage(company_id)
    if not usage:
        return {"message": "No usage data yet"}
    return usage


@router.get("/billing/charges/{company_id}")
async def get_charges(company_id: str):
    """Get current charges for company"""
    charges = billing_service.calculate_charges(company_id)
    return charges


@router.post("/billing/invoice/{company_id}")
async def generate_invoice(company_id: str, is_founding: bool = False):
    """Generate invoice for company"""
    # Get previous cycle usage (in real app, fetch from DB)
    previous_usage = billing_service.get_usage(company_id)
    
    invoice = billing_service.generate_invoice(
        company_id=company_id,
        previous_cycle_usage=previous_usage,
        is_founding=is_founding,
    )
    
    return {
        "invoice": invoice,
        "formatted": billing_service.format_invoice(invoice),
    }


# ============================================================================
# PRICING
# ============================================================================

@router.get("/pricing")
async def get_pricing():
    """Get pricing information"""
    return pricing_service.get_pricing()


@router.get("/pricing/calculate")
async def calculate_pricing(
    queries: int = 0,
    documents: int = 0,
    photos: int = 0,
    storage_gb: float = 0,
):
    """Calculate pricing for given usage"""
    usage_charges = pricing_service.calculate_usage(
        queries=queries,
        documents=documents,
        photos=photos,
        storage_gb=storage_gb,
    )
    
    return {
        "flat_fee": pricing_service.FLAT_FEE_USD,
        "usage_charges": usage_charges["total_usd"],
        "total": pricing_service.FLAT_FEE_USD + usage_charges["total_usd"],
        "breakdown": usage_charges["breakdown"],
    }
