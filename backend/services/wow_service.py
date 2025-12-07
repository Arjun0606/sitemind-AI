"""
SiteMind WOW Service
Features designed to create "holy shit" moments in Week 1

GOAL: Make them addicted in 7 days
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from utils.logger import logger


@dataclass
class UserStats:
    """Track user engagement for ROI"""
    user_id: str
    company_id: str
    first_query_at: datetime = None
    
    # Counts
    queries_answered: int = 0
    photos_analyzed: int = 0
    documents_processed: int = 0
    
    # Time saved estimates
    queries_time_saved_minutes: int = 0  # 5 min per query (vs calling architect)
    photos_time_saved_minutes: int = 0   # 10 min per photo (vs site visit)
    decisions_documented: int = 0         # Priceless for disputes
    
    # Wow moments
    memory_recalls: int = 0              # Times AI remembered context
    code_references: int = 0             # IS code citations
    safety_flags: int = 0                # Safety issues caught
    
    # Engagement
    days_active: set = field(default_factory=set)


class WowService:
    """
    Create addiction through value visibility
    """
    
    def __init__(self):
        self._stats: Dict[str, UserStats] = {}
        
        # Time saved estimates (conservative)
        self.MINUTES_PER_QUERY = 5      # vs calling someone
        self.MINUTES_PER_PHOTO = 10     # vs site visit to check
        self.MINUTES_PER_DOCUMENT = 30  # vs reading full document
        self.VALUE_PER_SAFETY_FLAG = 50000  # ₹50k per safety issue caught
    
    # =========================================================================
    # TRACK ENGAGEMENT
    # =========================================================================
    
    def track_query(self, user_id: str, company_id: str, had_code_reference: bool = False):
        """Track a query answered"""
        stats = self._get_stats(user_id, company_id)
        
        stats.queries_answered += 1
        stats.queries_time_saved_minutes += self.MINUTES_PER_QUERY
        stats.days_active.add(datetime.utcnow().date())
        
        if had_code_reference:
            stats.code_references += 1
    
    def track_photo(self, user_id: str, company_id: str):
        """Track photo analyzed"""
        stats = self._get_stats(user_id, company_id)
        
        stats.photos_analyzed += 1
        stats.photos_time_saved_minutes += self.MINUTES_PER_PHOTO
        stats.days_active.add(datetime.utcnow().date())
    
    def track_memory_recall(self, user_id: str, company_id: str):
        """Track when AI used memory (WOW moment!)"""
        stats = self._get_stats(user_id, company_id)
        stats.memory_recalls += 1
    
    def track_safety_flag(self, user_id: str, company_id: str):
        """Track safety issue caught"""
        stats = self._get_stats(user_id, company_id)
        stats.safety_flags += 1
    
    def track_decision(self, user_id: str, company_id: str):
        """Track decision documented"""
        stats = self._get_stats(user_id, company_id)
        stats.decisions_documented += 1
    
    def _get_stats(self, user_id: str, company_id: str) -> UserStats:
        """Get or create stats"""
        if user_id not in self._stats:
            self._stats[user_id] = UserStats(
                user_id=user_id,
                company_id=company_id,
                first_query_at=datetime.utcnow(),
            )
        return self._stats[user_id]
    
    # =========================================================================
    # ROI CALCULATION
    # =========================================================================
    
    def get_week1_roi(self, company_id: str) -> Dict[str, Any]:
        """Calculate Week 1 ROI for testimonial"""
        
        # Aggregate all users in company
        total_queries = 0
        total_photos = 0
        total_time_saved = 0
        total_memory_recalls = 0
        total_code_refs = 0
        total_safety_flags = 0
        total_decisions = 0
        active_users = set()
        
        for stats in self._stats.values():
            if stats.company_id == company_id:
                total_queries += stats.queries_answered
                total_photos += stats.photos_analyzed
                total_time_saved += (
                    stats.queries_time_saved_minutes + 
                    stats.photos_time_saved_minutes
                )
                total_memory_recalls += stats.memory_recalls
                total_code_refs += stats.code_references
                total_safety_flags += stats.safety_flags
                total_decisions += stats.decisions_documented
                active_users.add(stats.user_id)
        
        # Calculate value
        hours_saved = total_time_saved / 60
        engineer_hourly_rate = 500  # ₹500/hour
        time_value = hours_saved * engineer_hourly_rate
        
        safety_value = total_safety_flags * self.VALUE_PER_SAFETY_FLAG
        
        total_value = time_value + safety_value
        
        return {
            "period": "Week 1",
            "queries_answered": total_queries,
            "photos_analyzed": total_photos,
            "active_users": len(active_users),
            
            "hours_saved": round(hours_saved, 1),
            "time_value_inr": round(time_value),
            
            "memory_recalls": total_memory_recalls,
            "code_references": total_code_refs,
            "safety_flags": total_safety_flags,
            "safety_value_inr": safety_value,
            
            "decisions_documented": total_decisions,
            
            "total_value_inr": round(total_value),
            "total_value_usd": round(total_value / 83),
        }
    
    def format_week1_report(self, company_id: str, company_name: str) -> str:
        """Format Week 1 ROI report for WhatsApp"""
        roi = self.get_week1_roi(company_id)
        
        msg = f"""
