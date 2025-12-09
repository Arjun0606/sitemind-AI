"""
SiteMind Message Templates
==========================

Professional, enterprise-grade message formatting.
Every message should feel worth $1000/month.

PRINCIPLES:
1. Clean structure with clear sections
2. Visual hierarchy with separators
3. Citations always visible
4. Action items clear
5. Professional but not cold
"""

from typing import List, Dict, Optional
from datetime import datetime


class MessageTemplates:
    """
    Enterprise-grade message templates for WhatsApp
    
    Makes every response feel professional and valuable.
    """
    
    # =========================================================================
    # FORMATTING CONSTANTS
    # =========================================================================
    
    SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    THIN_SEP = "───────────────────────────────────────"
    
    # =========================================================================
    # AI RESPONSE - Questions
    # =========================================================================
    
    @staticmethod
    def format_ai_answer(
        question: str,
        answer: str,
        citations: List[Dict] = None,
        project_name: str = None,
    ) -> str:
        """
        Format AI answer with citations
        
        Professional structure that shows the AI is intelligent.
        """
        
        # Format citations
        citation_section = ""
        if citations:
            citation_lines = []
            for i, cite in enumerate(citations[:3], 1):
                source = cite.get("source", cite.get("document", "Project memory"))
                date = cite.get("date", "")
                date_str = f" ({date})" if date else ""
                citation_lines.append(f"   {i}. {source}{date_str}")
            
            citation_section = f"""

📎 *Sources:*
{chr(10).join(citation_lines)}"""
        
        return f"""
{MessageTemplates.SEPARATOR}
💬 *{project_name or 'Project'}*
{MessageTemplates.SEPARATOR}

{answer}{citation_section}

{MessageTemplates.THIN_SEP}
_Ask follow-up questions anytime._
"""
    
    # =========================================================================
    # PHOTO ANALYSIS
    # =========================================================================
    
    @staticmethod
    def format_photo_match(
        analysis: str,
        specs_verified: List[str],
        location: str = None,
    ) -> str:
        """Photo matches specifications"""
        
        specs_text = "\n".join([f"   ✓ {s}" for s in specs_verified[:5]])
        location_text = f"\n📍 *Location:* {location}" if location else ""
        
        return f"""
{MessageTemplates.SEPARATOR}
✅ *PHOTO VERIFIED*
{MessageTemplates.SEPARATOR}

{analysis}{location_text}

{MessageTemplates.THIN_SEP}
📐 *Verified Against:*
{specs_text}

{MessageTemplates.SEPARATOR}
_Photo stored in project memory._
"""
    
    @staticmethod
    def format_photo_mismatch(
        analysis: str,
        detected: str,
        expected: str,
        source_doc: str,
        cost_impact_lakh: float,
        alert_id: str,
    ) -> str:
        """Photo has mismatch - THE HIGH VALUE MOMENT"""
        
        return f"""
{MessageTemplates.SEPARATOR}
🚨 *MISMATCH DETECTED*
{MessageTemplates.SEPARATOR}

{analysis}

{MessageTemplates.THIN_SEP}
⚠️ *Discrepancy Found:*
{MessageTemplates.THIN_SEP}

📷 *What I see:* {detected}
📐 *What spec says:* {expected}
📄 *Source:* {source_doc}

{MessageTemplates.SEPARATOR}
💰 *COST IF NOT FIXED*
{MessageTemplates.SEPARATOR}

Estimated rework: *₹{cost_impact_lakh:.1f} Lakh*
Alert ID: {alert_id[:8]}

{MessageTemplates.THIN_SEP}
⛔ *RECOMMENDATION:* Stop work and verify.
{MessageTemplates.THIN_SEP}

_Reply /resolve {alert_id[:8]} if this is incorrect._
"""
    
    # =========================================================================
    # DOCUMENT PROCESSING
    # =========================================================================
    
    @staticmethod
    def format_document_processed(
        document_name: str,
        specs_count: int,
        specs_preview: List[Dict],
    ) -> str:
        """Document uploaded and specs extracted"""
        
        # Format spec preview
        preview_lines = []
        for spec in specs_preview[:6]:
            element = spec.get("element", "Item")
            location = spec.get("location", "")
            preview_lines.append(f"   • {element} @ {location}")
        
        preview_text = "\n".join(preview_lines)
        more_text = f"\n   _...and {specs_count - 6} more_" if specs_count > 6 else ""
        
        return f"""
{MessageTemplates.SEPARATOR}
📄 *DOCUMENT PROCESSED*
{MessageTemplates.SEPARATOR}

✅ *{document_name}*
📐 Specifications extracted: *{specs_count}*

{MessageTemplates.THIN_SEP}
🔍 *What I Found:*
{MessageTemplates.THIN_SEP}

{preview_text}{more_text}

{MessageTemplates.SEPARATOR}
🧠 *These specs are now active.*
{MessageTemplates.SEPARATOR}

Every site photo will be cross-referenced.
Every question will cite this document.

_Try: "What does this drawing say about [element]?"_
"""
    
    # =========================================================================
    # VALUE REPORTS
    # =========================================================================
    
    @staticmethod
    def format_value_report(
        company_name: str,
        period: str,
        mismatches_caught: int,
        value_protected_lakh: float,
        specs_stored: int,
        photos_analyzed: int,
        questions_answered: int,
    ) -> str:
        """Weekly/Monthly value report"""
        
        # Calculate ROI
        subscription_lakh = 0.83  # ₹83,000
        roi = value_protected_lakh / subscription_lakh if subscription_lakh > 0 else 0
        
        return f"""
{MessageTemplates.SEPARATOR}
📊 *SITEMIND VALUE REPORT*
   {company_name}
   {period}
{MessageTemplates.SEPARATOR}

💰 *VALUE PROTECTED*
{MessageTemplates.THIN_SEP}
   Mismatches Caught: {mismatches_caught}
   Value Saved: *₹{value_protected_lakh:.1f} Lakh*
   ROI: *{roi:.0f}x* your subscription

📐 *PROJECT INTELLIGENCE*
{MessageTemplates.THIN_SEP}
   Specifications Stored: {specs_stored}
   Photos Analyzed: {photos_analyzed}
   Questions Answered: {questions_answered}

{MessageTemplates.SEPARATOR}
💡 *Every photo cross-referenced.*
   *Every mismatch caught early.*
{MessageTemplates.SEPARATOR}

_Full report: sitemind.ai/dashboard_
"""
    
    # =========================================================================
    # ALERTS
    # =========================================================================
    
    @staticmethod
    def format_alert_summary(
        open_alerts: int,
        total_value_at_risk: float,
        critical_alerts: List[Dict],
    ) -> str:
        """Summary of open alerts"""
        
        if open_alerts == 0:
            return f"""
{MessageTemplates.SEPARATOR}
✅ *ALL CLEAR*
{MessageTemplates.SEPARATOR}

No open mismatch alerts.
All photos verified against specs.

_Keep sending photos for continuous verification._
"""
        
        # Format critical alerts
        alert_lines = []
        for alert in critical_alerts[:3]:
            severity = "🔴" if alert.get("severity") == "critical" else "🟠"
            desc = alert.get("description", "")[:40]
            alert_lines.append(f"   {severity} {desc}...")
        
        alerts_text = "\n".join(alert_lines)
        
        return f"""
{MessageTemplates.SEPARATOR}
🚨 *{open_alerts} OPEN ALERTS*
{MessageTemplates.SEPARATOR}

💰 Total value at risk: *₹{total_value_at_risk:.1f} Lakh*

{MessageTemplates.THIN_SEP}
*Priority Issues:*
{alerts_text}

{MessageTemplates.SEPARATOR}
View all: sitemind.ai/dashboard/alerts
{MessageTemplates.SEPARATOR}
"""
    
    # =========================================================================
    # COMMANDS
    # =========================================================================
    
    @staticmethod
    def format_help(user_name: str, project_name: str) -> str:
        """Help message - professional and clear"""
        
        return f"""
{MessageTemplates.SEPARATOR}
🧠 *SITEMIND - Your Project Brain*
{MessageTemplates.SEPARATOR}

Hi {user_name}! Here's what I can do:

*SEND ME:*
   📷 *Photos* → Cross-referenced against specs
   📄 *Documents* → Specs extracted automatically
   💬 *Questions* → Answered with citations
   📝 *Updates* → Stored in project memory

*COMMANDS:*
   /project  → Switch between projects
   /specs    → View stored specifications
   /alerts   → View mismatch alerts
   /report   → Get value protected report
   /search   → Search project memory
   /help     → Show this message

{MessageTemplates.THIN_SEP}
Current Project: *{project_name}*
{MessageTemplates.THIN_SEP}

_Just send a message to get started._
"""
    
    # =========================================================================
    # ERRORS - Even errors should feel professional
    # =========================================================================
    
    @staticmethod
    def format_error(error_type: str, details: str = None) -> str:
        """Professional error message"""
        
        detail_text = f"\n_{details}_" if details else ""
        
        return f"""
{MessageTemplates.SEPARATOR}
⚠️ *Unable to Process*
{MessageTemplates.SEPARATOR}

{error_type}{detail_text}

Please try again, or reply with your question
and I'll do my best to help.

{MessageTemplates.THIN_SEP}
_Need help? Just describe what you need._
"""
    
    # =========================================================================
    # TEAM NOTIFICATIONS
    # =========================================================================
    
    @staticmethod
    def format_team_member_added(
        member_name: str,
        added_by: str,
        company_name: str,
    ) -> str:
        """Notification when team member is added"""
        
        return f"""
{MessageTemplates.SEPARATOR}
👥 *TEAM MEMBER ADDED*
{MessageTemplates.SEPARATOR}

*{member_name}* has been added to
*{company_name}* by {added_by}.

They can now:
   • Send questions and get answers
   • Upload photos for verification
   • Access all project information

{MessageTemplates.THIN_SEP}
_Team management: sitemind.ai/dashboard/team_
"""


# Export singleton-style access
templates = MessageTemplates()

