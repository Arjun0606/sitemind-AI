"""
SiteMind Daily Brief Service
Automated morning summaries that make PMs addicted

This is the "I can't start my day without SiteMind" feature.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from utils.logger import logger


@dataclass
class ProjectBrief:
    """Daily brief for a project"""
    project_id: str
    project_name: str
    date: str
    
    # Activity summary
    queries_yesterday: int = 0
    photos_yesterday: int = 0
    documents_yesterday: int = 0
    active_users: int = 0
    
    # Alerts
    safety_flags: int = 0
    conflicts_detected: int = 0
    pending_decisions: int = 0
    
    # Insights
    top_topics: List[str] = None
    recommendations: List[str] = None


class DailyBriefService:
    """
    Generate and send daily morning briefs
    
    Sent at 8 AM to project managers/owners
    """
    
    def __init__(self):
        # Track daily activity per project
        self._daily_activity: Dict[str, Dict] = {}
        
        # Brief templates
        self.GREETING_TEMPLATES = [
            "☀️ Good morning! Here's your daily brief.",
            "🌅 Rise and shine! Your projects await.",
            "☕ Morning! Let's make today productive.",
        ]
    
    # =========================================================================
    # TRACK ACTIVITY
    # =========================================================================
    
    def track_query(self, project_id: str, topic: str = None):
        """Track a query for daily summary"""
        self._ensure_day(project_id)
        self._daily_activity[project_id]["queries"] += 1
        
        if topic:
            topics = self._daily_activity[project_id].setdefault("topics", {})
            topics[topic] = topics.get(topic, 0) + 1
    
    def track_photo(self, project_id: str):
        """Track photo upload"""
        self._ensure_day(project_id)
        self._daily_activity[project_id]["photos"] += 1
    
    def track_document(self, project_id: str):
        """Track document upload"""
        self._ensure_day(project_id)
        self._daily_activity[project_id]["documents"] += 1
    
    def track_user(self, project_id: str, user_id: str):
        """Track active user"""
        self._ensure_day(project_id)
        self._daily_activity[project_id].setdefault("users", set()).add(user_id)
    
    def track_safety_flag(self, project_id: str):
        """Track safety issue detected"""
        self._ensure_day(project_id)
        self._daily_activity[project_id]["safety_flags"] += 1
    
    def track_conflict(self, project_id: str):
        """Track conflict detected"""
        self._ensure_day(project_id)
        self._daily_activity[project_id]["conflicts"] += 1
    
    def _ensure_day(self, project_id: str):
        """Ensure today's tracking exists"""
        today = datetime.utcnow().date().isoformat()
        
        if project_id not in self._daily_activity:
            self._daily_activity[project_id] = {}
        
        if self._daily_activity[project_id].get("date") != today:
            # New day - reset
            self._daily_activity[project_id] = {
                "date": today,
                "queries": 0,
                "photos": 0,
                "documents": 0,
                "users": set(),
                "safety_flags": 0,
                "conflicts": 0,
                "topics": {},
            }
    
    # =========================================================================
    # GENERATE BRIEFS
    # =========================================================================
    
    def generate_brief(
        self,
        project_id: str,
        project_name: str,
        include_recommendations: bool = True,
    ) -> ProjectBrief:
        """Generate daily brief for a project"""
        activity = self._daily_activity.get(project_id, {})
        
        # Get top topics
        topics = activity.get("topics", {})
        top_topics = sorted(topics.keys(), key=lambda k: topics[k], reverse=True)[:3]
        
        # Generate recommendations
        recommendations = []
        if include_recommendations:
            recommendations = self._generate_recommendations(activity)
        
        return ProjectBrief(
            project_id=project_id,
            project_name=project_name,
            date=datetime.utcnow().strftime("%A, %B %d, %Y"),
            queries_yesterday=activity.get("queries", 0),
            photos_yesterday=activity.get("photos", 0),
            documents_yesterday=activity.get("documents", 0),
            active_users=len(activity.get("users", set())),
            safety_flags=activity.get("safety_flags", 0),
            conflicts_detected=activity.get("conflicts", 0),
            top_topics=top_topics,
            recommendations=recommendations,
        )
    
    def _generate_recommendations(self, activity: Dict) -> List[str]:
        """Generate smart recommendations"""
        recs = []
        
        queries = activity.get("queries", 0)
        photos = activity.get("photos", 0)
        safety = activity.get("safety_flags", 0)
        
        if queries == 0:
            recs.append("💡 Your team didn't use SiteMind yesterday. Remind them it's available 24/7!")
        
        if photos == 0:
            recs.append("📸 No site photos yesterday. Daily progress photos help track milestones.")
        
        if safety > 0:
            recs.append(f"⚠️ {safety} safety concern(s) flagged. Please review and address.")
        
        if queries > 20:
            recs.append("🔥 High activity! Your team is getting great value from SiteMind.")
        
        return recs
    
    # =========================================================================
    # FORMAT BRIEFS
    # =========================================================================
    
    def format_brief_whatsapp(self, brief: ProjectBrief) -> str:
        """Format brief for WhatsApp"""
        
        # Choose greeting based on day
        day_of_week = datetime.utcnow().weekday()
        greeting = self.GREETING_TEMPLATES[day_of_week % len(self.GREETING_TEMPLATES)]
        
        msg = f"""
{greeting}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 *{brief.project_name}*
{brief.date}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Yesterday's Activity*
• {brief.queries_yesterday} questions answered
• {brief.photos_yesterday} photos analyzed
• {brief.documents_yesterday} documents processed
• {brief.active_users} team members active"""

        if brief.safety_flags > 0 or brief.conflicts_detected > 0:
            msg += f"""

⚠️ *Alerts*"""
            if brief.safety_flags > 0:
                msg += f"\n• {brief.safety_flags} safety concern(s) - please review"
            if brief.conflicts_detected > 0:
                msg += f"\n• {brief.conflicts_detected} potential conflict(s) detected"
        
        if brief.top_topics:
            msg += f"""

🔍 *Hot Topics*
• {', '.join(brief.top_topics)}"""

        if brief.recommendations:
            msg += f"""

💡 *Recommendations*"""
            for rec in brief.recommendations[:3]:
                msg += f"\n{rec}"

        msg += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Have a productive day! 🏗️
