"""
SiteMind ROI Tracking Service
Transparent value calculation for clients

METHODOLOGY:
1. Track measurable actions (queries, issues caught)
2. Apply conservative time/cost estimates
3. Never overstate value
4. Show calculation methodology
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class ROIMetrics:
    """ROI metrics for a project"""
    queries_answered: int = 0
    issues_flagged: int = 0
    documents_processed: int = 0
    decisions_logged: int = 0
    time_saved_minutes: int = 0


class ROIService:
    """
    Track and calculate ROI for clients
    """
    
    def __init__(self):
        self._metrics: Dict[str, ROIMetrics] = {}
        
        # Conservative value estimates
        self.MINUTES_PER_QUERY = 5  # Manual lookup time saved
        self.VALUE_PER_ISSUE = 25000  # ₹25,000 avg per issue prevented
        self.HOURLY_ENGINEER_RATE = 500  # ₹500/hour
        self.HOURLY_PM_RATE = 1000  # ₹1000/hour
    
    def get_metrics(self, project_id: str) -> ROIMetrics:
        """Get or create metrics for a project"""
        if project_id not in self._metrics:
            self._metrics[project_id] = ROIMetrics()
        return self._metrics[project_id]
    
    def record_query(self, project_id: str, time_saved_minutes: int = 5):
        """Record a query answered"""
        metrics = self.get_metrics(project_id)
        metrics.queries_answered += 1
        metrics.time_saved_minutes += time_saved_minutes
    
    def record_issue_flagged(self, project_id: str):
        """Record an issue/red flag caught"""
        metrics = self.get_metrics(project_id)
        metrics.issues_flagged += 1
    
    def record_document_processed(self, project_id: str):
        """Record a document processed"""
        metrics = self.get_metrics(project_id)
        metrics.documents_processed += 1
    
    def record_decision_logged(self, project_id: str):
        """Record a decision logged"""
        metrics = self.get_metrics(project_id)
        metrics.decisions_logged += 1
    
    def calculate_roi(
        self,
        project_id: str,
        subscription_cost_usd: float = 500,
    ) -> Dict[str, Any]:
        """
        Calculate ROI for a project
        
        Returns transparent calculation with methodology
        """
        metrics = self.get_metrics(project_id)
        
        # Time savings calculation
        hours_saved = metrics.time_saved_minutes / 60
        time_value = hours_saved * self.HOURLY_ENGINEER_RATE
        
        # Issue prevention (conservative)
        issue_value = metrics.issues_flagged * self.VALUE_PER_ISSUE
        
        # Total value
        total_value = time_value + issue_value
        
        # Subscription cost in INR (approximate)
        subscription_cost_inr = subscription_cost_usd * 83
        
        # ROI multiple
        roi_multiple = total_value / subscription_cost_inr if subscription_cost_inr > 0 else 0
        
        return {
            "metrics": {
                "queries_answered": metrics.queries_answered,
                "issues_flagged": metrics.issues_flagged,
                "documents_processed": metrics.documents_processed,
                "decisions_logged": metrics.decisions_logged,
                "time_saved_hours": round(hours_saved, 1),
            },
            "value_calculation": {
                "time_savings": {
                    "hours": round(hours_saved, 1),
                    "rate_per_hour": self.HOURLY_ENGINEER_RATE,
                    "value_inr": round(time_value, 0),
                    "methodology": f"{metrics.queries_answered} queries × {self.MINUTES_PER_QUERY} min avg = {round(hours_saved, 1)} hours",
                },
                "issue_prevention": {
                    "issues_caught": metrics.issues_flagged,
                    "value_per_issue": self.VALUE_PER_ISSUE,
                    "value_inr": round(issue_value, 0),
                    "methodology": f"{metrics.issues_flagged} issues × ₹{self.VALUE_PER_ISSUE:,} avg = ₹{round(issue_value, 0):,}",
                },
            },
            "summary": {
                "total_value_inr": round(total_value, 0),
                "subscription_cost_inr": round(subscription_cost_inr, 0),
                "roi_multiple": round(roi_multiple, 1),
                "net_value_inr": round(total_value - subscription_cost_inr, 0),
            },
            "notes": [
                "Time savings based on 5 min avg per manual lookup",
                "Issue prevention valued conservatively at ₹25,000 each",
                "Actual rework costs typically range ₹50,000 - ₹5,00,000",
                "Documentation value (legal protection) not quantified",
            ],
        }
    
    def format_roi_report(
        self,
        project_id: str,
        project_name: str,
        period: str = "monthly",
    ) -> str:
        """Format ROI report for WhatsApp/dashboard"""
        roi = self.calculate_roi(project_id)
        m = roi["metrics"]
        s = roi["summary"]
        
        return f"""
**SiteMind ROI Report**
Project: {project_name}
Period: {period.title()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Queries Answered:     {m['queries_answered']}
Issues Caught:        {m['issues_flagged']}
Documents Processed:  {m['documents_processed']}
Decisions Logged:     {m['decisions_logged']}
Time Saved:          {m['time_saved_hours']} hours

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VALUE DELIVERED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Time Savings:         ₹{roi['value_calculation']['time_savings']['value_inr']:,.0f}
Issue Prevention:     ₹{roi['value_calculation']['issue_prevention']['value_inr']:,.0f}
─────────────────────────────────────────────
Total Value:          ₹{s['total_value_inr']:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROI SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subscription Cost:    ₹{s['subscription_cost_inr']:,.0f}
Net Value:           ₹{s['net_value_inr']:,.0f}
ROI:                 {s['roi_multiple']}x

_Calculation methodology available on request._
"""


# Singleton instance
roi_service = ROIService()
