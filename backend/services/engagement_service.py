"""
SiteMind Engagement Service
Professional value tracking for enterprise clients

KEEPS:
- Daily/weekly value summaries (ROI focused)
- Proactive alerts (drawing updates, trending queries)
- Time & cost savings tracking
- Issue detection metrics
- Professional reports for management

REMOVED:
- Gamification (no streaks, badges, milestones)
- Celebratory messages
- Playful language

TONE: Professional, data-driven, enterprise-grade
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from utils.logger import logger


class AlertType(str, Enum):
    DRAWING_UPDATE = "drawing_update"
    TRENDING_QUERY = "trending_query"
    ISSUE_DETECTED = "issue_detected"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_ROI = "monthly_roi"


class EngagementService:
    """
    Professional value tracking and reporting
    """
    
    def __init__(self):
        self._user_metrics: Dict[str, Dict] = {}
        self._project_metrics: Dict[str, Dict] = {}
        self._alerts: Dict[str, List[Dict]] = {}
    
    # =========================================================================
    # METRICS TRACKING
    # =========================================================================
    
    def track_query(
        self,
        project_id: str,
        user_phone: str,
        user_name: str,
        query: str,
        response: str,
        issue_detected: bool = False,
        response_time_ms: int = 0,
    ):
        """Track query metrics for reporting"""
        
        # User metrics
        if user_phone not in self._user_metrics:
            self._user_metrics[user_phone] = {
                "total_queries": 0,
                "queries_today": 0,
                "issues_flagged": 0,
                "avg_response_time_ms": 0,
            }
        
        user = self._user_metrics[user_phone]
        user["total_queries"] += 1
        user["queries_today"] += 1
        if issue_detected:
            user["issues_flagged"] += 1
        
        # Project metrics
        if project_id not in self._project_metrics:
            self._project_metrics[project_id] = {
                "total_queries": 0,
                "queries_today": 0,
                "queries_this_week": 0,
                "issues_flagged": 0,
                "active_users": set(),
                "query_categories": {},
            }
        
        proj = self._project_metrics[project_id]
        proj["total_queries"] += 1
        proj["queries_today"] += 1
        proj["queries_this_week"] += 1
        proj["active_users"].add(user_phone)
        if issue_detected:
            proj["issues_flagged"] += 1
    
    def track_drawing_upload(self, project_id: str, drawing_name: str, uploaded_by: str):
        """Track drawing uploads"""
        if project_id not in self._project_metrics:
            self._project_metrics[project_id] = {"drawing_uploads": []}
        
        if "drawing_uploads" not in self._project_metrics[project_id]:
            self._project_metrics[project_id]["drawing_uploads"] = []
        
        self._project_metrics[project_id]["drawing_uploads"].append({
            "drawing": drawing_name,
            "uploaded_by": uploaded_by,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def track_change_order(self, project_id: str, description: str):
        """Track change orders"""
        if project_id not in self._project_metrics:
            self._project_metrics[project_id] = {"change_orders": 0}
        
        self._project_metrics[project_id]["change_orders"] = \
            self._project_metrics[project_id].get("change_orders", 0) + 1
    
    # =========================================================================
    # PROFESSIONAL REPORTS
    # =========================================================================
    
    def generate_daily_summary(self, project_id: str) -> str:
        """Generate professional daily summary"""
        proj = self._project_metrics.get(project_id, {})
        queries = proj.get("queries_today", 0)
        
        if queries == 0:
            return ""
        
        time_saved_mins = queries * 5  # Conservative: 5 min per query
        active_users = len(proj.get("active_users", set()))
        issues = proj.get("issues_flagged", 0)
        
        summary = f"""**Daily Activity Summary**
Date: {datetime.utcnow().strftime("%d %b %Y")}

Queries processed: {queries}
Active users: {active_users}
Estimated time saved: {time_saved_mins} minutes
Issues flagged: {issues}