_Reply to ask anything_
"""
        return msg
    
    def format_company_brief(
        self,
        company_name: str,
        project_briefs: List[ProjectBrief],
    ) -> str:
        """Format company-wide brief (multiple projects)"""
        
        total_queries = sum(b.queries_yesterday for b in project_briefs)
        total_photos = sum(b.photos_yesterday for b in project_briefs)
        total_safety = sum(b.safety_flags for b in project_briefs)
        total_users = sum(b.active_users for b in project_briefs)
        
        msg = f"""
☀️ *Good Morning, {company_name}!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *Company Overview - Yesterday*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• {len(project_briefs)} active projects
• {total_queries} questions answered
• {total_photos} photos analyzed
• {total_users} team members active"""

        if total_safety > 0:
            msg += f"\n• ⚠️ {total_safety} safety alert(s) - review needed"

        msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 *Project Breakdown*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for brief in project_briefs[:5]:  # Top 5 projects
            status = "⚠️" if brief.safety_flags > 0 else "✅"
            msg += f"\n{status} *{brief.project_name}*: {brief.queries_yesterday} queries, {brief.active_users} users"
        
        if len(project_briefs) > 5:
            msg += f"\n_...and {len(project_briefs) - 5} more projects_"

        msg += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Have a great day! 🏗️
_Type 'projects' to see all projects_
"""
        return msg
    
    # =========================================================================
    # RESET
    # =========================================================================
    
    def reset_day(self, project_id: str) -> Dict:
        """Reset and return yesterday's data"""
        data = self._daily_activity.pop(project_id, {})
        return data


# Singleton
daily_brief_service = DailyBriefService()

