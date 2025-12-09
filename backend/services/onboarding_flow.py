"""
SiteMind Onboarding Flow
========================

THE FIRST HOUR EXPERIENCE

Goal: Customer says "WOW" within 60 minutes
Goal: Product feels worth $1000/month from minute 1

TIMELINE:
- Minute 0-5: Professional welcome
- Minute 5-15: First drawing upload → AI extracts specs LIVE
- Minute 15-30: First question → Answered with citations
- Minute 30-45: First photo → Cross-referenced in real-time
- Minute 45-60: Dashboard tour → See their data, ROI potential

Every interaction should feel: INTELLIGENT, PROFESSIONAL, VALUABLE
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from services.memory_service import memory_service
from services.connected_intelligence import connected_intelligence
from services.whatsapp_service import whatsapp_service
from utils.logger import logger


@dataclass
class OnboardingState:
    """Track onboarding progress for a company"""
    company_id: str
    company_name: str
    admin_phone: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    # Progress tracking
    welcome_sent: bool = False
    first_drawing_uploaded: bool = False
    specs_extracted: int = 0
    first_question_asked: bool = False
    first_photo_analyzed: bool = False
    dashboard_introduced: bool = False
    
    # Engagement
    total_messages: int = 0
    wow_moments: int = 0  # Times we impressed them


class OnboardingService:
    """
    First Hour Experience Manager
    
    Makes customers say WOW within 60 minutes.
    """
    
    def __init__(self):
        self._states: Dict[str, OnboardingState] = {}
    
    # =========================================================================
    # WELCOME - Minute 0-5
    # =========================================================================
    
    async def start_onboarding(
        self,
        company_id: str,
        company_name: str,
        admin_phone: str,
        admin_name: str,
    ) -> str:
        """
        Send the WOW welcome message
        
        This sets the tone. Professional. Intelligent. Valuable.
        """
        
        # Create state
        state = OnboardingState(
            company_id=company_id,
            company_name=company_name,
            admin_phone=admin_phone,
        )
        self._states[company_id] = state
        
        # THE WELCOME MESSAGE - Sets expectations HIGH
        welcome = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 *Welcome to SiteMind, {admin_name}!*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your Project Brain for *{company_name}* is now active.

I'm an AI construction expert that will:
✅ Remember every drawing, spec, and decision
✅ Cross-reference site photos against specs
✅ Catch expensive mistakes before they happen
✅ Answer any question with citations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 *LET'S GET YOU SET UP (5 minutes)*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*Step 1:* Send me ONE structural drawing (PDF or photo)
         I'll extract all the specs automatically.

*Step 2:* Ask me any question about it
         I'll answer with citations.

*Step 3:* Send a site photo
         I'll cross-reference against the specs.

Ready? *Send your first drawing now* 📐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_Your dedicated dashboard: sitemind.ai/dashboard_
_Support: Direct reply here anytime_
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        state.welcome_sent = True
        await whatsapp_service.send_message(admin_phone, welcome)
        
        logger.info(f"🎉 Onboarding started for {company_name}")
        return welcome
    
    # =========================================================================
    # FIRST DRAWING - Minute 5-15 (THE BIG WOW)
    # =========================================================================
    
    async def handle_first_drawing(
        self,
        company_id: str,
        project_id: str,
        document_name: str,
        specs_extracted: List[Dict],
        phone: str,
    ) -> str:
        """
        After first drawing upload - IMPRESSIVE response
        
        This is THE WOW MOMENT. Show them the AI is SMART.
        """
        
        state = self._states.get(company_id)
        if state:
            state.first_drawing_uploaded = True
            state.specs_extracted = len(specs_extracted)
            state.wow_moments += 1
        
        # Format specs beautifully
        specs_display = []
        for i, spec in enumerate(specs_extracted[:8], 1):  # Show first 8
            element = spec.get("element", "Unknown")
            location = spec.get("location", "")
            details = spec.get("details", {})
            
            detail_str = ", ".join(f"{k}: {v}" for k, v in list(details.items())[:3])
            specs_display.append(f"   {i}. *{element}* @ {location}\n      _{detail_str}_")
        
        specs_text = "\n".join(specs_display)
        more_text = f"\n   _...and {len(specs_extracted) - 8} more_" if len(specs_extracted) > 8 else ""
        
        # THE WOW RESPONSE
        response = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ *DRAWING PROCESSED*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 *{document_name}*

🔍 *I found {len(specs_extracted)} specifications:*

{specs_text}{more_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 *WHAT I CAN DO NOW:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Ask me: _"What's the column size at B2?"_
• Ask me: _"Rebar for beam on floor 3?"_
• Send a photo: _I'll verify against these specs_

*Try it now!* Ask any question about this drawing.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        await whatsapp_service.send_message(phone, response)
        logger.info(f"🎯 First drawing WOW delivered: {len(specs_extracted)} specs")
        
        return response
    
    # =========================================================================
    # FIRST QUESTION - Minute 15-30
    # =========================================================================
    
    async def format_first_answer(
        self,
        company_id: str,
        question: str,
        answer: str,
        citations: List[str],
        phone: str,
    ) -> str:
        """
        Format the first answer to be IMPRESSIVE
        
        Show citations prominently. Show the AI is smart.
        """
        
        state = self._states.get(company_id)
        if state and not state.first_question_asked:
            state.first_question_asked = True
            state.wow_moments += 1
        
        # Format citations
        citation_text = ""
        if citations:
            citation_text = "\n📎 *Source:* " + ", ".join(citations[:3])
        
        response = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 *YOUR QUESTION:*
_{question}_
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{answer}
{citation_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ *Notice how I cited the source?*
Every answer is traceable. No guessing.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*Next:* Send me a site photo and I'll cross-reference it against your specs!
"""
        
        return response
    
    # =========================================================================
    # FIRST PHOTO - Minute 30-45 (THE SECOND BIG WOW)
    # =========================================================================
    
    async def format_first_photo_analysis(
        self,
        company_id: str,
        analysis: str,
        matched_specs: List[str],
        has_mismatch: bool,
        mismatch_details: Dict = None,
        phone: str = None,
    ) -> str:
        """
        Format first photo analysis to be IMPRESSIVE
        
        Whether match or mismatch, show the cross-reference power.
        """
        
        state = self._states.get(company_id)
        if state and not state.first_photo_analyzed:
            state.first_photo_analyzed = True
            state.wow_moments += 1
        
        if has_mismatch:
            # MISMATCH - Show the value
            response = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 *MISMATCH DETECTED!*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 *VALUE DELIVERED*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If this had gone unnoticed until concrete pour:
