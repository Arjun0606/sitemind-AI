"""
SiteMind AI Progress Monitoring Service
AI-powered construction progress tracking using photos and data

FEATURES:
1. Photo-Based Progress - Compare site photos to expected state
2. Milestone Tracking - Automatic milestone detection
3. Delay Prediction - AI identifies potential delays early
4. Quality Monitoring - Detect quality issues from photos
5. Timeline Analytics - Actual vs planned progress
6. Predictive Insights - When will this floor be complete?

HOW IT WORKS:
- Engineers upload daily progress photos via WhatsApp
- AI compares to drawings and expected progress
- System tracks % complete per area
- Management sees real-time progress dashboard
- AI flags delays before they become critical
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from utils.logger import logger


class MilestoneStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    VERIFIED = "verified"


class WorkStage(str, Enum):
    # Foundation stages
    EXCAVATION = "excavation"
    PCC = "pcc"
    FOOTING = "footing"
    PLINTH = "plinth"
    
    # Structural stages
    COLUMN_REBAR = "column_rebar"
    COLUMN_SHUTTERING = "column_shuttering"
    COLUMN_POUR = "column_pour"
    BEAM_REBAR = "beam_rebar"
    BEAM_SHUTTERING = "beam_shuttering"
    SLAB_REBAR = "slab_rebar"
    SLAB_POUR = "slab_pour"
    DESHUTTERING = "deshuttering"
    CURING = "curing"
    
    # Finishing stages
    BRICKWORK = "brickwork"
    PLASTERING = "plastering"
    FLOORING = "flooring"
    PAINTING = "painting"
    
    # MEP
    ELECTRICAL_CONDUIT = "electrical_conduit"
    PLUMBING_ROUGH = "plumbing_rough"
    HVAC_DUCT = "hvac_duct"


@dataclass
class Milestone:
    """A construction milestone"""
    milestone_id: str
    project_id: str
    name: str
    location: str  # e.g., "Floor 3" or "Block A"
    stage: WorkStage
    planned_start: str
    planned_end: str
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    status: MilestoneStatus = MilestoneStatus.PLANNED
    progress_percent: int = 0
    photos: List[Dict] = field(default_factory=list)  # [{url, date, notes}]
    issues: List[str] = field(default_factory=list)
    verified_by: Optional[str] = None


@dataclass
class ProgressUpdate:
    """A progress update entry"""
    update_id: str
    project_id: str
    location: str
    stage: WorkStage
    progress_percent: int
    notes: str
    photo_url: Optional[str]
    updated_by: str
    updated_at: str
    ai_analysis: Optional[str] = None


class ProgressMonitoringService:
    """
    AI-powered construction progress monitoring
    """
    
    def __init__(self):
        self._milestones: Dict[str, List[Milestone]] = {}
        self._progress_updates: Dict[str, List[ProgressUpdate]] = {}
        self._area_progress: Dict[str, Dict[str, int]] = {}  # project -> {location: percent}
    
    # =========================================================================
    # MILESTONE MANAGEMENT
    # =========================================================================
    
    def create_milestone(
        self,
        project_id: str,
        name: str,
        location: str,
        stage: WorkStage,
        planned_start: str,
        planned_end: str,
    ) -> Milestone:
        """Create a milestone"""
        milestone = Milestone(
            milestone_id=f"ms_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            name=name,
            location=location,
            stage=stage,
            planned_start=planned_start,
            planned_end=planned_end,
        )
        
        if project_id not in self._milestones:
            self._milestones[project_id] = []
        
        self._milestones[project_id].append(milestone)
        
        return milestone
    
    def update_milestone_progress(
        self,
        milestone_id: str,
        progress_percent: int,
        notes: str = None,
        photo_url: str = None,
    ) -> bool:
        """Update milestone progress"""
        milestone = self._find_milestone(milestone_id)
        if milestone:
            milestone.progress_percent = progress_percent
            
            if photo_url:
                milestone.photos.append({
                    "url": photo_url,
                    "date": datetime.utcnow().isoformat(),
                    "notes": notes,
                })
            
            # Auto-update status
            if progress_percent == 0:
                milestone.status = MilestoneStatus.PLANNED
            elif progress_percent < 100:
                milestone.status = MilestoneStatus.IN_PROGRESS
                if not milestone.actual_start:
                    milestone.actual_start = datetime.utcnow().isoformat()
            else:
                milestone.status = MilestoneStatus.COMPLETED
                milestone.actual_end = datetime.utcnow().isoformat()
            
            # Check for delay
            if milestone.status == MilestoneStatus.IN_PROGRESS:
                planned_end = datetime.fromisoformat(milestone.planned_end).date()
                if datetime.utcnow().date() > planned_end:
                    milestone.status = MilestoneStatus.DELAYED
            
            return True
        return False
    
    def _find_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Find milestone by ID"""
        for project_milestones in self._milestones.values():
            for ms in project_milestones:
                if ms.milestone_id == milestone_id:
                    return ms
        return None
    
    # =========================================================================
    # PROGRESS UPDATES (Via WhatsApp)
    # =========================================================================
    
    def record_progress(
        self,
        project_id: str,
        location: str,
        stage: WorkStage,
        progress_percent: int,
        notes: str,
        updated_by: str,
        photo_url: str = None,
        ai_analysis: str = None,
    ) -> ProgressUpdate:
        """
        Record a progress update
        
        Called when engineer sends progress update via WhatsApp
        """
        update = ProgressUpdate(
            update_id=f"prog_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            location=location,
            stage=stage,
            progress_percent=progress_percent,
            notes=notes,
            photo_url=photo_url,
            updated_by=updated_by,
            updated_at=datetime.utcnow().isoformat(),
            ai_analysis=ai_analysis,
        )
        
        if project_id not in self._progress_updates:
            self._progress_updates[project_id] = []
        
        self._progress_updates[project_id].append(update)
        
        # Update area progress
        if project_id not in self._area_progress:
            self._area_progress[project_id] = {}
        
        self._area_progress[project_id][location] = progress_percent
        
        logger.info(f"📊 Progress recorded: {location} - {stage.value}: {progress_percent}%")
        
        return update
    
    def analyze_progress_photo(
        self,
        project_id: str,
        location: str,
        expected_stage: WorkStage,
        photo_url: str,
    ) -> Dict[str, Any]:
        """
        AI analysis of progress photo
        
        Would use Gemini to:
        - Verify work matches expected stage
        - Estimate completion percentage
        - Detect quality issues
        - Compare to previous photos
        """
        # This would call Gemini for actual analysis
        # Returning mock structure for now
        return {
            "location": location,
            "expected_stage": expected_stage.value,
            "detected_stage": expected_stage.value,  # Would be AI-detected
            "estimated_progress": 75,  # Would be AI-estimated
            "quality_issues": [],
            "recommendations": [],
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }
    
    # =========================================================================
    # DELAY DETECTION & PREDICTION
    # =========================================================================
    
    def detect_delays(self, project_id: str) -> List[Dict]:
        """Detect current and predicted delays"""
        milestones = self._milestones.get(project_id, [])
        delays = []
        
        today = datetime.utcnow().date()
        
        for ms in milestones:
            if ms.status in [MilestoneStatus.COMPLETED, MilestoneStatus.VERIFIED]:
                continue
            
            planned_end = datetime.fromisoformat(ms.planned_end).date()
            
            # Current delay
            if today > planned_end and ms.status != MilestoneStatus.COMPLETED:
                delay_days = (today - planned_end).days
                delays.append({
                    "milestone": ms.name,
                    "location": ms.location,
                    "type": "current_delay",
                    "delay_days": delay_days,
                    "planned_end": ms.planned_end,
                    "progress": ms.progress_percent,
                })
            
            # Predicted delay (based on current progress rate)
            elif ms.status == MilestoneStatus.IN_PROGRESS and ms.actual_start:
                days_elapsed = (today - datetime.fromisoformat(ms.actual_start).date()).days
                if days_elapsed > 0 and ms.progress_percent > 0:
                    daily_progress = ms.progress_percent / days_elapsed
                    remaining = 100 - ms.progress_percent
                    days_needed = remaining / daily_progress if daily_progress > 0 else 999
                    predicted_end = today + timedelta(days=int(days_needed))
                    
                    if predicted_end > planned_end:
                        delays.append({
                            "milestone": ms.name,
                            "location": ms.location,
                            "type": "predicted_delay",
                            "predicted_delay_days": (predicted_end - planned_end).days,
                            "planned_end": ms.planned_end,
                            "predicted_end": predicted_end.isoformat(),
                            "progress": ms.progress_percent,
                        })
        
        return delays
    
    def predict_completion(
        self,
        project_id: str,
        location: str,
    ) -> Dict[str, Any]:
        """Predict when a location will be complete"""
        updates = [u for u in self._progress_updates.get(project_id, [])
                   if u.location == location]
        
        if len(updates) < 2:
            return {"prediction": "Insufficient data"}
        
        # Calculate progress rate
        first = updates[0]
        last = updates[-1]
        
        days = (datetime.fromisoformat(last.updated_at) - 
                datetime.fromisoformat(first.updated_at)).days
        
        if days > 0:
            progress_diff = last.progress_percent - first.progress_percent
            daily_rate = progress_diff / days
            
            remaining = 100 - last.progress_percent
            days_to_complete = remaining / daily_rate if daily_rate > 0 else 999
            
            predicted_date = datetime.utcnow() + timedelta(days=int(days_to_complete))
            
            return {
                "location": location,
                "current_progress": last.progress_percent,
                "daily_rate": round(daily_rate, 1),
                "predicted_completion": predicted_date.date().isoformat(),
                "confidence": "medium" if len(updates) > 5 else "low",
            }
        
        return {"prediction": "Insufficient data"}
    
    # =========================================================================
    # REPORTS
    # =========================================================================
    
    def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get overall project progress"""
        milestones = self._milestones.get(project_id, [])
        
        if not milestones:
            return {"overall_progress": 0, "milestones": []}
        
        total_progress = sum(ms.progress_percent for ms in milestones)
        overall = total_progress / len(milestones)
        
        completed = len([ms for ms in milestones 
                        if ms.status in [MilestoneStatus.COMPLETED, MilestoneStatus.VERIFIED]])
        delayed = len([ms for ms in milestones if ms.status == MilestoneStatus.DELAYED])
        in_progress = len([ms for ms in milestones if ms.status == MilestoneStatus.IN_PROGRESS])
        
        return {
            "overall_progress": round(overall, 1),
            "total_milestones": len(milestones),
            "completed": completed,
            "in_progress": in_progress,
            "delayed": delayed,
            "on_track": len(milestones) - completed - delayed - in_progress,
        }
    
    def generate_progress_report(self, project_id: str) -> str:
        """Generate progress report for management"""
        progress = self.get_project_progress(project_id)
        delays = self.detect_delays(project_id)
        
        current_delays = [d for d in delays if d["type"] == "current_delay"]
        predicted_delays = [d for d in delays if d["type"] == "predicted_delay"]
        
        report = f"""
**Construction Progress Report**
Generated: {datetime.utcnow().strftime("%d %b %Y, %H:%M")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERALL PROGRESS: {progress['overall_progress']}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Milestones:
• Total: {progress['total_milestones']}
• Completed: {progress['completed']}
• In Progress: {progress['in_progress']}
• Delayed: {progress['delayed']}

"""
        
        if current_delays:
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "⚠️ CURRENT DELAYS\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for d in current_delays:
                report += f"• {d['milestone']} ({d['location']})\n"
                report += f"  Delayed by {d['delay_days']} days | Progress: {d['progress']}%\n\n"
        
        if predicted_delays:
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "📊 PREDICTED DELAYS (Action Required)\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for d in predicted_delays:
                report += f"• {d['milestone']} ({d['location']})\n"
                report += f"  Predicted {d['predicted_delay_days']} days delay\n"
                report += f"  Planned: {d['planned_end']} | Predicted: {d['predicted_end']}\n\n"
        
        return report


# Singleton instance
progress_monitoring = ProgressMonitoringService()

