"""
SiteMind Admin API
Complete API for dashboard and onboarding

Endpoints for:
- Company management
- Project management
- User management
- Billing & usage
- Analytics & reports
- Onboarding
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from services import (
    billing_service,
    pricing_service,
    wow_service,
    report_service,
    project_manager,
    alert_service,
)
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


class OnboardCompanyRequest(BaseModel):
    """Complete onboarding request"""
    company_name: str
    company_gstin: Optional[str] = None
    billing_email: str
    is_pilot: bool = False
    
    # Admin user
    admin_name: str
    admin_phone: str
    admin_email: Optional[str] = None
    
    # Initial projects (optional)
    projects: List[dict] = []
    
    # Additional team members (optional)
    team_members: List[dict] = []


# ============================================================================
# ONBOARDING (The money endpoint)
# ============================================================================

@router.post("/onboard")
async def onboard_company(request: OnboardCompanyRequest):
    """
    Complete company onboarding in one call
    
    Creates:
    1. Company
    2. Admin user
    3. Initial projects
    4. Team members
    
    Returns everything needed to get started.
    """
    logger.info(f"🚀 Onboarding: {request.company_name}")
    
    # 1. Create company
    company = await db.create_company(
        name=request.company_name,
        gstin=request.company_gstin,
        billing_email=request.billing_email,
        is_pilot=request.is_pilot,
    )
    
    if not company:
        # Fallback for when DB not configured
        company = {
            "id": f"company_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "name": request.company_name,
        }
    
    company_id = company.get("id", company.get("name", "unknown"))
    
    # 2. Create admin user
    admin = await db.create_user(
        company_id=company_id,
        name=request.admin_name,
        phone=request.admin_phone,
        email=request.admin_email,
        role="admin",
    )
    
    if not admin:
        admin = {
            "id": f"user_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "name": request.admin_name,
            "phone": request.admin_phone,
        }
    
    # 3. Create projects
    created_projects = []
    for proj in request.projects:
        project = await db.create_project(
            company_id=company_id,
            name=proj.get("name", "New Project"),
            location=proj.get("location"),
            project_type=proj.get("project_type", "residential"),
        )
        
        if not project:
            # Create in project manager
            project = project_manager.create_project(
                company_id=company_id,
                project_id=f"proj_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                name=proj.get("name", "New Project"),
                location=proj.get("location", ""),
                project_type=proj.get("project_type", "residential"),
            )
            project = {"id": project.id, "name": project.name}
        
        created_projects.append(project)
    
    # 4. Create team members
    created_members = []
    for member in request.team_members:
        user = await db.create_user(
            company_id=company_id,
            name=member.get("name", "Team Member"),
            phone=member.get("phone"),
            role=member.get("role", "site_engineer"),
        )
        
        if user:
            created_members.append(user)
    
    # 5. Initialize billing tracking
    billing_service.get_or_create_usage(company_id, request.company_name)
    
    logger.info(f"✅ Onboarded: {request.company_name} with {len(created_projects)} projects, {len(created_members) + 1} users")
    
    return {
        "status": "success",
        "message": f"Welcome to SiteMind, {request.company_name}!",
        "company": company,
        "admin": admin,
        "projects": created_projects,
        "team_members": created_members,
        "next_steps": [
            f"1. Admin ({request.admin_name}) will receive WhatsApp welcome message",
            "2. Team members can start sending messages to SiteMind",
            "3. Upload blueprints and documents for each project",
            "4. Start asking questions!",
        ],
        "whatsapp_number": "+14155238886",  # Twilio sandbox
    }


# ============================================================================
# COMPANY CRUD
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
        company = {
            "id": f"company_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "name": request.name,
            "is_pilot": request.is_pilot,
        }
    
    logger.info(f"🏢 Created company: {request.name}")
    return company


@router.get("/companies/{company_id}")
async def get_company(company_id: str):
    """Get company by ID"""
    company = await db.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/companies")
async def list_companies(limit: int = 50, offset: int = 0):
    """List all companies"""
    companies = await db.select("companies", limit=limit)
    return {"companies": companies, "count": len(companies)}


# ============================================================================
# USER CRUD
# ============================================================================

@router.post("/users")
async def create_user(request: CreateUserRequest):
    """Create a new user"""
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
        user = {
            "id": f"user_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "name": request.name,
            "phone": request.phone,
        }
    
    logger.info(f"👤 Created user: {request.name} ({request.phone})")
    return user


@router.get("/users/phone/{phone}")
async def get_user_by_phone(phone: str):
    """Get user by phone number"""
    user = await db.get_user_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/companies/{company_id}/users")
async def get_company_users(company_id: str):
    """Get all users for a company"""
    users = await db.get_company_users(company_id)
    return {"users": users, "count": len(users)}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    success = await db.delete("users", {"id": user_id})
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted"}


# ============================================================================
# PROJECT CRUD
# ============================================================================

@router.post("/projects")
async def create_project(request: CreateProjectRequest):
    """Create a new project"""
    project = await db.create_project(
        company_id=request.company_id,
        name=request.name,
        location=request.location,
        project_type=request.project_type,
    )
    
    # Also create in project manager
    pm_project = project_manager.create_project(
        company_id=request.company_id,
        project_id=project.get("id") if project else f"proj_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        name=request.name,
        location=request.location or "",
        project_type=request.project_type,
    )
    
    if not project:
        project = {"id": pm_project.id, "name": pm_project.name}
    
    logger.info(f"🏗️ Created project: {request.name}")
    return project


@router.get("/companies/{company_id}/projects")
async def get_company_projects(company_id: str):
    """Get all projects for a company"""
    # Try database first
    projects = await db.get_company_projects(company_id)
    
    # Also get from project manager
    pm_projects = project_manager.get_company_projects(company_id)
    
    # Combine
    all_projects = projects + [
        {"id": p.id, "name": p.name, "location": p.location, "stage": p.stage}
        for p in pm_projects
        if not any(dp.get("id") == p.id for dp in projects)
    ]
    
    return {"projects": all_projects, "count": len(all_projects)}


@router.patch("/projects/{project_id}")
async def update_project(project_id: str, updates: dict):
    """Update a project"""
    project = await db.update("projects", {"id": project_id}, updates)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ============================================================================
# BILLING & USAGE
# ============================================================================

@router.get("/billing/usage/{company_id}")
async def get_usage(company_id: str):
    """Get current usage for company"""
    usage = billing_service.get_usage(company_id)
    if not usage:
        return {
            "message": "No usage data yet",
            "queries": 0,
            "documents": 0,
            "photos": 0,
            "storage_gb": 0,
        }
    return usage


@router.get("/billing/charges/{company_id}")
async def get_charges(company_id: str):
    """Get current charges for company"""
    charges = billing_service.calculate_charges(company_id)
    return charges


@router.post("/billing/invoice/{company_id}")
async def generate_invoice(
    company_id: str,
    is_founding: bool = False,
    is_annual: bool = False,
):
    """Generate invoice for company"""
    previous_usage = billing_service.get_usage(company_id)
    
    invoice = pricing_service.generate_invoice(
        company_name=previous_usage.get("company_name", "Company") if previous_usage else "Company",
        previous_usage=previous_usage,
        is_founding=is_founding,
        is_annual=is_annual,
    )
    
    return {
        "invoice": invoice,
        "formatted": pricing_service.format_invoice(invoice),
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


# ============================================================================
# ANALYTICS & REPORTS
# ============================================================================

@router.get("/analytics/{company_id}")
async def get_analytics(company_id: str):
    """Get company analytics"""
    usage = billing_service.get_usage(company_id)
    roi = wow_service.get_week1_roi(company_id)
    alerts = alert_service.get_alert_count(company_id)
    projects = project_manager.get_company_projects(company_id)
    
    return {
        "usage": usage,
        "roi": roi,
        "alerts": alerts,
        "projects": {
            "total": len(projects),
            "active": len([p for p in projects if p.stage == "active"]),
        },
    }


@router.get("/reports/weekly/{company_id}")
async def get_weekly_report(company_id: str):
    """Get weekly report for company"""
    usage = billing_service.get_usage(company_id) or {}
    roi = wow_service.get_week1_roi(company_id)
    
    report = report_service.generate_weekly_report(
        company_id=company_id,
        company_name=usage.get("company_name", "Company"),
        activity_data={
            "queries": usage.get("queries", 0),
            "photos": usage.get("photos", 0),
            "documents": usage.get("documents", 0),
            "safety_flags": roi.get("safety_flags", 0),
            "conflicts": 0,
            "active_users": roi.get("active_users", 0),
            "active_projects": len(project_manager.get_active_projects(company_id)),
        },
    )
    
    return {
        "report": {
            "company": report.company_name,
            "period": f"{report.week_start} to {report.week_end}",
            "queries": report.total_queries,
            "photos": report.total_photos,
            "hours_saved": report.hours_saved,
            "value_inr": report.time_value_inr + report.safety_value_inr,
        },
        "formatted": report_service.format_weekly_whatsapp(report),
    }


@router.get("/reports/roi/{company_id}")
async def get_roi_report(company_id: str):
    """Get ROI report"""
    roi = wow_service.get_week1_roi(company_id)
    company_name = billing_service.get_usage(company_id)
    company_name = company_name.get("company_name", "Company") if company_name else "Company"
    
    return {
        "roi": roi,
        "formatted": wow_service.format_week1_report(company_id, company_name),
    }


# ============================================================================
# ALERTS
# ============================================================================

@router.get("/alerts/{company_id}")
async def get_alerts(company_id: str, project_id: str = None):
    """Get pending alerts for company"""
    alerts = alert_service.get_pending_alerts(company_id, project_id)
    
    return {
        "alerts": [
            {
                "id": a.id,
                "type": a.alert_type.value,
                "priority": a.priority.value,
                "title": a.title,
                "message": a.message,
                "action": a.action_required,
                "created": a.created_at,
            }
            for a in alerts
        ],
        "summary": alert_service.format_alert_summary(alerts),
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user_id: str):
    """Acknowledge an alert"""
    alert_service.mark_acknowledged(alert_id, user_id)
    return {"status": "acknowledged"}


# ============================================================================
# DASHBOARD DATA
# ============================================================================

@router.get("/dashboard/{company_id}")
async def get_dashboard_data(company_id: str):
    """Get all data for dashboard in one call"""
    
    # Usage
    usage = billing_service.get_usage(company_id) or {
        "queries": 0,
        "documents": 0,
        "photos": 0,
        "storage_gb": 0,
    }
    
    # Charges
    charges = billing_service.calculate_charges(company_id)
    
    # ROI
    roi = wow_service.get_week1_roi(company_id)
    
    # Projects
    projects = project_manager.get_company_projects(company_id)
    
    # Alerts
    alerts = alert_service.get_alert_count(company_id)
    
    return {
        "company_id": company_id,
        "usage": {
            "queries": usage.get("queries", 0),
            "queries_limit": 1000,
            "documents": usage.get("documents", 0),
            "documents_limit": 50,
            "photos": usage.get("photos", 0),
            "photos_limit": 200,
            "storage_gb": usage.get("storage_gb", 0),
            "storage_limit_gb": 25,
        },
        "billing": {
            "flat_fee": charges["flat_fee"],
            "usage_charges": charges["usage_charges"],
            "total": charges["total"],
            "cycle_start": usage.get("cycle_start"),
            "cycle_end": usage.get("cycle_end"),
        },
        "roi": {
            "hours_saved": roi["hours_saved"],
            "value_inr": roi["total_value_inr"],
            "safety_flags": roi["safety_flags"],
        },
        "projects": {
            "total": len(projects),
            "active": len([p for p in projects if p.stage in ["active", "planning", "finishing"]]),
            "list": [
                {"id": p.id, "name": p.name, "stage": p.stage, "queries": p.total_queries}
                for p in projects[:10]
            ],
        },
        "alerts": alerts,
    }
