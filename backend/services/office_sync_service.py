"""
SiteMind Office Sync Service
The bridge between site and office - ensuring nothing falls through

DAILY SYNC:
- Morning: Brief to site engineers (what's happening today)
- Evening: Summary to office/PMs (what happened today)
- Weekly: Full report to management

This ensures:
1. Office knows everything happening on site
2. Site knows what office expects
3. Nothing is lost in communication
4. All decisions are visible to both sides
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from utils.logger import logger


@dataclass
class DailyActivity:
    """Track daily site activity"""
    date: str
    project_id: str
    company_id: str
    
    # Queries & Discussions
    total_queries: int = 0
    queries_list: List[str] = field(default_factory=list)
    
    # Documents & Photos
    photos_uploaded: int = 0
    documents_uploaded: int = 0
    
    # Changes & Decisions
    change_orders_created: int = 0
    decisions_made: List[str] = field(default_factory=list)
    
    # Issues & Alerts
    safety_flags: int = 0
    issues_reported: List[str] = field(default_factory=list)
    alerts_raised: int = 0
    
    # Billable Work
    billable_items: List[str] = field(default_factory=list)
    
    # Active Users
    active_users: List[str] = field(default_factory=list)


class OfficeSyncService:
    """
    Keep office and site perfectly in sync
    """
    
    def __init__(self):
        # Daily activity tracking
        self._daily_activity: Dict[str, DailyActivity] = {}  # key: date_projectId
        
        # PM/Admin contacts for each company
        self._office_contacts: Dict[str, List[str]] = {}  # company_id -> list of phones
    
    # =========================================================================
    # ACTIVITY TRACKING
    # =========================================================================
    
    def _get_activity(self, project_id: str, company_id: str) -> DailyActivity:
        """Get or create today's activity tracker"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"{today}_{project_id}"
        
        if key not in self._daily_activity:
            self._daily_activity[key] = DailyActivity(
                date=today,
                project_id=project_id,
                company_id=company_id,
            )
        
        return self._daily_activity[key]
    
    def track_query(
        self,
        project_id: str,
        company_id: str,
        question: str,
        user_id: str,
    ):
        """Track a query from site"""
        activity = self._get_activity(project_id, company_id)
        activity.total_queries += 1
        activity.queries_list.append(question[:100])
        
        if user_id not in activity.active_users:
            activity.active_users.append(user_id)
    
    def track_photo(
        self,
        project_id: str,
        company_id: str,
        caption: str,
        user_id: str,
    ):
        """Track photo upload"""
        activity = self._get_activity(project_id, company_id)
        activity.photos_uploaded += 1
        
        if user_id not in activity.active_users:
            activity.active_users.append(user_id)
    
    def track_document(
        self,
        project_id: str,
        company_id: str,
        doc_name: str,
        user_id: str,
    ):
        """Track document upload"""
        activity = self._get_activity(project_id, company_id)
        activity.documents_uploaded += 1
        
        if user_id not in activity.active_users:
            activity.active_users.append(user_id)
    
    def track_change_order(
        self,
        project_id: str,
        company_id: str,
        description: str,
    ):
        """Track change order creation"""
        activity = self._get_activity(project_id, company_id)
        activity.change_orders_created += 1
        activity.decisions_made.append(f"Change: {description[:50]}")
    
    def track_decision(
        self,
        project_id: str,
        company_id: str,
        decision: str,
    ):
        """Track a decision made"""
        activity = self._get_activity(project_id, company_id)
        activity.decisions_made.append(decision[:100])
    
    def track_safety_flag(
        self,
        project_id: str,
        company_id: str,
        issue: str,
    ):
        """Track safety issue"""
        activity = self._get_activity(project_id, company_id)
        activity.safety_flags += 1
        activity.issues_reported.append(f"⚠️ Safety: {issue[:50]}")
    
    def track_issue(
        self,
        project_id: str,
        company_id: str,
        issue: str,
    ):
        """Track reported issue"""
        activity = self._get_activity(project_id, company_id)
        activity.issues_reported.append(issue[:100])
    
    def track_billable(
        self,
        project_id: str,
        company_id: str,
        description: str,
    ):
        """Track billable work item"""
        activity = self._get_activity(project_id, company_id)
        activity.billable_items.append(description[:100])
    
    def track_alert(
        self,
        project_id: str,
        company_id: str,
    ):
        """Track alert raised"""
        activity = self._get_activity(project_id, company_id)
        activity.alerts_raised += 1
    
    # =========================================================================
    # DAILY SUMMARIES
    # =========================================================================
    
    def generate_evening_summary(
        self,
        project_id: str,
        company_id: str,
        project_name: str,
    ) -> Dict[str, Any]:
        """
        Generate evening summary for office/PM
        
        This is the "what happened today" report
        """
        activity = self._get_activity(project_id, company_id)
        
        summary = {
            "type": "evening_summary",
            "project_id": project_id,
            "project_name": project_name,
            "date": activity.date,
            "generated_at": datetime.utcnow().isoformat(),
            
            "stats": {
                "total_queries": activity.total_queries,
                "photos_uploaded": activity.photos_uploaded,
                "documents_uploaded": activity.documents_uploaded,
                "active_users": len(activity.active_users),
            },
            
            "attention_needed": {
                "change_orders": activity.change_orders_created,
                "safety_flags": activity.safety_flags,
                "issues": len(activity.issues_reported),
                "alerts": activity.alerts_raised,
            },
            
            "billable_work": activity.billable_items,
            "decisions_made": activity.decisions_made,
            "issues_reported": activity.issues_reported,
            "top_queries": activity.queries_list[:5],
        }
        
        # Status assessment
        if activity.safety_flags > 0:
            summary["status"] = "critical"
            summary["status_message"] = "⚠️ Safety issues detected - immediate attention required"
        elif activity.change_orders_created > 0 or activity.alerts_raised > 0:
            summary["status"] = "attention"
            summary["status_message"] = "🟡 Items need your approval or review"
        else:
            summary["status"] = "normal"
            summary["status_message"] = "✅ Normal day - no critical issues"
        
        return summary
    
    def format_evening_summary_whatsapp(self, summary: Dict) -> str:
        """Format evening summary for WhatsApp to office"""
        
        status_icons = {
            "critical": "🔴",
            "attention": "🟡",
            "normal": "🟢",
        }
        
        msg = f"""{status_icons.get(summary['status'], '📊')} *Evening Summary: {summary['project_name']}*
📅 {summary['date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Today's Activity:*
• Queries: {summary['stats']['total_queries']}
• Photos: {summary['stats']['photos_uploaded']}
• Documents: {summary['stats']['documents_uploaded']}
• Active Users: {summary['stats']['active_users']}

"""
        
        # Attention items
        attention = summary['attention_needed']
        if any(v > 0 for v in attention.values()):
            msg += "🚨 *Needs Attention:*\n"
            if attention['safety_flags'] > 0:
                msg += f"• ⚠️ Safety Flags: {attention['safety_flags']}\n"
            if attention['change_orders'] > 0:
                msg += f"• 📝 New Change Orders: {attention['change_orders']}\n"
            if attention['issues'] > 0:
                msg += f"• ❗ Issues Reported: {attention['issues']}\n"
            if attention['alerts'] > 0:
                msg += f"• 🔔 Alerts: {attention['alerts']}\n"
            msg += "\n"
        
        # Billable work
        if summary['billable_work']:
            msg += "💰 *Billable Work:*\n"
            for item in summary['billable_work'][:3]:
                msg += f"• {item}\n"
            if len(summary['billable_work']) > 3:
                msg += f"_... and {len(summary['billable_work']) - 3} more_\n"
            msg += "\n"
        
        # Decisions
        if summary['decisions_made']:
            msg += "✅ *Decisions Made:*\n"
            for decision in summary['decisions_made'][:3]:
                msg += f"• {decision}\n"
            if len(summary['decisions_made']) > 3:
                msg += f"_... and {len(summary['decisions_made']) - 3} more_\n"
            msg += "\n"
        
        # Issues
        if summary['issues_reported']:
            msg += "⚠️ *Issues Reported:*\n"
            for issue in summary['issues_reported'][:3]:
                msg += f"• {issue}\n"
            msg += "\n"
        
        msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{summary['status_message']}"
        
        return msg
    
    def generate_morning_brief(
        self,
        project_id: str,
        company_id: str,
        project_name: str,
        pending_items: Dict = None,
    ) -> str:
        """
        Generate morning brief for site engineers
        
        This is the "what's expected today" message
        """
        
        now = datetime.utcnow()
        
        msg = f"""☀️ *Good Morning! {project_name}*
📅 {now.strftime("%A, %B %d")}

"""
        
        # Pending items from yesterday
        if pending_items:
            if pending_items.get("change_orders", 0) > 0:
                msg += f"📝 *{pending_items['change_orders']} Change Order(s)* awaiting approval\n"
            if pending_items.get("unbilled_items", 0) > 0:
                msg += f"💰 *{pending_items['unbilled_items']} item(s)* need to be billed\n"
            if pending_items.get("alerts", 0) > 0:
                msg += f"🚨 *{pending_items['alerts']} alert(s)* need attention\n"
            msg += "\n"
        
        msg += """💡 *Quick Reminders:*
• Document all changes with photos
• Log any extra work for billing
• Report safety issues immediately
• Ask SiteMind before uncertain decisions

_Reply with any questions. Have a productive day!_ 🏗️"""
        
        return msg
    
    # =========================================================================
    # WEEKLY REPORT
    # =========================================================================
    
    def generate_weekly_report(
        self,
        company_id: str,
        project_ids: List[str] = None,
    ) -> Dict[str, Any]:
        """Generate weekly report for management"""
        
        # Aggregate last 7 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        report = {
            "type": "weekly_report",
            "company_id": company_id,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "generated_at": end_date.isoformat(),
            "projects": [],
            "totals": {
                "queries": 0,
                "photos": 0,
                "documents": 0,
                "change_orders": 0,
                "safety_flags": 0,
                "billable_items": 0,
            },
        }
        
        # Aggregate from daily activities
        for key, activity in self._daily_activity.items():
            if activity.company_id != company_id:
                continue
            
            # Check date range
            activity_date = datetime.strptime(activity.date, "%Y-%m-%d")
            if activity_date < start_date or activity_date > end_date:
                continue
            
            if project_ids and activity.project_id not in project_ids:
                continue
            
            report["totals"]["queries"] += activity.total_queries
            report["totals"]["photos"] += activity.photos_uploaded
            report["totals"]["documents"] += activity.documents_uploaded
            report["totals"]["change_orders"] += activity.change_orders_created
            report["totals"]["safety_flags"] += activity.safety_flags
            report["totals"]["billable_items"] += len(activity.billable_items)
        
        return report
    
    def format_weekly_report_whatsapp(self, report: Dict) -> str:
        """Format weekly report for WhatsApp"""
        
        totals = report["totals"]
        
        return f"""📊 *Weekly Report*
📅 {report['period']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*Activity Summary:*
• Total Queries: {totals['queries']}
• Photos Analyzed: {totals['photos']}
• Documents Uploaded: {totals['documents']}

*Items Tracked:*
• Change Orders: {totals['change_orders']}
• Safety Flags: {totals['safety_flags']}
• Billable Items: {totals['billable_items']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_Full report available on dashboard._"""
    
    # =========================================================================
    # OFFICE CONTACT MANAGEMENT
    # =========================================================================
    
    def add_office_contact(self, company_id: str, phone: str, role: str = "pm"):
        """Add office contact for summaries"""
        if company_id not in self._office_contacts:
            self._office_contacts[company_id] = []
        
        self._office_contacts[company_id].append({
            "phone": phone,
            "role": role,
        })
    
    def get_office_contacts(self, company_id: str) -> List[Dict]:
        """Get office contacts for a company"""
        return self._office_contacts.get(company_id, [])


# Singleton instance
office_sync_service = OfficeSyncService()

