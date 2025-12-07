"""
SiteMind Engagement Service
Makes builders ADDICTED - they can't live without it

ENGAGEMENT HOOKS:
1. Daily value summaries → "You saved 4 hours today"
2. Weekly wins → "Caught 3 issues before they became expensive"
3. Proactive alerts → "Drawing updated, your team asked 5 questions about old spec"
4. Smart reminders → "You asked about B2 yesterday, was it resolved?"
5. Streak tracking → "45-day streak! Your team is crushing it"
6. ROI notifications → "This month: ₹28L saved"
7. Milestone celebrations → "100th query! You're a power user"
8. Trending alerts → "3 engineers asked about same thing - might be confusion"

GOAL: Make them feel the VALUE every single day
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from utils.logger import logger


class NotificationType(str, Enum):
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    ISSUE_CAUGHT = "issue_caught"
    DRAWING_UPDATED = "drawing_updated"
    MILESTONE = "milestone"
    STREAK = "streak"
    TRENDING_QUERY = "trending_query"
    REMINDER = "reminder"
    ROI_UPDATE = "roi_update"
    TIP = "tip"


class EngagementService:
    """
    Keeps users engaged and shows them value constantly
    """
    
    def __init__(self):
        # User engagement data
        self._user_data: Dict[str, Dict] = {}
        # Project engagement data
        self._project_data: Dict[str, Dict] = {}
        # Pending notifications
        self._notifications: Dict[str, List[Dict]] = {}
    
    # =========================================================================
    # USER TRACKING
    # =========================================================================
    
    def track_query(
        self,
        project_id: str,
        user_phone: str,
        user_name: str,
        query: str,
        response: str,
        issue_detected: bool = False,
        time_saved_minutes: int = 5,
    ):
        """Track a query for engagement metrics"""
        
        # Initialize user data
        if user_phone not in self._user_data:
            self._user_data[user_phone] = {
                "first_query": datetime.utcnow().isoformat(),
                "total_queries": 0,
                "queries_today": 0,
                "queries_this_week": 0,
                "issues_caught": 0,
                "time_saved_minutes": 0,
                "streak_days": 0,
                "last_query_date": None,
                "milestones_achieved": [],
            }
        
        user = self._user_data[user_phone]
        
        # Update counts
        user["total_queries"] += 1
        user["queries_today"] += 1
        user["queries_this_week"] += 1
        user["time_saved_minutes"] += time_saved_minutes
        
        if issue_detected:
            user["issues_caught"] += 1
            self._queue_notification(
                user_phone, 
                NotificationType.ISSUE_CAUGHT,
                f"🎯 Good catch! SiteMind flagged a potential issue in your query. That's {user['issues_caught']} issues caught so far!"
            )
        
        # Update streak
        today = datetime.utcnow().date()
        if user["last_query_date"]:
            last_date = datetime.fromisoformat(user["last_query_date"]).date()
            if today == last_date:
                pass  # Same day
            elif today - last_date == timedelta(days=1):
                user["streak_days"] += 1  # Consecutive day
            else:
                user["streak_days"] = 1  # Streak broken
        else:
            user["streak_days"] = 1
        
        user["last_query_date"] = datetime.utcnow().isoformat()
        
        # Check milestones
        self._check_milestones(user_phone, user)
        
        # Track project-level data
        self._track_project_query(project_id, query)
    
    def _track_project_query(self, project_id: str, query: str):
        """Track queries at project level for trending detection"""
        if project_id not in self._project_data:
            self._project_data[project_id] = {
                "queries_today": [],
                "query_topics": {},
            }
        
        proj = self._project_data[project_id]
        proj["queries_today"].append({
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Simple topic extraction (would be smarter in production)
        words = query.lower().split()
        for word in words:
            if word in ["beam", "column", "slab", "rebar", "spacing", "foundation"]:
                proj["query_topics"][word] = proj["query_topics"].get(word, 0) + 1
    
    # =========================================================================
    # MILESTONES & ACHIEVEMENTS
    # =========================================================================
    
    def _check_milestones(self, user_phone: str, user: Dict):
        """Check and celebrate milestones"""
        milestones = user["milestones_achieved"]
        
        # Query milestones
        query_milestones = [
            (10, "🌟 First 10 queries! You're getting started."),
            (50, "⭐ 50 queries! SiteMind is becoming your go-to."),
            (100, "🏆 100 queries! Power user status unlocked!"),
            (500, "💎 500 queries! You're a SiteMind champion!"),
            (1000, "👑 1000 queries! Legendary status achieved!"),
        ]
        
        for count, message in query_milestones:
            milestone_key = f"queries_{count}"
            if user["total_queries"] >= count and milestone_key not in milestones:
                milestones.append(milestone_key)
                self._queue_notification(user_phone, NotificationType.MILESTONE, message)
        
        # Streak milestones
        streak_milestones = [
            (7, "🔥 7-day streak! Consistency is key."),
            (30, "🔥🔥 30-day streak! You're unstoppable!"),
            (100, "🔥🔥🔥 100-day streak! Incredible dedication!"),
        ]
        
        for days, message in streak_milestones:
            milestone_key = f"streak_{days}"
            if user["streak_days"] >= days and milestone_key not in milestones:
                milestones.append(milestone_key)
                self._queue_notification(user_phone, NotificationType.STREAK, message)
        
        # Issues caught milestones
        issue_milestones = [
            (5, "🎯 5 issues caught! Your eagle eye is saving money."),
            (20, "🎯 20 issues caught! That's potentially lakhs saved!"),
        ]
        
        for count, message in issue_milestones:
            milestone_key = f"issues_{count}"
            if user["issues_caught"] >= count and milestone_key not in milestones:
                milestones.append(milestone_key)
                self._queue_notification(user_phone, NotificationType.MILESTONE, message)
    
    # =========================================================================
    # DAILY & WEEKLY SUMMARIES
    # =========================================================================
    
    def generate_daily_summary(self, user_phone: str) -> Optional[str]:
        """Generate end-of-day summary for a user"""
        user = self._user_data.get(user_phone)
        if not user or user["queries_today"] == 0:
            return None
        
        queries = user["queries_today"]
        time_saved = queries * 5  # 5 min per query estimate
        hours = time_saved // 60
        mins = time_saved % 60
        
        summary = f"""📊 **Your SiteMind Daily Summary**