• Estimated rework cost: *₹{mismatch_details.get('cost_lakh', '3-5')} Lakh*
• Delay: 2-5 days
• Quality impact: Significant

*SiteMind just paid for itself.* 🎯

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 View your dashboard: sitemind.ai/dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            # MATCH - Still show the cross-reference
            specs_checked = "\n".join([f"   ✓ {s}" for s in matched_specs[:5]])
            
            response = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ *PHOTO VERIFIED*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 *CROSS-REFERENCED AGAINST:*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{specs_checked}

*Everything matches specifications.* ✓
This verification is now on record.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *Every photo your team sends gets 
   cross-referenced automatically.*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return response
    
    # =========================================================================
    # DASHBOARD INTRO - Minute 45-60
    # =========================================================================
    
    async def send_dashboard_intro(
        self,
        company_id: str,
        company_name: str,
        phone: str,
        stats: Dict,
    ) -> str:
        """
        Introduce the dashboard after they've used WhatsApp
        """
        
        state = self._states.get(company_id)
        if state:
            state.dashboard_introduced = True
        
        response = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *YOUR SITEMIND DASHBOARD*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 *sitemind.ai/dashboard*

*What you'll see:*
• 📐 All {stats.get('specs', 0)} specifications stored
• 🔔 Mismatch alerts (if any)
• 📈 Value protected over time
• 📋 Audit trail of all decisions
• 💰 Usage & billing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 *ONBOARDING COMPLETE!*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your Project Brain is ready for *{company_name}*.

*What happens now:*
1. Add your team (they just message this number)
2. Upload more drawings for more coverage
3. Every site photo gets cross-referenced
4. Every question answered with citations

*Need help?* Just reply here anytime.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_Thank you for choosing SiteMind._
_We're excited to protect your projects._
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        await whatsapp_service.send_message(phone, response)
        logger.info(f"🎓 Onboarding complete for {company_name}")
        
        return response
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def get_onboarding_progress(self, company_id: str) -> Dict[str, Any]:
        """Get onboarding progress for analytics"""
        
        state = self._states.get(company_id)
        if not state:
            return {"status": "not_started"}
        
        steps_complete = sum([
            state.welcome_sent,
            state.first_drawing_uploaded,
            state.first_question_asked,
            state.first_photo_analyzed,
            state.dashboard_introduced,
        ])
        
        return {
            "status": "complete" if steps_complete >= 4 else "in_progress",
            "steps_complete": steps_complete,
            "total_steps": 5,
            "progress_percent": (steps_complete / 5) * 100,
            "specs_extracted": state.specs_extracted,
            "wow_moments": state.wow_moments,
            "started_at": state.started_at.isoformat(),
        }


# Singleton
onboarding_service = OnboardingService()

