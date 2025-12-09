"""
SiteMind First Hour WOW Experience
===================================

THE GOAL: Make customer feel they got a BARGAIN at $1000/month
within the FIRST HOUR of using SiteMind.

THE STRATEGY:
1. Premium welcome experience
2. Immediate AI demonstration
3. First "catch" within 30 minutes
4. ROI shown before end of hour

THE PSYCHOLOGY:
- Large developers expect premium
- Free tools feel worthless
- If it's easy + powerful = "this is worth it"
- One caught mistake = "already paid for itself"
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from services.memory_service import memory_service
from services.connected_intelligence import connected_intelligence
from services.whatsapp_service import whatsapp_service
from utils.logger import logger


@dataclass
class OnboardingState:
    """Track customer's onboarding progress"""
    company_id: str
    company_name: str
    started_at: datetime
    steps_completed: List[str]
    first_spec_uploaded: bool = False
    first_photo_analyzed: bool = False
    first_question_answered: bool = False
    first_mismatch_caught: bool = False
    demo_value_shown: float = 0  # INR


class OnboardingWowService:
    """
    Create the $1000/month WOW experience in the first hour
    """
    
    def __init__(self):
        self._states: Dict[str, OnboardingState] = {}
    
    # =========================================================================
    # WELCOME MESSAGES - Premium Feel
    # =========================================================================
    
    def get_premium_welcome(self, company_name: str, user_name: str) -> str:
        """
        First message that sets the tone - THIS IS PREMIUM
        """
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 *Welcome to SiteMind*
   _Your Project Brain_
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hello {user_name}! 👋

Welcome to *{company_name}*'s dedicated AI construction assistant.

*What I do for you:*
✅ Answer ANY construction question with citations
✅ Cross-reference site photos against specs
✅ Catch expensive mismatches BEFORE rework
✅ Track every decision with full audit trail

*Quick Start (takes 5 minutes):*

1️⃣ *Upload a drawing* - Send any PDF/image
   I'll extract all specifications

2️⃣ *Ask me anything* - Try: "What's the column size at B2?"
   I'll answer with exact source reference

3️⃣ *Send a site photo* - I'll verify against specs
   If something's wrong, I'll catch it

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *Try now:* Send me a structural drawing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_SiteMind: Zero information gaps. Zero money leaks._"""

    def get_first_drawing_response(self, specs_count: int, drawing_name: str) -> str:
        """
        Response after first drawing uploaded - Show immediate value
        """
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 *Drawing Processed*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ *{drawing_name}* analyzed

📊 *Extracted:*
• {specs_count} specifications stored
• All dimensions indexed
• Rebar details captured
• Concrete grades noted

*What this enables:*
🔍 Ask "column size at B2?" → Instant answer with source
📷 Send site photo → Auto-verify against these specs
⚠️ Any mismatch → Caught before it costs ₹3-5 lakh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *Try now:* Ask me about any element in this drawing
   Or send a site photo to verify against specs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    def get_first_question_response(self, question: str, answer: str, source: str) -> str:
        """
        First question answered - Demonstrate citation power
        """
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 *Your Question:*
{question}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📎 *Source:* {source}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ *Notice:* Every answer includes the exact source.
No more "who said that?" or "where's that from?"

_Everything in SiteMind is traceable and citeable._"""

    def get_photo_match_response(self, description: str) -> str:
        """
        Photo analyzed, matches specs - Show verification value
        """
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📷 *Photo Verified*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{description}

✅ *Status:* MATCHES SPECIFICATIONS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ *Verification Complete*
   Cross-referenced against stored drawings
   No discrepancies detected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_Every photo you send is automatically verified._
_If something's wrong, SiteMind catches it._"""

    def get_mismatch_caught_response(
        self, 
        description: str,
        detected: str,
        expected: str,
        source: str,
        cost_impact: float,
    ) -> str:
        """
        THE MONEY MOMENT - First mismatch caught
        This is where they realize the value
        """
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 *MISMATCH DETECTED*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{description}

┌─────────────────────────────────────┐
│ 🔴 *FOUND:*     {detected}
│ 🟢 *REQUIRED:*  {expected}
│ 📎 *SOURCE:*    {source}
└─────────────────────────────────────┘

⚠️ *If not caught:*
• Rework after concrete: ₹{cost_impact/100000:.1f} Lakh
• Schedule delay: 1-2 weeks
• Quality compromise risk

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 *VALUE DELIVERED*
   This ONE catch just saved ₹{cost_impact/100000:.1f} Lakh
   
   Your monthly subscription: ₹83,000
   This single catch: ₹{cost_impact/100000:.1f} Lakh
   
   *ROI on this catch alone: {cost_impact/83000:.0f}x*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛑 *RECOMMENDED ACTION:*
Stop work. Verify on site. Fix before pour.

