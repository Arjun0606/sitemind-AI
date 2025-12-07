"""
SiteMind Admin API
Endpoints for customer onboarding and management

All customization happens through API - no code changes needed for customers.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from services.onboarding_service import onboarding_service, OnboardingStatus
from services.config_service import config_service
from utils.logger import logger


router = APIRouter(prefix="/admin", tags=["Admin"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class StartOnboardingRequest(BaseModel):
    customer_name: str
    contact_email: str
    contact_phone: str
    plan: str = "pilot"


class CreateOrganizationRequest(BaseModel):
    session_id: str
    name: str
    slug: Optional[str] = None
    billing_email: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class CreateAdminUserRequest(BaseModel):
    session_id: str
    name: str
    email: str
    phone: str


class CreateProjectRequest(BaseModel):
    session_id: str
    name: str
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    project_type: str = "residential"
    settings: Optional[Dict[str, Any]] = None


class TeamMember(BaseModel):
    name: str
    phone: str
    role: str = "site_engineer"
    permissions: Optional[Dict[str, bool]] = None


class AddTeamMembersRequest(BaseModel):
    session_id: str
    project_id: str
    members: List[TeamMember]


class QuickSetupSite(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    team: Optional[List[TeamMember]] = None


class QuickSetupRequest(BaseModel):
    company_name: str
    admin_name: str
    admin_email: str
    admin_phone: str
    sites: List[QuickSetupSite]
    plan: str = "pilot"


class UpdateConfigRequest(BaseModel):
    config: Dict[str, Any]


# =============================================================================
# ONBOARDING ENDPOINTS
# =============================================================================

@router.post("/onboarding/start")
async def start_onboarding(request: StartOnboardingRequest):
    """
    Start a new onboarding session
    
    This is the first step in setting up a new customer.
    Returns a session_id to use in subsequent calls.
    """
    try:
        session = onboarding_service.start_onboarding(
            customer_name=request.customer_name,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            plan=request.plan,
        )
        return {"success": True, "data": session}
    except Exception as e:
        logger.error(f"Failed to start onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/onboarding/{session_id}")
async def get_onboarding_status(session_id: str):
    """Get current onboarding session status"""
    session = onboarding_service.get_onboarding_status(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "data": session}


@router.post("/onboarding/organization")
async def create_organization(request: CreateOrganizationRequest):
    """Create organization for onboarding session"""
    try:
        org = onboarding_service.create_organization(
            session_id=request.session_id,
            name=request.name,
            slug=request.slug,
            billing_email=request.billing_email,
            settings=request.settings,
        )
        return {"success": True, "data": org}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create organization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/onboarding/admin-user")
async def create_admin_user(request: CreateAdminUserRequest):
    """Create admin/owner user for organization"""
    try:
        user = onboarding_service.create_admin_user(
            session_id=request.session_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
        )
        return {"success": True, "data": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/onboarding/project")
async def create_project(request: CreateProjectRequest):
    """Create a project/site"""
    try:
        project = onboarding_service.create_project(
            session_id=request.session_id,
            name=request.name,
            code=request.code,
            address=request.address,
            city=request.city,
            project_type=request.project_type,
            settings=request.settings,
        )
        return {"success": True, "data": project}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/onboarding/team-members")
async def add_team_members(request: AddTeamMembersRequest):
    """Add team members to a project"""
    try:
        members = [m.dict() for m in request.members]
        results = onboarding_service.add_team_members_bulk(
            session_id=request.session_id,
            project_id=request.project_id,
            members=members,
        )
        return {"success": True, "data": {"members_added": len(results), "members": results}}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to add team members: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/onboarding/{session_id}/complete-projects")
async def complete_projects_step(session_id: str):
    """Mark projects step as complete"""
    onboarding_service.complete_projects_step(session_id)
    return {"success": True, "message": "Projects step completed"}


@router.post("/onboarding/{session_id}/complete-team")
async def complete_team_step(session_id: str):
    """Mark team members step as complete"""
    onboarding_service.complete_team_step(session_id)
    return {"success": True, "message": "Team step completed"}


@router.post("/onboarding/{session_id}/drawings-uploaded")
async def mark_drawings_uploaded(session_id: str, count: int):
    """Mark drawings as uploaded"""
    onboarding_service.mark_drawings_uploaded(session_id, count)
    return {"success": True, "message": f"{count} drawings marked as uploaded"}


@router.get("/onboarding/{session_id}/welcome-messages")
async def get_welcome_messages(session_id: str):
    """Generate welcome messages for team members"""
    messages = onboarding_service.generate_welcome_messages(session_id)
    return {"success": True, "data": {"messages": messages, "count": len(messages)}}


@router.post("/onboarding/{session_id}/complete")
async def complete_onboarding(session_id: str):
    """Complete the onboarding process"""
    try:
        summary = onboarding_service.complete_onboarding(session_id)
        return {"success": True, "data": summary}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# QUICK SETUP (All-in-one)
# =============================================================================

@router.post("/quick-setup")
async def quick_setup(request: QuickSetupRequest):
    """
    One-call setup for simple onboarding
    
    Creates organization, admin user, projects, and team members in one call.
    
    Example:
    ```json
    {
        "company_name": "ABC Builders",
        "admin_name": "Rajesh Sharma",
        "admin_email": "rajesh@abc.com",
        "admin_phone": "+919876543210",
        "sites": [{
            "name": "Skyline Towers",
            "address": "Sector 62, Noida",
            "city": "Noida",
            "team": [
                {"name": "Ramesh", "phone": "+919876543211", "role": "site_engineer"},
                {"name": "Priya", "phone": "+919876543212", "role": "pm"}
            ]
        }],
        "plan": "pilot"
    }
    ```
    """
    try:
        sites_data = []
        for site in request.sites:
            site_dict = {
                "name": site.name,
                "address": site.address,
                "city": site.city,
            }
            if site.team:
                site_dict["team"] = [m.dict() for m in site.team]
            sites_data.append(site_dict)
        
        summary = onboarding_service.quick_setup(
            company_name=request.company_name,
            admin_name=request.admin_name,
            admin_email=request.admin_email,
            admin_phone=request.admin_phone,
            sites=sites_data,
            plan=request.plan,
        )
        return {"success": True, "data": summary}
    except Exception as e:
        logger.error(f"Quick setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CONFIGURATION ENDPOINTS
# =============================================================================

@router.get("/organizations/{org_id}/config")
async def get_organization_config(org_id: str):
    """Get organization configuration"""
    config = config_service.get_organization_config(org_id)
    return {"success": True, "data": config}


@router.put("/organizations/{org_id}/config")
async def update_organization_config(org_id: str, request: UpdateConfigRequest):
    """Update organization configuration"""
    config = config_service.set_organization_config(org_id, request.config)
    return {"success": True, "data": config}


@router.get("/projects/{project_id}/config")
async def get_project_config(project_id: str):
    """Get project configuration"""
    config = config_service.get_project_config(project_id)
    return {"success": True, "data": config}


@router.put("/projects/{project_id}/config")
async def update_project_config(project_id: str, request: UpdateConfigRequest):
    """Update project configuration"""
    config = config_service.set_project_config(project_id, request.config)
    return {"success": True, "data": config}


@router.get("/users/{user_id}/config")
async def get_user_config(user_id: str, role: str = "site_engineer"):
    """Get user configuration"""
    config = config_service.get_user_config(user_id, role)
    return {"success": True, "data": config}


@router.put("/users/{user_id}/config")
async def update_user_config(user_id: str, request: UpdateConfigRequest):
    """Update user configuration"""
    config = config_service.set_user_config(user_id, request.config)
    return {"success": True, "data": config}


# =============================================================================
# FEATURE FLAGS
# =============================================================================

@router.get("/organizations/{org_id}/features")
async def get_enabled_features(org_id: str):
    """Get list of enabled features for an organization"""
    features = config_service.get_enabled_features(org_id)
    return {"success": True, "data": {"features": features}}


@router.post("/organizations/{org_id}/features/{feature}/enable")
async def enable_feature(org_id: str, feature: str):
    """Enable a feature for an organization"""
    config_service.set_organization_config(org_id, {
        "features": {feature: True}
    })
    return {"success": True, "message": f"Feature '{feature}' enabled"}


@router.post("/organizations/{org_id}/features/{feature}/disable")
async def disable_feature(org_id: str, feature: str):
    """Disable a feature for an organization"""
    config_service.set_organization_config(org_id, {
        "features": {feature: False}
    })
    return {"success": True, "message": f"Feature '{feature}' disabled"}


# =============================================================================
# PERMISSIONS
# =============================================================================

@router.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: str, role: str = "site_engineer"):
    """Get user permissions"""
    permissions = config_service.get_user_permissions(user_id, role)
    return {"success": True, "data": {"permissions": permissions}}


@router.post("/users/{user_id}/permissions")
async def update_user_permissions(user_id: str, permissions: Dict[str, bool]):
    """Update specific user permissions"""
    config_service.set_user_config(user_id, {"permissions": permissions})
    return {"success": True, "message": "Permissions updated"}
