"""
SiteMind Dashboard API
======================

Endpoints for the management dashboard:
- Company overview
- Project stats
- Member management
- Usage tracking
- Reports
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from services import (
    memory_engine,
    awareness_engine,
    intelligence_engine,
    billing_service,
    pricing_service,
)
from database import db
from utils.logger import logger

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# =============================================================================
# COMPANY OVERVIEW
# =============================================================================

@router.get("/company/{company_id}")
async def get_company_overview(company_id: str) -> Dict[str, Any]:
    """Get company-wide overview"""
    
    company = await db.get_company(company_id)
    projects = await db.get_company_projects(company_id)
    users = await db.get_company_users(company_id)
    
    # Aggregate stats across all projects
    total_stats = {
        "total_rfis": 0,
        "open_rfis": 0,
        "total_decisions": 0,
        "total_issues": 0,
        "open_issues": 0,
        "total_drawings": 0,
    }
    
    project_summaries = []
    
    for project in projects:
        project_id = project["id"]
        
        stats = memory_engine.get_stats(company_id, project_id)
        awareness_stats = awareness_engine.get_stats(company_id, project_id)
        
        # Aggregate
        total_stats["total_rfis"] += stats.get("total_rfis", 0)
        total_stats["open_rfis"] += stats.get("open_rfis", 0)
        total_stats["total_decisions"] += stats.get("total_decisions", 0)
        total_stats["total_drawings"] += stats.get("total_drawings", 0)
        total_stats["total_issues"] += awareness_stats.get("total_issues", 0)
        total_stats["open_issues"] += awareness_stats.get("open_issues", 0)
        
        project_summaries.append({
            "id": project_id,
            "name": project["name"],
            "location": project.get("location"),
            "stage": project.get("stage", "active"),
            "rfis": stats.get("open_rfis", 0),
            "issues": awareness_stats.get("open_issues", 0),
            "decisions": stats.get("total_decisions", 0),
        })
    
    return {
        "company": {
            "id": company_id,
            "name": company["name"] if company else "Unknown",
            "is_pilot": company.get("is_pilot", False) if company else False,
        },
        "stats": total_stats,
        "projects": project_summaries,
        "members": len(users),
        "active_users": len([u for u in users if u.get("last_active_at")]),
    }


# =============================================================================
# PROJECT DETAILS
# =============================================================================

@router.get("/project/{company_id}/{project_id}")
async def get_project_details(company_id: str, project_id: str) -> Dict[str, Any]:
    """Get detailed project stats"""
    
    project = await db.get_project(project_id)
    
    stats = memory_engine.get_stats(company_id, project_id)
    awareness_stats = awareness_engine.get_stats(company_id, project_id)
    
    # Get RFIs
    open_rfis = memory_engine.get_open_rfis(company_id, project_id)
    overdue_rfis = memory_engine.get_overdue_rfis(company_id, project_id)
    
    # Get issues
    open_issues = awareness_engine.get_open_issues(company_id, project_id)
    
    # Get decisions
    decisions = memory_engine.get_decisions(company_id, project_id, limit=10)
    
    return {
        "project": {
            "id": project_id,
            "name": project["name"] if project else "Unknown",
            "location": project.get("location") if project else None,
            "stage": project.get("stage", "active") if project else "active",
        },
        "stats": {
            **stats,
            **awareness_stats,
            "overdue_rfis": len(overdue_rfis),
        },
        "rfis": [
            {
                "id": rfi.id,
                "title": rfi.title,
                "raised_by": rfi.raised_by,
                "assigned_to": rfi.assigned_to,
                "status": rfi.status,
                "raised_at": rfi.raised_at.isoformat(),
                "is_overdue": rfi.id in [o.id for o in overdue_rfis],
            }
            for rfi in open_rfis[:10]
        ],
        "issues": [
            {
                "id": issue.id,
                "description": issue.description[:100],
                "severity": issue.severity,
                "location": issue.location,
                "reported_at": issue.reported_at.isoformat(),
            }
            for issue in open_issues[:10]
        ],
        "decisions": [
            {
                "id": d.id,
                "description": d.description[:100],
                "approved_by": d.approved_by,
                "approved_at": d.approved_at.isoformat(),
            }
            for d in decisions
        ],
    }


# =============================================================================
# USAGE & BILLING
# =============================================================================

@router.get("/usage/{company_id}")
async def get_usage(company_id: str) -> Dict[str, Any]:
    """Get usage stats for billing"""
    
    billing_cycle = datetime.utcnow().strftime("%Y-%m")
    
    # Get usage from billing service
    usage = billing_service.get_usage(company_id)
    
    # Get pricing info
    pricing = {
        "flat_fee": pricing_service.FLAT_FEE_USD,
        "included": pricing_service.INCLUDED,
        "prices": pricing_service.USAGE_PRICES,
    }
    
    # Calculate current bill
    invoice = pricing_service.calculate_invoice(
        queries=usage.get("queries", 0),
        documents=usage.get("documents", 0),
        photos=usage.get("photos", 0),
        storage_gb=usage.get("storage_gb", 0),
        whatsapp_messages=usage.get("whatsapp_messages", 0),
    )
    
    return {
        "billing_cycle": billing_cycle,
        "usage": usage,
        "pricing": pricing,
        "invoice": invoice,
    }


@router.get("/usage/{company_id}/history")
async def get_usage_history(company_id: str) -> List[Dict[str, Any]]:
    """Get usage history"""
    
    # Get from database
    # In production, this would query the usage table
    return []


# =============================================================================
# MEMBERS
# =============================================================================

@router.get("/members/{company_id}")
async def get_members(company_id: str) -> Dict[str, Any]:
    """Get all members"""
    
    users = await db.get_company_users(company_id)
    
    return {
        "total": len(users),
        "members": [
            {
                "id": u.get("id"),
                "name": u.get("name"),
                "phone": u.get("phone"),
                "role": u.get("role", "site_engineer"),
                "email": u.get("email"),
                "last_active": u.get("last_active_at"),
            }
            for u in users
        ],
    }


@router.post("/members/{company_id}")
async def add_member(company_id: str, member: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new member"""
    
    user = await db.create_user(
        company_id=company_id,
        name=member.get("name"),
        phone=member.get("phone"),
        role=member.get("role", "site_engineer"),
        email=member.get("email"),
    )
    
    if user:
        return {"success": True, "user": user}
    return {"success": False, "error": "Failed to create user"}


