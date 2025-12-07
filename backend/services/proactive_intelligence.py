"""
SiteMind Proactive Intelligence Service
AI that thinks ahead - not just reactive

FEATURES:
- Morning briefs
- Predictive alerts
- Pattern detection
- Recommendations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Insight:
    id: str
    project_id: str
    insight_type: str  # pattern, prediction, recommendation
    title: str
    description: str
    priority: str  # high, medium, low
    created_at: str
    dismissed: bool = False


class ProactiveIntelligenceService:
    """
    Generate proactive insights
    """
    
    def __init__(self):
        self._insights: Dict[str, List[Insight]] = {}  # project_id -> insights
        self._issues: Dict[str, List[Dict]] = {}  # project_id -> issues
        self._patterns: Dict[str, Dict] = {}  # project_id -> detected patterns
    
    # =========================================================================
    # ISSUE TRACKING (for pattern detection)
    # =========================================================================
    
    def record_issue(
        self,
        project_id: str,
        issue_type: str,
        description: str,
        location: str = None,
    ):
        """Record an issue for pattern analysis"""
        if project_id not in self._issues:
            self._issues[project_id] = []
        
        self._issues[project_id].append({
            "type": issue_type,
            "description": description,
            "location": location,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    # =========================================================================
    # INSIGHT GENERATION
    # =========================================================================
    
    def generate_insights(self, project_id: str) -> List[Insight]:
        """Generate insights based on project data"""
        insights = []
        
        # Pattern detection
        patterns = self._detect_patterns(project_id)
        for pattern in patterns:
            insights.append(self._create_insight(
                project_id=project_id,
                insight_type="pattern",
                title=pattern["title"],
                description=pattern["description"],
                priority=pattern["priority"],
            ))
        
        return insights
    
    def _detect_patterns(self, project_id: str) -> List[Dict]:
        """Detect patterns in project data"""
        patterns = []
        issues = self._issues.get(project_id, [])
        
        if not issues:
            return patterns
        
        # Count issues by type
        by_type = defaultdict(list)
        for issue in issues[-30:]:  # Last 30 issues
            by_type[issue["type"]].append(issue)
        
        # Check for repeated issues
        for issue_type, type_issues in by_type.items():
            if len(type_issues) >= 3:
                patterns.append({
                    "title": f"Recurring {issue_type.title()} Issues",
                    "description": f"There have been {len(type_issues)} {issue_type} issues recently. Consider reviewing root cause.",
                    "priority": "high" if len(type_issues) >= 5 else "medium",
                })
        
        # Check for location clustering
        by_location = defaultdict(list)
        for issue in issues:
            if issue.get("location"):
                by_location[issue["location"]].append(issue)
        
        for location, loc_issues in by_location.items():
            if len(loc_issues) >= 3:
                patterns.append({
                    "title": f"Multiple Issues at {location}",
                    "description": f"{len(loc_issues)} issues reported at {location}. Consider site inspection.",
                    "priority": "medium",
                })
        
        return patterns
    
    def _create_insight(
        self,
        project_id: str,
        insight_type: str,
        title: str,
        description: str,
        priority: str,
    ) -> Insight:
        """Create and store an insight"""
        insight = Insight(
            id=f"insight_{datetime.utcnow().timestamp():.0f}",
            project_id=project_id,
            insight_type=insight_type,
            title=title,
            description=description,
            priority=priority,
            created_at=datetime.utcnow().isoformat(),
        )
        
        if project_id not in self._insights:
            self._insights[project_id] = []
        self._insights[project_id].append(insight)
        
        return insight
    
    # =========================================================================
    # MORNING BRIEF
    # =========================================================================
    
    def generate_morning_brief(
        self,
        project_id: str,
        project_name: str,
        weather: Dict = None,
        tasks: List[Dict] = None,
        milestones: List[Dict] = None,
        low_stock: List[Dict] = None,
        red_flags: List[Dict] = None,
    ) -> str:
        """Generate comprehensive morning brief"""
        now = datetime.utcnow()
        
        brief = f"""☀️ **Good Morning!**

**Daily Brief** - {project_name}
{now.strftime("%A, %B %d, %Y")}

"""

        # Weather (if available)
        if weather:
            brief += f"🌤️ Weather: {weather.get('description', 'Clear')}, {weather.get('temp', '--')}°C\n\n"
        
        # Red flags first
        if red_flags:
            brief += "🚨 **Attention Required:**\n"
            for flag in red_flags[:3]:
                brief += f"• {flag.get('title', 'Issue')}\n"
            brief += "\n"
        
        # Tasks
        if tasks:
            pending = [t for t in tasks if t.get("status") == "pending"]
            brief += f"📋 **Today's Tasks ({len(pending)}):**\n"
            for task in pending[:5]:
                brief += f"• {task.get('title', 'Task')}"
                if task.get("assigned_to"):
                    brief += f" → {task['assigned_to']}"
                brief += "\n"
            brief += "\n"
        
        # Milestones
        if milestones:
            brief += "🎯 **Upcoming Milestones:**\n"
            for ms in milestones[:3]:
                days = ms.get("days_remaining", "?")
                brief += f"• {ms.get('name', 'Milestone')} ({days} days)\n"
            brief += "\n"
        
        # Low stock
        if low_stock:
            brief += "📦 **Low Stock Alert:**\n"
            for item in low_stock[:3]:
                brief += f"• {item.get('name', 'Material')}: {item.get('quantity', 0)} {item.get('unit', '')}\n"
            brief += "\n"
        
        # Insights
        insights = self.generate_insights(project_id)
        if insights:
            brief += "💡 **Insights:**\n"
            for insight in insights[:2]:
                brief += f"• {insight.title}\n"
            brief += "\n"
        
        brief += "_Reply with any question or 'help' for commands._"
        
        return brief
    
    # =========================================================================
    # QUERIES
    # =========================================================================
    
    def get_active_insights(self, project_id: str) -> List[Insight]:
        """Get non-dismissed insights"""
        insights = self._insights.get(project_id, [])
        return [i for i in insights if not i.dismissed]
    
    def dismiss_insight(self, project_id: str, insight_id: str):
        """Dismiss an insight"""
        insights = self._insights.get(project_id, [])
        for insight in insights:
            if insight.id == insight_id:
                insight.dismissed = True
                break
    
    def format_insight(self, insight: Insight) -> str:
        """Format insight for WhatsApp"""
        icons = {
            "pattern": "🔄",
            "prediction": "🔮",
            "recommendation": "💡",
        }
        
        icon = icons.get(insight.insight_type, "ℹ️")
        
        return f"""{icon} **{insight.title}**

{insight.description}

Priority: {insight.priority.upper()}

_Reply 'dismiss' to clear this insight._"""


# Singleton instance
proactive_intelligence = ProactiveIntelligenceService()