_SiteMind caught this. Your Project Brain is working._"""

    # =========================================================================
    # FIRST HOUR MILESTONES
    # =========================================================================

    def get_30_minute_checkin(self, company_name: str, stats: Dict) -> str:
        """
        30 minute check-in - Show progress
        """
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *Your First 30 Minutes with SiteMind*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*{company_name}* Progress:

📐 Specifications stored: {stats.get('specs', 0)}
📷 Photos analyzed: {stats.get('photos', 0)}
💬 Questions answered: {stats.get('queries', 0)}
⚠️ Mismatches caught: {stats.get('alerts', 0)}

💰 *Estimated Value Protected: ₹{stats.get('value_protected', 0)/100000:.1f} Lakh*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*What's Next:*

{"✅" if stats.get('specs', 0) > 0 else "⬜"} Upload project drawings
{"✅" if stats.get('queries', 0) > 0 else "⬜"} Ask a construction question
{"✅" if stats.get('photos', 0) > 0 else "⬜"} Send a site photo for verification

_The more you use SiteMind, the smarter it gets._"""

    def get_first_hour_summary(self, company_name: str, stats: Dict) -> str:
        """
        First hour summary - The WOW moment
        """
        value = stats.get('value_protected', 0)
        subscription = 83000  # INR
        roi = value / subscription if value > 0 else 0
        
        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 *YOUR FIRST HOUR WITH SITEMIND*
   {company_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Activity:*
├─ Drawings processed: {stats.get('documents', 0)}
├─ Specifications stored: {stats.get('specs', 0)}
├─ Photos analyzed: {stats.get('photos', 0)}
├─ Questions answered: {stats.get('queries', 0)}
└─ Mismatches detected: {stats.get('alerts', 0)}

💰 *Value in First Hour:*
┌─────────────────────────────────────────────┐
│                                             │
│   Potential Rework Prevented: ₹{value/100000:.1f}L    
│   Monthly Subscription: ₹0.83L              │
│                                             │
│   *First Hour ROI: {roi:.0f}x*                  │
│                                             │
└─────────────────────────────────────────────┘

{"🏆 *CONGRATULATIONS!*" if value > 0 else ""}
{"SiteMind already paid for itself!" if roi > 1 else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*What Happens Next:*

• Every photo gets cross-referenced
• Every decision gets tracked
• Every question gets cited answers
• Every mismatch gets caught

Your team just got a 24/7 AI construction expert.

_SiteMind: Your Project Brain is now active._
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    # =========================================================================
    # DEMO SCENARIOS
    # =========================================================================

    async def run_demo_scenario(
        self,
        company_id: str,
        project_id: str,
        phone: str,
    ) -> None:
        """
        Run a demo that shows SiteMind's power
        Uses example specs and simulated mismatch detection
        """
        
        # Step 1: Store demo specifications
        demo_specs = [
            {
                "element": "column",
                "location": "Grid B2, Floor 3",
                "details": {
                    "size": "450x450mm",
                    "rebar": "12T16 (12 nos, 16mm dia)",
                    "ties": "8mm @ 150mm c/c",
                    "concrete": "M30",
                    "cover": "40mm",
                },
                "source": "Drawing STR-07, Page 3",
            },
            {
                "element": "beam",
                "location": "Grid B2-C2, Floor 3",
                "details": {
                    "size": "300x600mm",
                    "top_steel": "4T20",
                    "bottom_steel": "3T16",
                    "stirrups": "8mm @ 100mm c/c (near support)",
                    "concrete": "M30",
                },
                "source": "Drawing STR-08",
            },
            {
                "element": "slab",
                "location": "Floor 3, Area A",
                "details": {
                    "thickness": "150mm",
                    "main_steel": "10mm @ 150mm c/c",
                    "distribution": "8mm @ 200mm c/c",
                    "concrete": "M25",
                    "cover": "25mm",
                },
                "source": "Drawing STR-09",
            },
        ]
        
        for spec in demo_specs:
            await connected_intelligence.store_specification(
                company_id=company_id,
                project_id=project_id,
                spec_type="structural",
                element=spec["element"],
                location=spec["location"],
                details=spec["details"],
                source_document=spec["source"],
                uploaded_by="SiteMind Demo",
            )
        
        # Step 2: Send demo summary
        demo_msg = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 *DEMO: SiteMind in Action*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I've loaded sample specifications:

📐 *Column B2* (Floor 3)
   450x450mm, 12T16, M30

📐 *Beam B2-C2* (Floor 3)
   300x600mm, 4T20 top, 3T16 bottom

📐 *Slab* (Floor 3, Area A)
   150mm thick, 10mm @ 150mm c/c

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Try these:*

1️⃣ Ask: "What's the column size at B2?"
2️⃣ Ask: "Rebar for beam B2-C2?"
3️⃣ Ask: "Slab thickness on floor 3?"

_I'll answer with exact citations._
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        await whatsapp_service.send_message(phone, demo_msg)
        
        logger.info(f"🎬 Demo scenario loaded for {company_id}")


# Singleton
onboarding_wow = OnboardingWowService()

