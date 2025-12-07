"""
SiteMind Report Service
Automated weekly and monthly reports

These reports justify the $1000/month and make renewals automatic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass 
class WeeklyReport:
    """Weekly report data"""
    company_id: str
    company_name: str
    week_start: str
    week_end: str
    
    # Activity
    total_queries: int = 0
    total_photos: int = 0
    total_documents: int = 0
    active_users: int = 0
    active_projects: int = 0
    
    # Value delivered
    hours_saved: float = 0
    time_value_inr: float = 0
    safety_flags: int = 0
    safety_value_inr: float = 0
    conflicts_caught: int = 0
    conflicts_value_inr: float = 0
    
    # Engagement
    busiest_day: str = None
    top_users: List[str] = None
    top_topics: List[str] = None


class ReportService:
    """
    Generate automated reports that prove ROI
    """
    
    def __init__(self):
        # Value calculations
        self.MINUTES_PER_QUERY = 5         # Time saved per query
        self.MINUTES_PER_PHOTO = 10        # Time saved per photo analysis
        self.ENGINEER_HOURLY_RATE = 500    # ₹500/hour
        self.SAFETY_VALUE = 100000         # ₹1 lakh per safety issue
        self.CONFLICT_VALUE = 200000       # ₹2 lakh per conflict caught
        
        # Report storage
        self._reports: List[Dict] = []
    
    # =========================================================================
    # GENERATE REPORTS
    # =========================================================================
    
    def generate_weekly_report(
        self,
        company_id: str,
        company_name: str,
        activity_data: Dict,
    ) -> WeeklyReport:
        """Generate weekly report from activity data"""
        
        # Calculate time saved
        queries = activity_data.get("queries", 0)
        photos = activity_data.get("photos", 0)
        
        minutes_saved = (queries * self.MINUTES_PER_QUERY) + (photos * self.MINUTES_PER_PHOTO)
        hours_saved = minutes_saved / 60
        time_value = hours_saved * self.ENGINEER_HOURLY_RATE
        
        # Safety value
        safety_flags = activity_data.get("safety_flags", 0)
        safety_value = safety_flags * self.SAFETY_VALUE
        
        # Conflict value
        conflicts = activity_data.get("conflicts", 0)
        conflicts_value = conflicts * self.CONFLICT_VALUE
        
        # Week dates
        today = datetime.utcnow()
        week_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        week_end = today.strftime("%Y-%m-%d")
        
        return WeeklyReport(
            company_id=company_id,
            company_name=company_name,
            week_start=week_start,
            week_end=week_end,
            total_queries=queries,
            total_photos=photos,
            total_documents=activity_data.get("documents", 0),
            active_users=activity_data.get("active_users", 0),
            active_projects=activity_data.get("active_projects", 0),
            hours_saved=round(hours_saved, 1),
            time_value_inr=round(time_value),
            safety_flags=safety_flags,
            safety_value_inr=safety_value,
            conflicts_caught=conflicts,
            conflicts_value_inr=conflicts_value,
            top_topics=activity_data.get("top_topics", []),
        )
    
    # =========================================================================
    # FORMAT REPORTS
    # =========================================================================
    
    def format_weekly_whatsapp(self, report: WeeklyReport) -> str:
        """Format weekly report for WhatsApp"""
        
        total_value = report.time_value_inr + report.safety_value_inr + report.conflicts_value_inr
        
        msg = f"""
