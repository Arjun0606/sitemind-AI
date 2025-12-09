"""
Reminder Service - Background Job for RFI Reminders
====================================================

This service runs periodically to:
1. Check for overdue RFIs
2. Send reminders via WhatsApp
3. Escalate if needed
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from services.phase1_memory_engine import memory_engine
from services.whatsapp_service import whatsapp_service
from database import db
from utils.logger import logger


class ReminderService:
    """
    Sends automatic reminders for:
    - Overdue RFIs
    - Pending decisions
    - Unresolved issues
    """
    
    async def check_and_send_reminders(self, company_id: str) -> Dict[str, Any]:
        """
        Check all projects for items needing reminders
        """
        projects = await db.get_company_projects(company_id)
        
        reminders_sent = {
            "rfi_reminders": 0,
            "escalations": 0,
        }
        
        for project in projects:
            project_id = project["id"]
            
            # Check overdue RFIs
            overdue_rfis = memory_engine.get_overdue_rfis(company_id, project_id, days=3)
            
            for rfi in overdue_rfis:
                days_overdue = (datetime.utcnow() - rfi.raised_at).days
                
                # Send reminder
                await self.send_rfi_reminder(
                    rfi=rfi,
                    project_name=project.get("name", "Project"),
                    days_overdue=days_overdue,
                )
                reminders_sent["rfi_reminders"] += 1
                
                # Escalate if very overdue (>7 days)
                if days_overdue > 7:
                    await self.escalate_rfi(
                        rfi=rfi,
                        company_id=company_id,
                        project_name=project.get("name", "Project"),
                    )
                    reminders_sent["escalations"] += 1
        
        return reminders_sent
    
    async def send_rfi_reminder(
        self,
        rfi,
        project_name: str,
        days_overdue: int,
    ):
        """Send reminder for overdue RFI"""
        
        # Get the assigned person's phone (if we have it)
        # For now, we'll log it - in production, would send to actual phone
        
        reminder_message = f"""⏰ *RFI REMINDER*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*{rfi.id}* - Pending {days_overdue} days

Project: {project_name}
Question: {rfi.question[:100]}...

Raised by: {rfi.raised_by}
Assigned to: {rfi.assigned_to or 'Unassigned'}

⚠️ This RFI is overdue. Please respond.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        logger.info(f"📧 RFI Reminder: {rfi.id} - {days_overdue} days overdue")
        
        # In production, send to the assigned person
        # await whatsapp_service.send_message(assigned_phone, reminder_message)
        
        return reminder_message
    
    async def escalate_rfi(
        self,
        rfi,
        company_id: str,
        project_name: str,
    ):
        """Escalate severely overdue RFI to management"""
        
        days_overdue = (datetime.utcnow() - rfi.raised_at).days
        
        escalation_message = f"""🚨 *RFI ESCALATION*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*{rfi.id}* - OVERDUE {days_overdue} DAYS

Project: {project_name}
Question: {rfi.question[:100]}...

Raised by: {rfi.raised_by}
Assigned to: {rfi.assigned_to or 'Unassigned'}
Original date: {rfi.raised_at.strftime('%d-%b-%Y')}

🔴 This requires immediate attention.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        logger.warning(f"🚨 RFI Escalation: {rfi.id} - {days_overdue} days overdue")
        
        # In production, send to admins/management
        # admins = await db.get_company_admins(company_id)
        # for admin in admins:
        #     await whatsapp_service.send_message(admin.phone, escalation_message)
        
        return escalation_message
    
    async def send_morning_summary(self, company_id: str):
        """
        Send morning summary to all project managers
        """
        projects = await db.get_company_projects(company_id)
        
        for project in projects:
            project_id = project["id"]
            
            # Generate summary
            summary = await memory_engine.generate_daily_summary(company_id, project_id)
            
            # In production, send to project managers
            logger.info(f"📊 Morning summary generated for {project.get('name')}")
        
        return len(projects)


# Singleton
reminder_service = ReminderService()


# =============================================================================
# SCHEDULED TASK (Run this periodically)
# =============================================================================

async def run_daily_reminders():
    """
    Run this function daily (via cron, APScheduler, or similar)
    
    Example cron: 0 9 * * * (9 AM daily)
    
    Or with APScheduler:
    scheduler.add_job(run_daily_reminders, 'cron', hour=9)
    """
    from database import db
    
    logger.info("🔔 Starting daily reminder job...")
    
    # Get all active companies
    # In production, iterate through all companies
    # For now, this is a placeholder
    
    # Example:
    # companies = await db.select("companies", filters={"status": "active"})
    # for company in companies:
    #     await reminder_service.check_and_send_reminders(company["id"])
    #     await reminder_service.send_morning_summary(company["id"])
    
    logger.info("✅ Daily reminder job complete")

