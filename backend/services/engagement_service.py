"""
SiteMind Engagement Service
Professional communication and reporting

FEATURES:
- Morning briefs
- Daily/weekly summaries
- Proactive alerts
- Query tracking

NO GAMIFICATION - Enterprise-focused
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ProjectActivity:
    """Daily activity for a project"""
    queries: List[Dict] = field(default_factory=list)
    documents_uploaded: int = 0
    issues_flagged: int = 0
    tasks_completed: int = 0
    decisions_made: int = 0


class EngagementService:
    """
    Professional engagement and reporting
    """
    
    def __init__(self):
        self._activity: Dict[str, Dict[str, ProjectActivity]] = {}  # project_id -> date -> activity
        self._user_queries: Dict[str, List[Dict]] = {}  # user_phone -> queries
    
    # =========================================================================
    # ACTIVITY TRACKING
    # =========================================================================
    
    def track_query(
        self,
        project_id: str,
        user_phone: str,
        user_name: str,
        query: str,
        response: str,
    ):
        """Track a query for reporting"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        if project_id not in self._activity:
            self._activity[project_id] = {}
        if today not in self._activity[project_id]:
            self._activity[project_id][today] = ProjectActivity()
        
        self._activity[project_id][today].queries.append({
            "user_phone": user_phone,
            "user_name": user_name,
            "query": query,
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Track per user
        if user_phone not in self._user_queries:
            self._user_queries[user_phone] = []
        self._user_queries[user_phone].append({
            "project_id": project_id,
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def track_document_upload(self, project_id: str):
        """Track document upload"""
        self._get_today_activity(project_id).documents_uploaded += 1
    
    def track_issue_flagged(self, project_id: str):
        """Track issue flagged"""
        self._get_today_activity(project_id).issues_flagged += 1
    
    def track_task_completed(self, project_id: str):
        """Track task completion"""
        self._get_today_activity(project_id).tasks_completed += 1
    
    def track_decision_made(self, project_id: str):
        """Track decision made"""
        self._get_today_activity(project_id).decisions_made += 1
    
    def _get_today_activity(self, project_id: str) -> ProjectActivity:
        """Get today's activity for a project"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        if project_id not in self._activity:
            self._activity[project_id] = {}
        if today not in self._activity[project_id]:
            self._activity[project_id][today] = ProjectActivity()
        
        return self._activity[project_id][today]
    
    # =========================================================================
    # REPORT GENERATION
    # =========================================================================
    
    def generate_daily_summary(self, project_id: str) -> str:
        """Generate daily summary for project"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        activity = self._activity.get(project_id, {}).get(today, ProjectActivity())
        
        query_count = len(activity.queries)
        
        # Group queries by user
        by_user = defaultdict(list)
        for q in activity.queries:
            by_user[q["user_name"]].append(q)
        
        summary = f"""**Daily Summary** - {today}

**Activity Overview:**
• Queries Answered: {query_count}
• Documents Uploaded: {activity.documents_uploaded}
• Issues Flagged: {activity.issues_flagged}
• Tasks Completed: {activity.tasks_completed}
"""

        if by_user:
            summary += "\n**Team Activity:**\n"
            for user, queries in by_user.items():
                summary += f"• {user}: {len(queries)} queries\n"
        
        summary += "\n_Reply with any query to get started._"
        
        return summary
    
    def generate_weekly_report(self, project_id: str, project_name: str) -> str:
        """Generate weekly report for management"""
        
        # Get last 7 days of activity
        total_queries = 0
        total_docs = 0
        total_issues = 0
        total_tasks = 0
        total_decisions = 0
        daily_breakdown = []
        
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            activity = self._activity.get(project_id, {}).get(date, ProjectActivity())
            
            day_queries = len(activity.queries)
            total_queries += day_queries
            total_docs += activity.documents_uploaded
            total_issues += activity.issues_flagged
            total_tasks += activity.tasks_completed
            total_decisions += activity.decisions_made
            
            if day_queries > 0 or activity.documents_uploaded > 0:
                daily_breakdown.append({
                    "date": date,
                    "queries": day_queries,
                    "docs": activity.documents_uploaded,
                })
        
        report = f"""**Weekly Report**
Project: {project_name}
Period: Last 7 Days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Queries Answered:     {total_queries}
Documents Processed:  {total_docs}
Issues Caught:        {total_issues}
Tasks Completed:      {total_tasks}
Decisions Logged:     {total_decisions}

"""

        if daily_breakdown:
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "DAILY ACTIVITY\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for day in daily_breakdown[:5]:  # Show last 5 active days
                report += f"{day['date']}: {day['queries']} queries, {day['docs']} docs\n"
        
        report += "\n_Full analytics available on the dashboard._"
        
        return report
    
    # =========================================================================
    # MORNING BRIEF
    # =========================================================================
    
    def generate_morning_brief(
        self,
        project_id: str,
        project_name: str,
        pending_tasks: List[Dict] = None,
        pending_rfis: List[Dict] = None,
        upcoming_milestones: List[Dict] = None,
    ) -> str:
        """Generate morning brief for PM"""
        
        now = datetime.utcnow()
        greeting = "Good Morning" if now.hour < 12 else "Good Afternoon"
        
        brief = f"""{greeting}! ☀️

**Daily Brief** - {project_name}
{now.strftime("%B %d, %Y")}

"""

        # Pending tasks
        if pending_tasks:
            brief += f"**📋 Pending Tasks ({len(pending_tasks)})**\n"
            for task in pending_tasks[:3]:
                brief += f"• {task.get('title', 'Task')}"
                if task.get("assigned_to"):
                    brief += f" ({task['assigned_to']})"
                brief += "\n"
            if len(pending_tasks) > 3:
                brief += f"  _...and {len(pending_tasks) - 3} more_\n"
            brief += "\n"
        
        # Pending RFIs
        if pending_rfis:
            brief += f"**❓ Pending RFIs ({len(pending_rfis)})**\n"
            for rfi in pending_rfis[:2]:
                brief += f"• {rfi.get('question', 'RFI')[:50]}...\n"
            brief += "\n"
        
        # Upcoming milestones
        if upcoming_milestones:
            brief += f"**🎯 Upcoming Milestones**\n"
            for ms in upcoming_milestones[:3]:
                brief += f"• {ms.get('name', 'Milestone')} - {ms.get('due', 'TBD')}\n"
            brief += "\n"
        
        brief += "_Reply with any question about today's work._"
        
        return brief
    
    # =========================================================================
    # PROACTIVE ALERTS
    # =========================================================================
    
    def generate_alert(
        self,
        alert_type: str,
        title: str,
        description: str,
        priority: str = "high",
    ) -> str:
        """Generate formatted alert message"""
        
        icons = {
            "safety": "🚨",
            "deadline": "⏰",
            "material": "📦",
            "weather": "🌧️",
            "inspection": "📋",
            "conflict": "⚠️",
        }
        
        icon = icons.get(alert_type, "⚠️")
        
        return f"""{icon} **ALERT: {title}**

{description}

_Reply 'more' for details or 'dismiss' to acknowledge._"""


# Singleton instance
engagement_service = EngagementService()
