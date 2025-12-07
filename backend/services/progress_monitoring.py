"""
SiteMind Progress Monitoring Service
AI-based progress tracking and delay prediction

FEATURES:
- Activity tracking
- Progress calculation
- Delay prediction
- Milestone management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class Milestone:
    id: str
    name: str
    planned_date: str
    actual_date: Optional[str]
    status: str  # pending, completed, delayed


@dataclass
class ProjectProgress:
    overall_percent: float
    phase: str
    on_schedule: bool
    days_ahead_behind: int
    milestones_completed: int
    milestones_total: int


class ProgressMonitoringService:
    """
    Monitor project progress
    """
    
    def __init__(self):
        self._milestones: Dict[str, List[Milestone]] = {}  # project_id -> milestones
        self._activities: Dict[str, List[Dict]] = {}  # project_id -> daily activities
        self._progress: Dict[str, ProjectProgress] = {}
    
    # =========================================================================
    # MILESTONE MANAGEMENT
    # =========================================================================
    
    def add_milestone(
        self,
        project_id: str,
        name: str,
        planned_date: str,
    ) -> Milestone:
        """Add a milestone"""
        milestone = Milestone(
            id=f"ms_{datetime.utcnow().timestamp():.0f}",
            name=name,
            planned_date=planned_date,
            actual_date=None,
            status="pending",
        )
        
        if project_id not in self._milestones:
            self._milestones[project_id] = []
        self._milestones[project_id].append(milestone)
        
        return milestone
    
    def complete_milestone(
        self,
        project_id: str,
        milestone_id: str,
    ) -> Optional[Milestone]:
        """Mark milestone complete"""
        milestones = self._milestones.get(project_id, [])
        
        for ms in milestones:
            if ms.id == milestone_id:
                ms.actual_date = datetime.utcnow().isoformat()
                
                # Check if delayed
                if ms.actual_date > ms.planned_date:
                    ms.status = "delayed"
                else:
                    ms.status = "completed"
                
                return ms
        
        return None
    
    def get_upcoming_milestones(
        self,
        project_id: str,
        days: int = 14,
    ) -> List[Milestone]:
        """Get upcoming milestones"""
        milestones = self._milestones.get(project_id, [])
        cutoff = (datetime.utcnow() + timedelta(days=days)).isoformat()
        
        upcoming = [
            ms for ms in milestones 
            if ms.status == "pending" and ms.planned_date <= cutoff
        ]
        
        return sorted(upcoming, key=lambda x: x.planned_date)
    
    # =========================================================================
    # ACTIVITY TRACKING
    # =========================================================================
    
    def record_activity(
        self,
        project_id: str,
        activity_type: str,
        location: str,
        description: str,
        user_phone: str,
    ):
        """Record daily activity"""
        if project_id not in self._activities:
            self._activities[project_id] = []
        
        self._activities[project_id].append({
            "type": activity_type,
            "location": location,
            "description": description,
            "user": user_phone,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    # =========================================================================
    # PROGRESS CALCULATION
    # =========================================================================
    
    def calculate_progress(self, project_id: str) -> ProjectProgress:
        """Calculate overall project progress"""
        milestones = self._milestones.get(project_id, [])
        
        if not milestones:
            return ProjectProgress(
                overall_percent=0,
                phase="Unknown",
                on_schedule=True,
                days_ahead_behind=0,
                milestones_completed=0,
                milestones_total=0,
            )
        
        completed = [ms for ms in milestones if ms.status in ["completed", "delayed"]]
        pending = [ms for ms in milestones if ms.status == "pending"]
        
        overall = (len(completed) / len(milestones)) * 100 if milestones else 0
        
        # Determine current phase
        if overall < 20:
            phase = "Foundation"
        elif overall < 50:
            phase = "Structure"
        elif overall < 80:
            phase = "Finishing"
        else:
            phase = "Final"
        
        # Check schedule
        delayed_count = len([ms for ms in completed if ms.status == "delayed"])
        on_schedule = delayed_count == 0
        
        return ProjectProgress(
            overall_percent=round(overall, 1),
            phase=phase,
            on_schedule=on_schedule,
            days_ahead_behind=0,  # Would calculate from actual vs planned
            milestones_completed=len(completed),
            milestones_total=len(milestones),
        )
    
    def predict_delay(self, project_id: str) -> Optional[Dict]:
        """Predict potential delays based on activity patterns"""
        activities = self._activities.get(project_id, [])
        
        if len(activities) < 7:
            return None  # Not enough data
        
        # Simple heuristic: check if activity dropped
        last_week = [a for a in activities if a["timestamp"] > (datetime.utcnow() - timedelta(days=7)).isoformat()]
        week_before = [a for a in activities if 
            (datetime.utcnow() - timedelta(days=14)).isoformat() < a["timestamp"] <= 
            (datetime.utcnow() - timedelta(days=7)).isoformat()]
        
        if week_before and len(last_week) < len(week_before) * 0.5:
            return {
                "warning": True,
                "message": "Activity dropped 50%+ compared to previous week",
                "recommendation": "Check for blockers or resource issues",
            }
        
        return None
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def generate_progress_report(self, project_id: str) -> str:
        """Generate progress report for WhatsApp"""
        progress = self.calculate_progress(project_id)
        milestones = self._milestones.get(project_id, [])
        upcoming = self.get_upcoming_milestones(project_id, 14)
        
        # Progress bar
        filled = int(progress.overall_percent / 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        report = f"""**Project Progress Report**

**Overall:** {bar} {progress.overall_percent}%
**Phase:** {progress.phase}
**Schedule:** {"✅ On Track" if progress.on_schedule else "⚠️ Delayed"}

**Milestones:** {progress.milestones_completed}/{progress.milestones_total} completed

"""

        if upcoming:
            report += "**Upcoming:**\n"
            for ms in upcoming[:3]:
                days = (datetime.fromisoformat(ms.planned_date) - datetime.utcnow()).days
                report += f"• {ms.name} ({days} days)\n"
        
        delay = self.predict_delay(project_id)
        if delay:
            report += f"\n⚠️ **Alert:** {delay['message']}"
        
        return report


# Singleton instance
progress_monitoring = ProgressMonitoringService()
