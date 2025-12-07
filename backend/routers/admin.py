"""
SiteMind Admin API
Administrative endpoints for customer management and onboarding

ENDPOINTS:
- Onboarding (start, organization, users, projects, complete)
- Configuration (org, project, user settings)
- Feature toggles
- Analytics
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from utils.logger import logger

from services.onboarding_service import onboarding_service
from services.config_service import config_service
from services.roi_service import roi_service
from services.engagement_service import engagement_service
from services.storage_service import StorageService


router = APIRouter(prefix="/admin", tags=["Admin"])

storage = StorageService()


# =============================================================================
# MODELS
# =============================================================================

class OrganizationCreate(BaseModel):
    name: str
    gstin: Optional[str] = None
    address: Optional[str] = None
    plan: str = "professional"


class AdminUserCreate(BaseModel):
    name: str
    email: str
    phone: str


class ProjectCreate(BaseModel):
    name: str
    location: Optional[str] = None
    project_type: str = "residential"


class TeamMemberCreate(BaseModel):
    project_id: str
    name: str
    phone: str
    role: str = "site_engineer"


class ConfigUpdate(BaseModel):
    config: Dict[str, Any]


class QuickSetup(BaseModel):
    organization_name: str
    admin_name: str
    admin_email: str
    admin_phone: str
    projects: Optional[List[Dict]] = None
    team_members: Optional[List[Dict]] = None
    config: Optional[Dict] = None
    send_welcome: bool = True


# =============================================================================
# ONBOARDING ENDPOINTS
# =============================================================================

@router.post("/onboarding/start")
async def start_onboarding():
    """Start a new onboarding session"""
    session = onboarding_service.start_session()
    return {
        "session_id": session.id,
        "status": session.status,
        "created_at": session.created_at,
    }


@router.post("/onboarding/{session_id}/organization")
async def create_organization(session_id: str, org: OrganizationCreate):
    """Create organization in onboarding session"""
    result = onboarding_service.create_organization(
        session_id=session_id,
        name=org.name,
        gstin=org.gstin,
        address=org.address,
        plan=org.plan,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/onboarding/{session_id}/admin-user")
async def create_admin_user(session_id: str, user: AdminUserCreate):
    """Create admin user in onboarding session"""
    result = onboarding_service.create_admin_user(
        session_id=session_id,
        name=user.name,
        email=user.email,
        phone=user.phone,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/onboarding/{session_id}/project")
async def add_project(session_id: str, project: ProjectCreate):
    """Add project to onboarding session"""
    result = onboarding_service.add_project(
        session_id=session_id,
        name=project.name,
        location=project.location,
        project_type=project.project_type,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/onboarding/{session_id}/team-member")
async def add_team_member(session_id: str, member: TeamMemberCreate):
    """Add team member to onboarding session"""
    result = onboarding_service.add_team_member(
        session_id=session_id,
        project_id=member.project_id,
        name=member.name,
        phone=member.phone,
        role=member.role,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/onboarding/{session_id}/config")
async def set_onboarding_config(session_id: str, config: ConfigUpdate):
    """Set configuration in onboarding session"""
    onboarding_service.set_config(session_id, config.config)
    return {"status": "ok"}


@router.post("/onboarding/{session_id}/complete")
async def complete_onboarding(session_id: str, send_welcome: bool = True):
    """Complete onboarding and send welcome messages"""
    result = await onboarding_service.complete_onboarding(session_id, send_welcome)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/onboarding/{session_id}")
async def get_onboarding_session(session_id: str):
    """Get onboarding session status"""
    session = onboarding_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "organization_id": session.organization_id,
        "organization_name": session.organization_name,
        "admin_user": session.admin_user,
        "projects": session.projects,
        "team_members": session.team_members,
        "config": session.config,
        "status": session.status,
        "created_at": session.created_at,
        "completed_at": session.completed_at,
    }


@router.post("/quick-setup")
async def quick_setup(setup: QuickSetup):
    """Quick setup - create everything in one call"""
    result = await onboarding_service.quick_setup(
        organization_name=setup.organization_name,
        admin_name=setup.admin_name,
        admin_email=setup.admin_email,
        admin_phone=setup.admin_phone,
        projects=setup.projects,
        team_members=setup.team_members,
        config=setup.config,
        send_welcome=setup.send_welcome,
    )
    
    return result


# =============================================================================
# ORGANIZATION ENDPOINTS
# =============================================================================

@router.get("/organizations")
async def list_organizations():
    """List all organizations"""
    return onboarding_service.list_organizations()


@router.get("/organizations/{org_id}")
async def get_organization(org_id: str):
    """Get organization details"""
    org = onboarding_service.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/organizations/{org_id}/config")
async def get_org_config(org_id: str):
    """Get organization configuration"""
    return config_service.get_org_config(org_id)


@router.put("/organizations/{org_id}/config")
async def update_org_config(org_id: str, config: ConfigUpdate):
    """Update organization configuration"""
    config_service.set_org_config(org_id, config.config)
    return {"status": "ok", "config": config_service.get_org_config(org_id)}


# =============================================================================
# PROJECT ENDPOINTS
# =============================================================================

@router.get("/projects")
async def list_projects(org_id: Optional[str] = None):
    """List projects"""
    return onboarding_service.list_projects(org_id)


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    project = onboarding_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/projects/{project_id}/config")
async def get_project_config(project_id: str, org_id: Optional[str] = None):
    """Get project configuration"""
    return config_service.get_project_config(project_id, org_id)


@router.put("/projects/{project_id}/config")
async def update_project_config(project_id: str, config: ConfigUpdate):
    """Update project configuration"""
    config_service.set_project_config(project_id, config.config)
    return {"status": "ok"}


# =============================================================================
# USER ENDPOINTS
# =============================================================================

@router.get("/users")
async def list_users(org_id: Optional[str] = None, project_id: Optional[str] = None):
    """List users"""
    return onboarding_service.list_users(org_id, project_id)


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user details"""
    user = onboarding_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/{user_id}/config")
