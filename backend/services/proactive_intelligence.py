"""
SiteMind Proactive Intelligence
The differentiator - tells you what you NEED to know before you ask

PROACTIVE FEATURES:
1. Morning Brief - Daily summary at 7 AM
2. Red Flag Alerts - Immediate notification of risks
3. Pattern Detection - "Many asking about X" = confusion
4. Deadline Reminders - Pending decisions, overdue tasks
5. Smart Follow-ups - "Was that issue resolved?"
6. Predictive Alerts - "Delay likely if..."
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from utils.logger import logger


class AlertPriority(str, Enum):
    CRITICAL = "critical"  # Immediate action needed
    HIGH = "high"          # Address today
    NORMAL = "normal"      # Informational
    LOW = "low"            # FYI


class AlertCategory(str, Enum):
    RED_FLAG = "red_flag"
    PENDING_DECISION = "pending_decision"
    OVERDUE_TASK = "overdue_task"
    MATERIAL_SHORTAGE = "material_shortage"
    PROGRESS_DELAY = "progress_delay"
    COMMUNICATION_GAP = "communication_gap"
    PATTERN_DETECTED = "pattern_detected"
    MILESTONE = "milestone"


class ProactiveIntelligenceService:
    """
    Generates proactive alerts and insights
    """
    
    def __init__(self):
        self._pending_decisions: Dict[str, List[Dict]] = {}
        self._query_patterns: Dict[str, Dict[str, int]] = {}
        self._unresolved_issues: Dict[str, List[Dict]] = {}
    
    # =========================================================================
    # MORNING BRIEF
    # =========================================================================
    
    def generate_morning_brief(
        self,
        project_id: str,
        project_name: str,
        recipient_role: str,  # pm, owner, site_engineer
        data: Dict[str, Any],
    ) -> str:
        """
        Generate personalized morning brief
        
        Sent automatically at 7 AM to relevant users
        """
        brief = f"""**Good morning. Here's your SiteMind brief for {project_name}.**
_{datetime.utcnow().strftime("%A, %d %B %Y")}_

