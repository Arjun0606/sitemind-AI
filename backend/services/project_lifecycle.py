"""
SiteMind Project Lifecycle Service
Handles the full lifecycle of a construction project

LIFECYCLE:
1. ONBOARDING → Upload blueprints, add engineers
2. ACTIVE → Daily/weekly updates, queries, changes
3. COMPLETED → Construction finished
4. ARCHIVED → Legal retention, read-only access

Projects are constantly updated:
- Daily: Queries, verifications, small decisions
- Weekly: Blueprint revisions, change orders, RFIs
- Monthly: Reports, ROI tracking
- At completion: Transition to archive
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from utils.logger import logger


class ProjectPhase(str, Enum):
    """Construction project phases"""
    ONBOARDING = "onboarding"       # Initial setup
    FOUNDATION = "foundation"        # Foundation work
    STRUCTURE = "structure"          # Structural work
    FINISHING = "finishing"          # MEP, finishing
    HANDOVER = "handover"           # Final handover
    COMPLETED = "completed"         # Construction done
    ARCHIVED = "archived"           # Legal retention


class UpdateType(str, Enum):
    """Types of project updates"""
    BLUEPRINT_REVISION = "blueprint_revision"
    CHANGE_ORDER = "change_order"
    RFI = "rfi"
    DECISION = "decision"
    REWORK = "rework"
    MILESTONE = "milestone"
    DAILY_LOG = "daily_log"
    WEEKLY_REPORT = "weekly_report"


class ProjectLifecycleService:
    """
    Manages the lifecycle of construction projects
    
    Key functions:
    - Track project phases
    - Handle daily/weekly updates
    - Manage blueprint revisions
    - Transition to archive when complete
    """
    
    def __init__(self):
        # In-memory tracking (would be in DB in production)
        self._projects: Dict[str, Dict] = {}
        self._updates: Dict[str, List[Dict]] = {}
    
    def register_project(
        self,
        project_id: str,
        project_name: str,
        builder_id: str,
        location: str,
        expected_duration_months: int = 24,
        start_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new project for SiteMind
        """
        now = datetime.utcnow()
        start = datetime.fromisoformat(start_date) if start_date else now
        expected_end = start + timedelta(days=expected_duration_months * 30)
        
        project = {
            "project_id": project_id,
            "project_name": project_name,
            "builder_id": builder_id,
            "location": location,
            "phase": ProjectPhase.ONBOARDING,
            "status": "active",
            "start_date": start.isoformat(),
            "expected_end_date": expected_end.isoformat(),
            "actual_end_date": None,
            "created_at": now.isoformat(),
            "last_activity": now.isoformat(),
            "stats": {
                "total_queries": 0,
                "total_updates": 0,
                "blueprint_revisions": 0,
                "change_orders": 0,
                "rfis": 0,
                "reworks": 0,
            },
        }
        
        self._projects[project_id] = project
        self._updates[project_id] = []
        
        logger.info(f"📋 Project registered: {project_name} ({project_id})")
        
        return {
            "success": True,
            "project": project,
            "next_steps": [
                "Upload blueprints via dashboard",
                "Add site engineers (WhatsApp numbers)",
                "Configure project settings",
                "Start using SiteMind!",
            ],
        }
    
    def record_update(
        self,
        project_id: str,
        update_type: UpdateType,
        description: str,
        details: Dict[str, Any],
        recorded_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a project update (daily/weekly)
        
        This is called automatically when:
        - Blueprint revision uploaded
        - Change order recorded
        - RFI answered
        - Decision made
        - Rework logged
        """
        if project_id not in self._projects:
            return {"success": False, "error": "Project not found"}
        
        now = datetime.utcnow()
        
        update = {
            "update_id": f"upd_{int(now.timestamp() * 1000)}",
            "type": update_type.value,
            "description": description,
            "details": details,
            "recorded_by": recorded_by,
            "timestamp": now.isoformat(),
        }
        
        self._updates[project_id].append(update)
        
        # Update project stats
        project = self._projects[project_id]
        project["last_activity"] = now.isoformat()
        project["stats"]["total_updates"] += 1
        
        # Update specific counters
        if update_type == UpdateType.BLUEPRINT_REVISION:
            project["stats"]["blueprint_revisions"] += 1
        elif update_type == UpdateType.CHANGE_ORDER:
            project["stats"]["change_orders"] += 1
        elif update_type == UpdateType.RFI:
            project["stats"]["rfis"] += 1
        elif update_type == UpdateType.REWORK:
            project["stats"]["reworks"] += 1
        
        logger.info(f"📝 Update recorded: {update_type.value} for {project_id}")
        
        return {
            "success": True,
            "update": update,
            "project_stats": project["stats"],
        }
    
    def update_phase(
        self,
        project_id: str,
        new_phase: ProjectPhase,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update project phase (e.g., Foundation → Structure)
        """
        if project_id not in self._projects:
            return {"success": False, "error": "Project not found"}
        
        project = self._projects[project_id]
        old_phase = project["phase"]
        project["phase"] = new_phase
        
        # Record as milestone
        self.record_update(
            project_id=project_id,
            update_type=UpdateType.MILESTONE,
            description=f"Phase changed: {old_phase} → {new_phase}",
            details={"old_phase": old_phase, "new_phase": new_phase, "notes": notes},
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "old_phase": old_phase,
            "new_phase": new_phase,
        }
    
    def complete_project(
        self,
        project_id: str,
        completion_notes: Optional[str] = None,
        handover_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Mark project as completed
        
        This triggers:
        1. Final report generation
        2. Archive pricing offer
        3. Data export option
        """
        if project_id not in self._projects:
            return {"success": False, "error": "Project not found"}
        
        now = datetime.utcnow()
        project = self._projects[project_id]
        
        project["phase"] = ProjectPhase.COMPLETED
        project["status"] = "completed"
        project["actual_end_date"] = handover_date or now.isoformat()
        
        # Calculate project duration
        start = datetime.fromisoformat(project["start_date"])
        end = datetime.fromisoformat(project["actual_end_date"])
        duration_days = (end - start).days
        
        # Get final stats
        stats = project["stats"]
        
        return {
            "success": True,
            "project_id": project_id,
            "project_name": project["project_name"],
            "status": "completed",
            "completion_date": project["actual_end_date"],
            "project_duration": f"{duration_days} days ({duration_days // 30} months)",
            "final_stats": {
                "total_queries": stats["total_queries"],
                "total_updates": stats["total_updates"],
                "blueprint_revisions": stats["blueprint_revisions"],
                "change_orders": stats["change_orders"],
                "rfis": stats["rfis"],
                "reworks": stats["reworks"],
            },
            "archive_offer": {
                "message": "🎉 Project Completed! Keep your data for legal protection.",
                "monthly_price": "$50/month",
                "onetime_price": "$2,000 (5 years)",
                "whats_preserved": [
                    "All decisions with citations",
                    "Complete audit trail",
                    "All change orders & RFIs",
                    "WhatsApp history",
                    "All blueprints & revisions",
                ],
                "why_archive": [
                    "Legal disputes happen 5-10 years later",
                    "All approvals documented",
                    "Reference for future projects",
                ],
            },
            "next_steps": [
                "Download full project export",
                "Choose archive plan (optional)",
                "Leave review (help us improve!)",
            ],
        }
    
    def archive_project(
        self,
        project_id: str,
        archive_plan: str = "monthly",  # "monthly" or "5year"
    ) -> Dict[str, Any]:
        """
        Move completed project to archive tier
        """
        if project_id not in self._projects:
            return {"success": False, "error": "Project not found"}
        
        project = self._projects[project_id]
        
        if project["phase"] != ProjectPhase.COMPLETED:
            return {
                "success": False,
                "error": "Project must be completed before archiving",
            }
        
        project["phase"] = ProjectPhase.ARCHIVED
        project["status"] = "archived"
        project["archive_started"] = datetime.utcnow().isoformat()
        project["archive_plan"] = archive_plan
        
        pricing = {
            "monthly": {"price": "$50/month", "inr": "₹4,150/month"},
            "5year": {"price": "$2,000 one-time", "inr": "₹1,66,000 one-time"},
        }[archive_plan]
        
        return {
            "success": True,
            "project_id": project_id,
            "project_name": project["project_name"],
            "status": "archived",
            "archive_plan": archive_plan,
            "pricing": pricing,
            "access": "Read-only via dashboard",
            "preserved_data": [
                f"📊 {project['stats']['total_queries']} queries",
                f"🔄 {project['stats']['change_orders']} change orders",
                f"❓ {project['stats']['rfis']} RFIs",
                f"📐 {project['stats']['blueprint_revisions']} blueprint revisions",
                "📜 Complete audit trail",
                "💬 All WhatsApp conversations",
            ],
            "message": f"""
✅ Project Archived: {project['project_name']}

Your project data is now in archive mode.
• Access: Read-only via dashboard
• All data preserved with citations
• Export available anytime

Archive Plan: {archive_plan}
Price: {pricing['price']} ({pricing['inr']})

This data can protect you in legal disputes
for years to come. All decisions, approvals,
and changes are fully documented.
            """,
        }
    
    def get_project_timeline(
        self,
        project_id: str,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Get project update timeline
        
        Useful for:
        - Dashboard display
        - Audit trail review
        - Legal documentation
        """
        if project_id not in self._projects:
            return {"success": False, "error": "Project not found"}
        
        project = self._projects[project_id]
        updates = self._updates.get(project_id, [])[-limit:]
        updates.reverse()  # Most recent first
        
        return {
            "project_id": project_id,
            "project_name": project["project_name"],
            "current_phase": project["phase"],
            "status": project["status"],
            "timeline": updates,
            "stats": project["stats"],
        }
    
    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Get complete project summary"""
        if project_id not in self._projects:
            return {"success": False, "error": "Project not found"}
        
        project = self._projects[project_id]
        updates = self._updates.get(project_id, [])
        
        # Calculate activity stats
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        updates_this_week = [
            u for u in updates 
            if datetime.fromisoformat(u["timestamp"]) > week_ago
        ]
        updates_this_month = [
            u for u in updates 
            if datetime.fromisoformat(u["timestamp"]) > month_ago
        ]
        
        return {
            "project": project,
            "activity": {
                "total_updates": len(updates),
                "updates_this_week": len(updates_this_week),
                "updates_this_month": len(updates_this_month),
                "last_activity": project["last_activity"],
            },
            "stats": project["stats"],
        }


# Singleton instance
project_lifecycle = ProjectLifecycleService()