All queries logged with full audit trail."""
        
        # Reset daily counters
        proj["queries_today"] = 0
        
        return summary
    
    def generate_weekly_report(self, project_id: str, project_name: str) -> str:
        """Generate professional weekly report for management"""
        proj = self._project_metrics.get(project_id, {})
        
        queries = proj.get("queries_this_week", 0)
        time_saved_hours = (queries * 5) / 60
        active_users = len(proj.get("active_users", set()))
        issues = proj.get("issues_flagged", 0)
        change_orders = proj.get("change_orders", 0)
        drawings = len(proj.get("drawing_uploads", []))
        
        report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SITEMIND WEEKLY REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: {project_name}
Period: Week ending {datetime.utcnow().strftime("%d %b %Y")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Queries:          {queries}
Active Engineers:       {active_users}
Drawings Uploaded:      {drawings}
Change Orders Logged:   {change_orders}
Issues Flagged:         {issues}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VALUE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estimated Time Saved:   {time_saved_hours:.1f} hours
(Based on 5 min avg per manual lookup)

Engineering Cost Saved: ₹{time_saved_hours * 500:,.0f}
(At ₹500/hour engineer time)

Potential Rework Avoided: {issues} issues caught early

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DOCUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All queries, decisions, and changes are logged with:
• Timestamp
• User identification
• Source citations
• Full context

This audit trail is available for export at any time.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Reset weekly counters
        proj["queries_this_week"] = 0
        
        return report
    
    def generate_monthly_roi_report(
        self, 
        project_id: str, 
        project_name: str,
        subscription_cost: float = 500,
    ) -> str:
        """Generate monthly ROI report"""
        proj = self._project_metrics.get(project_id, {})
        
        queries = proj.get("total_queries", 0)
        issues = proj.get("issues_flagged", 0)
        change_orders = proj.get("change_orders", 0)
        
        # Conservative value calculations
        time_saved_hours = (queries * 5) / 60
        time_value = time_saved_hours * 500  # ₹500/hr
        
        # Issue prevention value (very conservative)
        issue_value = issues * 25000  # ₹25k avg per issue prevented
        
        total_value = time_value + issue_value
        roi_multiple = total_value / (subscription_cost * 83) if subscription_cost > 0 else 0
        
        report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONTHLY ROI REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: {project_name}
Month: {datetime.utcnow().strftime("%B %Y")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVITY SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Queries Processed:      {queries}
Issues Flagged:         {issues}
Change Orders Logged:   {change_orders}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VALUE CALCULATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Time Savings:
  {queries} queries × 5 min = {time_saved_hours:.1f} hours
  {time_saved_hours:.1f} hours × ₹500/hr = ₹{time_value:,.0f}

Issue Prevention (Conservative):
  {issues} issues × ₹25,000 avg = ₹{issue_value:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL ESTIMATED VALUE: ₹{total_value:,.0f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Subscription Cost:      ${subscription_cost}/month (₹{subscription_cost * 83:,.0f})
Estimated ROI:          {roi_multiple:.1f}x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Time savings based on 5 min avg per manual lookup
• Issue prevention valued conservatively at ₹25,000 each
• Actual rework costs typically range ₹50,000 - ₹5,00,000
• Documentation value (legal protection) not quantified

Complete audit trail available for export.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report
    
    # =========================================================================
    # PROACTIVE ALERTS (Professional, not gamified)
    # =========================================================================
    
    def check_drawing_update_alert(
        self,
        project_id: str,
        drawing_name: str,
        queries_using_old: int,
    ) -> Optional[str]:
        """Alert if queries reference outdated drawings"""
        if queries_using_old >= 3:
            return f"""**Drawing Update Notice**

Drawing '{drawing_name}' was recently updated. 
{queries_using_old} queries today may have referenced the previous version.

Recommended action:
• Confirm all site engineers are aware of the update
• Verify the latest revision is being used

Reply 'notify team' to send an update to all engineers."""
        return None
    
    def check_trending_query_alert(self, project_id: str) -> Optional[str]:
        """Detect unusual query patterns"""
        proj = self._project_metrics.get(project_id, {})
        categories = proj.get("query_categories", {})
        
        for category, count in categories.items():
            if count >= 5:
                return f"""**Query Pattern Detected**

Multiple queries ({count}) regarding '{category}' today.

This may indicate:
• Unclear specifications
• Recent changes not communicated
• Missing information in drawings

Consider reviewing this area with the project team."""
        
        return None
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def get_project_metrics(self, project_id: str) -> Dict[str, Any]:
        """Get current metrics for a project"""
        proj = self._project_metrics.get(project_id, {})
        return {
            "total_queries": proj.get("total_queries", 0),
            "active_users": len(proj.get("active_users", set())),
            "issues_flagged": proj.get("issues_flagged", 0),
            "change_orders": proj.get("change_orders", 0),
            "drawings_uploaded": len(proj.get("drawing_uploads", [])),
        }
    
    def reset_daily_metrics(self):
        """Reset daily counters (call at midnight)"""
        for proj in self._project_metrics.values():
            proj["queries_today"] = 0
        for user in self._user_metrics.values():
            user["queries_today"] = 0
    
    def reset_weekly_metrics(self):
        """Reset weekly counters (call on Monday)"""
        for proj in self._project_metrics.values():
            proj["queries_this_week"] = 0


# Singleton instance
engagement_service = EngagementService()
