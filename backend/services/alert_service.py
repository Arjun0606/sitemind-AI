"""
SiteMind Alert Service
Proactive notifications that make this indispensable

The difference between "nice to have" and "can't live without"
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from utils.logger import logger


class AlertType(Enum):
    """Alert types"""
    SAFETY = "safety"
    CONFLICT = "conflict"
    REMINDER = "reminder"
    MILESTONE = "milestone"
    WEATHER = "weather"
    DEADLINE = "deadline"
    INSIGHT = "insight"


class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert data"""
    id: str
    company_id: str
    project_id: Optional[str]
    
    alert_type: AlertType
    priority: AlertPriority
    
    title: str
    message: str
    action_required: Optional[str] = None
    
    created_at: str = ""
    sent: bool = False
    sent_at: Optional[str] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None


class AlertService:
    """
    Proactive alert system
    
    Alert types:
    1. Safety - Immediate safety concerns
    2. Conflict - Design/spec conflicts detected
    3. Reminder - Task/deadline reminders
    4. Milestone - Project milestones reached
    5. Weather - Weather-based alerts
    6. Deadline - Approaching deadlines
    7. Insight - AI-generated insights
    """
    
    def __init__(self):
        # Alert storage
        self._alerts: Dict[str, Alert] = {}
        self._alert_counter = 0
        
        # Alert templates
        self.TEMPLATES = {
            AlertType.SAFETY: {
                "icon": "🚨",
                "prefix": "SAFETY ALERT",
            },
            AlertType.CONFLICT: {
                "icon": "⚠️",
                "prefix": "CONFLICT DETECTED",
            },
            AlertType.REMINDER: {
                "icon": "⏰",
                "prefix": "REMINDER",
            },
            AlertType.MILESTONE: {
                "icon": "🎉",
                "prefix": "MILESTONE",
            },
            AlertType.WEATHER: {
                "icon": "🌧️",
                "prefix": "WEATHER ALERT",
            },
            AlertType.DEADLINE: {
                "icon": "📅",
                "prefix": "DEADLINE",
            },
            AlertType.INSIGHT: {
                "icon": "💡",
                "prefix": "INSIGHT",
            },
        }
    
    # =========================================================================
    # CREATE ALERTS
    # =========================================================================
    
    def create_alert(
        self,
        company_id: str,
        alert_type: AlertType,
        priority: AlertPriority,
        title: str,
        message: str,
        project_id: str = None,
        action_required: str = None,
    ) -> Alert:
        """Create a new alert"""
        self._alert_counter += 1
        alert_id = f"alert_{self._alert_counter}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        alert = Alert(
            id=alert_id,
            company_id=company_id,
            project_id=project_id,
            alert_type=alert_type,
            priority=priority,
            title=title,
            message=message,
            action_required=action_required,
            created_at=datetime.utcnow().isoformat(),
        )
        
        self._alerts[alert_id] = alert
        
        logger.info(f"🔔 Alert created: [{priority.value.upper()}] {title}")
        
        return alert
    
    # =========================================================================
    # QUICK ALERT CREATORS
    # =========================================================================
    
    def safety_alert(
        self,
        company_id: str,
        project_id: str,
        issue: str,
        recommendation: str,
    ) -> Alert:
        """Create safety alert"""
        return self.create_alert(
            company_id=company_id,
            project_id=project_id,
            alert_type=AlertType.SAFETY,
            priority=AlertPriority.CRITICAL,
            title="Safety Issue Detected",
            message=issue,
            action_required=recommendation,
        )
    
    def conflict_alert(
        self,
        company_id: str,
        project_id: str,
        conflict_description: str,
    ) -> Alert:
        """Create conflict alert"""
        return self.create_alert(
            company_id=company_id,
            project_id=project_id,
            alert_type=AlertType.CONFLICT,
            priority=AlertPriority.HIGH,
            title="Potential Conflict Detected",
            message=conflict_description,
            action_required="Please review and confirm with architect/engineer",
        )
    
    def insight_alert(
        self,
        company_id: str,
        project_id: str,
        insight: str,
    ) -> Alert:
        """Create insight alert"""
        return self.create_alert(
            company_id=company_id,
            project_id=project_id,
            alert_type=AlertType.INSIGHT,
            priority=AlertPriority.LOW,
            title="AI Insight",
            message=insight,
        )
    
    def reminder_alert(
        self,
        company_id: str,
        project_id: str,
        reminder: str,
        action: str = None,
    ) -> Alert:
        """Create reminder alert"""
        return self.create_alert(
            company_id=company_id,
            project_id=project_id,
            alert_type=AlertType.REMINDER,
            priority=AlertPriority.MEDIUM,
            title="Reminder",
            message=reminder,
            action_required=action,
        )
    
    # =========================================================================
    # GET ALERTS
    # =========================================================================
    
    def get_pending_alerts(
        self,
        company_id: str,
        project_id: str = None,
        priority: AlertPriority = None,
    ) -> List[Alert]:
        """Get pending (unsent) alerts"""
        alerts = [
            a for a in self._alerts.values()
            if a.company_id == company_id and not a.sent
        ]
        
        if project_id:
            alerts = [a for a in alerts if a.project_id == project_id]
        
        if priority:
            alerts = [a for a in alerts if a.priority == priority]
        
        # Sort by priority (critical first)
        priority_order = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.LOW: 3,
        }
        
        alerts.sort(key=lambda a: priority_order.get(a.priority, 99))
        
        return alerts
    
    def get_alert_count(self, company_id: str) -> Dict[str, int]:
        """Get alert counts by priority"""
        alerts = [a for a in self._alerts.values() if a.company_id == company_id and not a.sent]
        
        return {
            "critical": len([a for a in alerts if a.priority == AlertPriority.CRITICAL]),
            "high": len([a for a in alerts if a.priority == AlertPriority.HIGH]),
            "medium": len([a for a in alerts if a.priority == AlertPriority.MEDIUM]),
            "low": len([a for a in alerts if a.priority == AlertPriority.LOW]),
            "total": len(alerts),
        }
    
    # =========================================================================
    # MARK ALERTS
    # =========================================================================
    
    def mark_sent(self, alert_id: str):
        """Mark alert as sent"""
        if alert_id in self._alerts:
            self._alerts[alert_id].sent = True
            self._alerts[alert_id].sent_at = datetime.utcnow().isoformat()
    
    def mark_acknowledged(self, alert_id: str, user_id: str):
        """Mark alert as acknowledged"""
        if alert_id in self._alerts:
            self._alerts[alert_id].acknowledged = True
            self._alerts[alert_id].acknowledged_by = user_id
    
    # =========================================================================
    # FORMAT ALERTS
    # =========================================================================
    
    def format_alert_whatsapp(self, alert: Alert) -> str:
        """Format single alert for WhatsApp"""
        template = self.TEMPLATES.get(alert.alert_type, {"icon": "🔔", "prefix": "ALERT"})
        
        priority_indicator = ""
        if alert.priority == AlertPriority.CRITICAL:
            priority_indicator = "🔴 "
        elif alert.priority == AlertPriority.HIGH:
            priority_indicator = "🟠 "
        
        msg = f"""
{priority_indicator}{template['icon']} *{template['prefix']}*

*{alert.title}*

{alert.message}"""

        if alert.action_required:
            msg += f"""

📋 *Action Required:*
{alert.action_required}"""

        if alert.project_id:
            msg += f"""

_Project: {alert.project_id}_"""

        return msg
    
    def format_alert_summary(self, alerts: List[Alert]) -> str:
        """Format multiple alerts as summary"""
        if not alerts:
            return "✅ No pending alerts"
        
        counts = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.HIGH: 0,
            AlertPriority.MEDIUM: 0,
            AlertPriority.LOW: 0,
        }
        
        for a in alerts:
            counts[a.priority] += 1
        
        msg = """
🔔 *Alert Summary*

"""
        
        if counts[AlertPriority.CRITICAL] > 0:
            msg += f"🔴 {counts[AlertPriority.CRITICAL]} critical\n"
        if counts[AlertPriority.HIGH] > 0:
            msg += f"🟠 {counts[AlertPriority.HIGH]} high priority\n"
        if counts[AlertPriority.MEDIUM] > 0:
            msg += f"🟡 {counts[AlertPriority.MEDIUM]} medium\n"
        if counts[AlertPriority.LOW] > 0:
            msg += f"🟢 {counts[AlertPriority.LOW]} low\n"
        
        msg += f"\n*Total: {len(alerts)} alerts pending*"
        
        # Show top critical alerts
        critical = [a for a in alerts if a.priority == AlertPriority.CRITICAL]
        if critical:
            msg += "\n\n⚠️ *Critical Alerts:*"
            for a in critical[:3]:
                msg += f"\n• {a.title}"
        
        return msg


# Singleton
alert_service = AlertService()