📊 *WEEKLY REPORT*
{report.company_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{report.week_start} to {report.week_end}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *ACTIVITY*
• {report.total_queries:,} questions answered
• {report.total_photos:,} photos analyzed
• {report.total_documents:,} documents processed
• {report.active_users} team members active
• {report.active_projects} projects active

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ *TIME SAVED*
• {report.hours_saved} hours this week
• Worth ₹{report.time_value_inr:,}"""

        if report.safety_flags > 0:
            msg += f"""

🛡️ *SAFETY*
• {report.safety_flags} issue(s) flagged
• Estimated savings: ₹{report.safety_value_inr:,}"""

        if report.conflicts_caught > 0:
            msg += f"""

🔄 *CONFLICTS CAUGHT*
• {report.conflicts_caught} conflict(s) detected
• Rework prevented: ₹{report.conflicts_value_inr:,}"""

        if report.top_topics:
            msg += f"""

🔍 *TOP TOPICS*
• {', '.join(report.top_topics[:5])}"""

        msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *TOTAL VALUE DELIVERED*

        ₹{total_value:,}
        
        (${int(total_value/83):,} USD)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_SiteMind cost: ₹{int(1000*83/4):,}/week_
_ROI: {int(total_value/(1000*83/4))}x_ 🚀

Keep building! 🏗️
"""
        return msg
    
    def format_monthly_whatsapp(
        self,
        company_name: str,
        monthly_data: Dict,
    ) -> str:
        """Format monthly report"""
        
        queries = monthly_data.get("queries", 0)
        photos = monthly_data.get("photos", 0)
        documents = monthly_data.get("documents", 0)
        safety_flags = monthly_data.get("safety_flags", 0)
        conflicts = monthly_data.get("conflicts", 0)
        
        # Calculate value
        hours_saved = ((queries * 5) + (photos * 10)) / 60
        time_value = hours_saved * 500
        safety_value = safety_flags * 100000
        conflicts_value = conflicts * 200000
        total_value = time_value + safety_value + conflicts_value
        
        # Cost
        monthly_cost = 1000 * 83  # $1000 in INR
        roi = total_value / monthly_cost if monthly_cost > 0 else 0
        
        msg = f"""
📊 *MONTHLY REPORT*
{company_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{datetime.utcnow().strftime('%B %Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 *MONTHLY ACTIVITY*

Questions Answered      {queries:>8,}
Photos Analyzed         {photos:>8,}
Documents Processed     {documents:>8,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *VALUE DELIVERED*

Time Saved ({hours_saved:.0f} hrs)     ₹{time_value:>10,.0f}
Safety Issues ({safety_flags})         ₹{safety_value:>10,.0f}
Conflicts Caught ({conflicts})         ₹{conflicts_value:>10,.0f}
                            ─────────────
*TOTAL VALUE*              ₹{total_value:>10,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *ROI ANALYSIS*

SiteMind Cost             ₹{monthly_cost:>10,}
Value Delivered           ₹{total_value:>10,.0f}
                            ─────────────
*NET VALUE*               ₹{total_value - monthly_cost:>10,.0f}

*ROI: {roi:.1f}x your investment* 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for trusting SiteMind! 🏗️
"""
        return msg
    
    # =========================================================================
    # EXECUTIVE SUMMARY
    # =========================================================================
    
    def format_executive_summary(
        self,
        company_name: str,
        data: Dict,
    ) -> str:
        """One-page executive summary for management"""
        
        queries = data.get("queries", 0)
        photos = data.get("photos", 0)
        safety_flags = data.get("safety_flags", 0)
        conflicts = data.get("conflicts", 0)
        active_projects = data.get("active_projects", 0)
        active_users = data.get("active_users", 0)
        
        hours_saved = ((queries * 5) + (photos * 10)) / 60
        total_value = (hours_saved * 500) + (safety_flags * 100000) + (conflicts * 200000)
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        SITEMIND EXECUTIVE SUMMARY
        {company_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COVERAGE
├── {active_projects} active projects
├── {active_users} team members using SiteMind
└── 24/7 AI support across all sites

ACTIVITY
├── {queries:,} questions answered
├── {photos:,} site photos analyzed
└── {conflicts} potential conflicts caught

VALUE DELIVERED
├── {hours_saved:.0f} engineer hours saved
├── {safety_flags} safety issues flagged
└── ₹{total_value:,.0f} estimated value

INVESTMENT
├── Monthly cost: ₹{1000*83:,}
├── Value delivered: ₹{total_value:,.0f}
└── ROI: {total_value/(1000*83):.1f}x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Powered by SiteMind 🏗️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# Singleton
report_service = ReportService()