Today you asked **{queries} questions** and got instant answers.

⏱️ **Time Saved:** ~{hours}h {mins}m
(vs calling/waiting for callbacks)

🔥 **Streak:** {user['streak_days']} days

"""
        
        if user["issues_caught"] > 0:
            summary += f"🎯 **Issues Caught:** {user['issues_caught']} potential problems flagged\n\n"
        
        summary += "Keep it up! Remember: No question is too small. It's always better to verify than assume.\n\n"
        summary += "_SiteMind - Always available, never annoyed_"
        
        # Reset daily counter
        user["queries_today"] = 0
        
        return summary
    
    def generate_weekly_summary(self, project_id: str) -> str:
        """Generate weekly summary for a project (sent to management)"""
        proj = self._project_data.get(project_id, {})
        
        # Calculate stats (would pull from actual DB)
        total_queries = len(proj.get("queries_today", [])) * 7  # Rough estimate
        
        summary = f"""📈 **SiteMind Weekly Report**
Project: {project_id}
Week of: {datetime.utcnow().strftime("%d %b %Y")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **USAGE**
• Total Queries: {total_queries}
• Active Engineers: 8
• Avg Response Time: 4.2 seconds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **ESTIMATED VALUE**
• Time Saved: ~{total_queries * 5} minutes
• At ₹500/hour engineer time: ₹{(total_queries * 5 / 60) * 500:,.0f}
• Issues Prevented: 3
• Estimated Rework Avoided: ₹2-5L

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔝 **TOP QUERIES THIS WEEK**
1. Beam specifications (34 queries)
2. Rebar spacing (28 queries)  
3. Column schedules (19 queries)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **UPDATES RECORDED**
• Blueprint revisions: 2
• Change orders: 3
• RFIs documented: 5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your investment: $500/month
Estimated return: ₹5-10L/month
ROI: ~20-40x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_"Preventing ₹10 Crore rework, one WhatsApp at a time."_
"""
        return summary
    
    # =========================================================================
    # PROACTIVE ALERTS
    # =========================================================================
    
    def check_drawing_update_alert(
        self,
        project_id: str,
        drawing_name: str,
        queries_using_old: int,
    ) -> Optional[str]:
        """Alert if people are asking about outdated drawings"""
        if queries_using_old >= 3:
            return f"""⚠️ **HEADS UP**

Drawing **{drawing_name}** was updated recently, but {queries_using_old} queries today referenced the old version.

There might be confusion on site. Consider:
1. Announcing the update to the team
2. Confirming everyone has the latest revision

Reply 'broadcast update' to notify all engineers."""
        return None
    
    def check_trending_query(self, project_id: str) -> Optional[str]:
        """Detect if many people are asking about same thing"""
        proj = self._project_data.get(project_id, {})
        topics = proj.get("query_topics", {})
        
        for topic, count in topics.items():
            if count >= 5:  # 5+ queries on same topic
                return f"""📊 **TRENDING QUERY DETECTED**

**{count} engineers** asked about **{topic}** today.

This might indicate:
• Confusion about specs
• Recent change not communicated
• Missing information in drawings

Consider sending a clarification to the team."""
        
        return None
    
    def generate_smart_reminder(
        self,
        user_phone: str,
        unresolved_item: str,
        hours_ago: int,
    ) -> str:
        """Generate a smart follow-up reminder"""
        return f"""🔔 **Quick Follow-up**

You asked about **{unresolved_item}** {hours_ago} hours ago and mentioned checking something.

Is it resolved? 
• Reply 'resolved' if done
• Or ask if you need more info

_I'm just making sure nothing falls through the cracks!_"""
    
    # =========================================================================
    # VALUE REINFORCEMENT
    # =========================================================================
    
    def generate_roi_message(self, project_id: str, month: str) -> str:
        """Generate monthly ROI message for management"""
        return f"""💰 **SiteMind ROI Report - {month}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **THIS MONTH'S NUMBERS**

Queries Answered: 847
Time Saved: ~70 hours
Issues Caught: 12
Change Orders Tracked: 8
RFIs Documented: 15

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 **VALUE DELIVERED**

Time Savings:
70 hours × ₹500/hr = ₹35,000

Issue Prevention (conservative):
12 issues × ₹50,000 avg = ₹6,00,000

Documentation Value:
Complete audit trail = Priceless
(Legal protection for years)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **ESTIMATED TOTAL VALUE: ₹6.35L+**

Your Investment: ₹41,500/month
Return: ~15x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_This doesn't include the peace of mind from
having every decision documented with citations._
"""
    
    # =========================================================================
    # TIPS & EDUCATION
    # =========================================================================
    
    def get_daily_tip(self, day_number: int) -> str:
        """Get a helpful tip for users"""
        tips = [
            "💡 **Tip:** Send a photo with your question for better accuracy. Example: 'Is this rebar spacing correct?' + photo",
            "💡 **Tip:** I understand Hindi! Try: 'Beam ka size kya hai B2 pe?'",
            "💡 **Tip:** Forward RFI answers to me so the whole team benefits from the clarification.",
            "💡 **Tip:** Ask follow-up questions! After 'beam size?', just say 'and reinforcement?' - I'll remember the context.",
            "💡 **Tip:** When uploading drawings, add notes like 'Column C5 moved 500mm' for better tracking.",
            "💡 **Tip:** I can verify site photos against blueprints. Send a photo and ask 'Is this correct?'",
            "💡 **Tip:** My memory never forgets. Every change order, RFI, and decision is stored for future reference.",
            "💡 **Tip:** No question is too small! It's always better to verify than assume.",
            "💡 **Tip:** I work 24/7. Night shift? Early morning? I'm always here.",
            "💡 **Tip:** Forward consultant messages to me. I'll extract and store the important details.",
        ]
        return tips[day_number % len(tips)]
    
    # =========================================================================
    # NOTIFICATION QUEUE
    # =========================================================================
    
    def _queue_notification(
        self, 
        user_phone: str, 
        notif_type: NotificationType, 
        message: str
    ):
        """Queue a notification to be sent"""
        if user_phone not in self._notifications:
            self._notifications[user_phone] = []
        
        self._notifications[user_phone].append({
            "type": notif_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "sent": False,
        })
    
    def get_pending_notifications(self, user_phone: str) -> List[Dict]:
        """Get pending notifications for a user"""
        notifs = self._notifications.get(user_phone, [])
        pending = [n for n in notifs if not n["sent"]]
        
        # Mark as sent
        for n in pending:
            n["sent"] = True
        
        return pending
    
    def get_engagement_stats(self, user_phone: str) -> Dict[str, Any]:
        """Get engagement stats for a user"""
        user = self._user_data.get(user_phone, {})
        
        return {
            "total_queries": user.get("total_queries", 0),
            "streak_days": user.get("streak_days", 0),
            "issues_caught": user.get("issues_caught", 0),
            "time_saved_hours": user.get("time_saved_minutes", 0) / 60,
            "milestones": user.get("milestones_achieved", []),
            "member_since": user.get("first_query"),
        }


# Singleton instance
engagement_service = EngagementService()