async def get_user_config(user_id: str, project_id: Optional[str] = None, org_id: Optional[str] = None):
    """Get user configuration"""
    return config_service.get_user_config(user_id, project_id, org_id)


@router.put("/users/{user_id}/config")
async def update_user_config(user_id: str, config: ConfigUpdate):
    """Update user configuration"""
    config_service.set_user_config(user_id, config.config)
    return {"status": "ok"}


# =============================================================================
# FEATURE TOGGLES
# =============================================================================

@router.get("/features")
async def list_features():
    """List all available features"""
    return {"features": config_service.get_all_features()}


@router.get("/organizations/{org_id}/features")
async def get_org_features(org_id: str):
    """Get features enabled for an organization"""
    config = config_service.get_org_config(org_id)
    return config.get("features", {})


@router.post("/organizations/{org_id}/features/{feature}/enable")
async def enable_feature(org_id: str, feature: str):
    """Enable a feature for an organization"""
    config_service.enable_feature(feature, org_id=org_id)
    return {"status": "enabled", "feature": feature}


@router.post("/organizations/{org_id}/features/{feature}/disable")
async def disable_feature(org_id: str, feature: str):
    """Disable a feature for an organization"""
    config_service.disable_feature(feature, org_id=org_id)
    return {"status": "disabled", "feature": feature}


# =============================================================================
# ANALYTICS
# =============================================================================

@router.get("/analytics/overview")
async def get_analytics_overview():
    """Get overall analytics"""
    orgs = onboarding_service.list_organizations()
    projects = onboarding_service.list_projects()
    users = onboarding_service.list_users()
    
    return {
        "organizations": len(orgs),
        "projects": len(projects),
        "users": len(users),
        "active_projects": len([p for p in projects if p.get("status") == "active"]),
    }


@router.get("/analytics/projects/{project_id}/roi")
async def get_project_roi(project_id: str):
    """Get ROI for a project"""
    return roi_service.calculate_roi(project_id)


@router.get("/analytics/projects/{project_id}/activity")
async def get_project_activity(project_id: str):
    """Get activity summary for a project"""
    return engagement_service.generate_daily_summary(project_id)


# =============================================================================
# DOCUMENT UPLOAD
# =============================================================================

@router.post("/projects/{project_id}/documents")
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    user_id: Optional[str] = None,
):
    """Upload a document to a project"""
    content = await file.read()
    
    result = await storage.upload_document(
        project_id=project_id,
        file_content=content,
        file_name=file.filename,
        content_type=file.content_type,
        user_id=user_id,
    )
    
    return result


@router.get("/projects/{project_id}/documents")
async def list_project_documents(project_id: str):
    """List documents for a project"""
    return await storage.list_project_files(project_id, "application")