"""
        
        # Critical items first
        critical_items = data.get("critical_items", [])
        if critical_items:
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            brief += "🚨 **REQUIRES IMMEDIATE ATTENTION**\n"
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for item in critical_items:
                brief += f"• {item['title']}\n  {item['description']}\n\n"
        
        # Red flags
        red_flags = data.get("red_flags", [])
        if red_flags:
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            brief += f"🚩 **RED FLAGS ({len(red_flags)})**\n"
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for flag in red_flags[:3]:  # Top 3
                brief += f"• **{flag['severity'].upper()}**: {flag['title']}\n"
                brief += f"  {flag['description'][:100]}...\n\n"
        
        # Pending decisions
        pending = data.get("pending_decisions", [])
        if pending:
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            brief += f"⏳ **PENDING DECISIONS ({len(pending)})**\n"
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for item in pending[:5]:
                days_pending = item.get('days_pending', 0)
                urgent = " ⚠️" if days_pending > 3 else ""
                brief += f"• {item['title']}{urgent}\n"
                brief += f"  Waiting since {days_pending} days\n\n"
        
        # Today's milestones
        milestones = data.get("todays_milestones", [])
        if milestones:
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            brief += "📊 **TODAY'S MILESTONES**\n"
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for ms in milestones:
                brief += f"• {ms['name']} ({ms['location']})\n"
        
        # Material alerts
        material_alerts = data.get("material_alerts", [])
        if material_alerts:
            brief += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            brief += "📦 **MATERIAL ALERTS**\n"
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            for alert in material_alerts:
                critical = "🚨 " if alert.get('critical') else "⚠️ "
                brief += f"{critical}{alert['material']}: {alert['stock']} {alert['unit']} remaining\n"
        
        # Quick stats (for PM/Owner)
        if recipient_role in ["pm", "owner"]:
            stats = data.get("stats", {})
            brief += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            brief += "📈 **YESTERDAY'S ACTIVITY**\n"
            brief += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            brief += f"• Queries answered: {stats.get('queries', 0)}\n"
            brief += f"• Documents uploaded: {stats.get('documents', 0)}\n"
            brief += f"• Tasks completed: {stats.get('tasks_completed', 0)}\n"
            brief += f"• Issues flagged: {stats.get('issues', 0)}\n"
        
        brief += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        brief += "_Reply with any query or 'details [item]' for more info_"
        
        return brief
    
    # =========================================================================
    # PATTERN DETECTION
    # =========================================================================
    
    def record_query_topic(self, project_id: str, topic: str):
        """Record a query topic for pattern detection"""
        if project_id not in self._query_patterns:
            self._query_patterns[project_id] = {}
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"{today}:{topic}"
        
        self._query_patterns[project_id][key] = \
            self._query_patterns[project_id].get(key, 0) + 1
    
    def detect_confusion_pattern(self, project_id: str) -> Optional[Dict]:
        """Detect if many people asking about same thing"""
        patterns = self._query_patterns.get(project_id, {})
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        for key, count in patterns.items():
            if key.startswith(today) and count >= 5:
                topic = key.split(":")[1]
                return {
                    "category": AlertCategory.PATTERN_DETECTED,
                    "priority": AlertPriority.HIGH,
                    "title": f"Multiple queries about '{topic}'",
                    "description": f"{count} queries today about this topic. Possible confusion or unclear specification.",
                    "recommended_action": "Review specification clarity. Consider sending clarification to team.",
                }
        
        return None
    
    # =========================================================================
    # SMART FOLLOW-UPS
    # =========================================================================
    
    def record_issue(self, project_id: str, issue_id: str, description: str):
        """Record an issue for follow-up tracking"""
        if project_id not in self._unresolved_issues:
            self._unresolved_issues[project_id] = []
        
        self._unresolved_issues[project_id].append({
            "issue_id": issue_id,
            "description": description,
            "reported_at": datetime.utcnow().isoformat(),
            "follow_up_sent": False,
        })
    
    def get_followup_reminders(self, project_id: str) -> List[Dict]:
        """Get issues that need follow-up"""
        issues = self._unresolved_issues.get(project_id, [])
        reminders = []
        
        for issue in issues:
            if issue["follow_up_sent"]:
                continue
            
            reported = datetime.fromisoformat(issue["reported_at"])
            days_ago = (datetime.utcnow() - reported).days
            
            if days_ago >= 2:  # Follow up after 2 days
                reminders.append({
                    "category": AlertCategory.RED_FLAG,
                    "priority": AlertPriority.NORMAL,
                    "title": "Issue follow-up needed",
                    "description": f"Issue reported {days_ago} days ago: {issue['description'][:100]}",
                    "question": "Has this been resolved?",
                })
                issue["follow_up_sent"] = True
        
        return reminders
    
    # =========================================================================
    # DEADLINE TRACKING
    # =========================================================================
    
    def record_pending_decision(
        self,
        project_id: str,
        decision_id: str,
        title: str,
        waiting_from: str,
    ):
        """Record a pending decision"""
        if project_id not in self._pending_decisions:
            self._pending_decisions[project_id] = []
        
        self._pending_decisions[project_id].append({
            "decision_id": decision_id,
            "title": title,
            "waiting_from": waiting_from,
            "recorded_at": datetime.utcnow().isoformat(),
        })
    
    def get_pending_decision_alerts(self, project_id: str) -> List[Dict]:
        """Get alerts for pending decisions"""
        decisions = self._pending_decisions.get(project_id, [])
        alerts = []
        
        for decision in decisions:
            recorded = datetime.fromisoformat(decision["recorded_at"])
            days_pending = (datetime.utcnow() - recorded).days
            
            if days_pending >= 3:
                priority = AlertPriority.HIGH if days_pending >= 5 else AlertPriority.NORMAL
                
                alerts.append({
                    "category": AlertCategory.PENDING_DECISION,
                    "priority": priority,
                    "title": decision["title"],
                    "description": f"Waiting for {decision['waiting_from']} since {days_pending} days",
                    "days_pending": days_pending,
                })
        
        return alerts
    
    # =========================================================================
    # PREDICTIVE ALERTS
    # =========================================================================
    
    def generate_predictive_alerts(
        self,
        project_id: str,
        progress_data: Dict,
        material_data: Dict,
    ) -> List[Dict]:
        """Generate predictive alerts based on data"""
        alerts = []
        
        # Delay prediction
        delays = progress_data.get("predicted_delays", [])
        for delay in delays:
            alerts.append({
                "category": AlertCategory.PROGRESS_DELAY,
                "priority": AlertPriority.HIGH,
                "title": f"Predicted delay: {delay['milestone']}",
                "description": f"Based on current progress rate, {delay['milestone']} may be delayed by {delay['days']} days.",
                "recommended_action": "Consider adding resources or adjusting timeline.",
            })
        
        # Material shortage prediction
        low_stock = material_data.get("low_stock", [])
        for item in low_stock:
            days_remaining = item.get("days_remaining", 0)
            if days_remaining <= 3:
                alerts.append({
                    "category": AlertCategory.MATERIAL_SHORTAGE,
                    "priority": AlertPriority.CRITICAL if days_remaining <= 1 else AlertPriority.HIGH,
                    "title": f"Material shortage imminent: {item['material']}",
                    "description": f"Only {days_remaining} days of stock remaining at current consumption rate.",
                    "recommended_action": "Place order immediately to avoid work stoppage.",
                })
        
        return alerts
    
    # =========================================================================
    # COMMUNICATION GAP DETECTION
    # =========================================================================
    
    def detect_communication_gaps(
        self,
        project_id: str,
        sync_data: Dict,
    ) -> List[Dict]:
        """Detect communication gaps"""
        alerts = []
        
        # Unacknowledged drawings
        unack_drawings = sync_data.get("unacknowledged_drawings", [])
        for drawing in unack_drawings:
            if drawing.get("hours_since_upload", 0) >= 24:
                alerts.append({
                    "category": AlertCategory.COMMUNICATION_GAP,
                    "priority": AlertPriority.HIGH,
                    "title": f"Drawing not acknowledged: {drawing['name']}",
                    "description": f"Uploaded {drawing['hours_since_upload']} hours ago. {drawing['pending_count']} recipients haven't acknowledged.",
                    "recommended_action": "Follow up with team to ensure drawing is received.",
                })
        
        # Users not active
        inactive_users = sync_data.get("inactive_users", [])
        for user in inactive_users:
            if user.get("days_inactive", 0) >= 3:
                alerts.append({
                    "category": AlertCategory.COMMUNICATION_GAP,
                    "priority": AlertPriority.NORMAL,
                    "title": f"User inactive: {user['name']}",
                    "description": f"No activity in {user['days_inactive']} days.",
                    "recommended_action": "Verify user still has site access and is using SiteMind.",
                })
        
        return alerts
    
    # =========================================================================
    # AGGREGATED ALERTS
    # =========================================================================
    
    def get_all_alerts(
        self,
        project_id: str,
        include_low_priority: bool = False,
    ) -> List[Dict]:
        """Get all current alerts for a project"""
        alerts = []
        
        # Confusion patterns
        confusion = self.detect_confusion_pattern(project_id)
        if confusion:
            alerts.append(confusion)
        
        # Pending decisions
        alerts.extend(self.get_pending_decision_alerts(project_id))
        
        # Follow-up reminders
        alerts.extend(self.get_followup_reminders(project_id))
        
        # Sort by priority
        priority_order = ["critical", "high", "normal", "low"]
        alerts.sort(key=lambda x: priority_order.index(x.get("priority", "normal")))
        
        if not include_low_priority:
            alerts = [a for a in alerts if a.get("priority") != "low"]
        
        return alerts
    
    def format_alert_for_whatsapp(self, alert: Dict) -> str:
        """Format an alert for WhatsApp delivery"""
        priority_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "normal": "ℹ️",
            "low": "📝",
        }
        
        emoji = priority_emoji.get(alert.get("priority", "normal"), "ℹ️")
        
        msg = f"{emoji} **{alert['title']}**\n\n"
        msg += f"{alert['description']}\n"
        
        if alert.get("recommended_action"):
            msg += f"\n**Recommended:** {alert['recommended_action']}"
        
        if alert.get("question"):
            msg += f"\n\n_{alert['question']}_"
        
        return msg


# Singleton instance
proactive_intelligence = ProactiveIntelligenceService()