🎉 *{company_name} - Week 1 with SiteMind*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *ACTIVITY*
• Questions answered: {roi['queries_answered']}
• Photos analyzed: {roi['photos_analyzed']}
• Active team members: {roi['active_users']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️ *TIME SAVED*
• {roi['hours_saved']} hours this week
• Worth ₹{roi['time_value_inr']:,} in engineer time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 *AI CAPABILITIES*
• Memory recalls: {roi['memory_recalls']} times
• IS code references: {roi['code_references']}
• Decisions documented: {roi['decisions_documented']}"""

        if roi['safety_flags'] > 0:
            msg += f"""

🚨 *SAFETY ISSUES CAUGHT*
• {roi['safety_flags']} potential issues flagged
• Estimated savings: ₹{roi['safety_value_inr']:,}"""

        msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *TOTAL VALUE DELIVERED*

    ₹{roi['total_value_inr']:,}
    
    (${roi['total_value_usd']} USD)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_This is Week 1. Imagine a full month._

SiteMind: Your site's AI brain 🏗️
"""
        return msg
    
    # =========================================================================
    # DAILY BRIEF
    # =========================================================================
    
    def get_daily_brief(self, company_id: str, company_name: str) -> str:
        """Generate morning brief"""
        roi = self.get_week1_roi(company_id)
        
        today = datetime.utcnow().strftime("%A, %B %d")
        
        return f"""
☀️ *Good Morning, {company_name}!*

*{today}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Yesterday's Activity*
• {roi['queries_answered']} questions answered
• {roi['photos_analyzed']} photos analyzed
• {roi['hours_saved']} hours saved so far

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *Tip of the Day*
Send me site photos for instant quality analysis!
Just click a photo and send - I'll analyze it in seconds.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Have a productive day! 🏗️

_Just reply to ask anything_
"""
    
    # =========================================================================
    # MEMORY FLEX
    # =========================================================================
    
    def format_memory_response(
        self,
        answer: str,
        recalled_context: List[str],
    ) -> str:
        """Add memory context to response (WOW factor)"""
        
        if not recalled_context:
            return answer
        
        # Add context reference
        context_note = "\n\n📝 _Based on previous discussions:_\n"
        for ctx in recalled_context[:2]:  # Max 2 references
            context_note += f"• _{ctx[:100]}..._\n"
        
        return answer + context_note
    
    # =========================================================================
    # TESTIMONIAL REQUEST
    # =========================================================================
    
    def get_testimonial_request(self, company_name: str) -> str:
        """Generate testimonial request message"""
        return f"""
🙏 *Quick Request, {company_name}*

You've been using SiteMind for a week now.

Would you mind sharing a quick 30-second testimonial?

Just answer:
1. What was your biggest frustration before?
2. How has SiteMind helped?
3. Would you recommend it?

You can send a voice note or video!

_This helps me show other builders what's possible._

Thank you! 🙏
"""


# Singleton
wow_service = WowService()