@router.delete("/members/{company_id}/{user_id}")
async def remove_member(company_id: str, user_id: str) -> Dict[str, Any]:
    """Remove a member"""
    
    success = await db.delete("users", {"id": user_id, "company_id": company_id})
    return {"success": success}


# =============================================================================
# REPORTS
# =============================================================================

@router.get("/reports/{company_id}/{project_id}/weekly")
async def get_weekly_report(company_id: str, project_id: str) -> Dict[str, Any]:
    """Generate weekly report"""
    
    report = await intelligence_engine.generate_health_report(
        company_id=company_id,
        project_id=project_id,
        period="weekly",
    )
    
    return {
        "report": report,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/reports/{company_id}/{project_id}/risks")
async def get_risk_report(company_id: str, project_id: str) -> Dict[str, Any]:
    """Get risk analysis"""
    
    risks = await intelligence_engine.monitor_risks(company_id, project_id)
    delays = await intelligence_engine.predict_delays(company_id, project_id)
    
    return {
        "risks": [
            {
                "id": r.id,
                "description": r.description,
                "category": r.category,
                "severity": r.severity,
                "affected_work": r.affected_work,
                "mitigation": r.mitigation,
            }
            for r in risks
        ],
        "delay_predictions": delays,
    }


@router.get("/reports/{company_id}/{project_id}/contractors")
async def get_contractor_report(company_id: str, project_id: str) -> Dict[str, Any]:
    """Get contractor performance"""
    
    rankings = await intelligence_engine.get_contractor_rankings(company_id, project_id)
    
    return {
        "contractors": rankings,
    }


# =============================================================================
# SEARCH
# =============================================================================

@router.get("/search/{company_id}/{project_id}")
async def search(company_id: str, project_id: str, q: str) -> Dict[str, Any]:
    """Search project data"""
    
    result = await memory_engine.search(q, company_id, project_id)
    
    return {
        "query": q,
        "answer": result.get("answer"),
        "results": result.get("results", [])[:10],
        "count": result.get("count", 0),
    }


# =============================================================================
# HEALTH
# =============================================================================

@router.get("/health")
async def health():
    return {"status": "ok", "service": "dashboard-api"}
