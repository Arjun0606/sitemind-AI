"""
SiteMind Subscription Reminder Service
Handles billing reminders and admin notifications

REMINDER SCHEDULE:
- 7 days before due: Friendly reminder
- 3 days before due: Urgent reminder
- 1 day before due: Final reminder
- On due date: Invoice sent
- 3 days after due: Grace period warning
- 7 days after due: Service suspension warning
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from utils.logger import logger


@dataclass
class SubscriptionStatus:
    """Company subscription status"""
    company_id: str
    company_name: str
    plan: str = "enterprise"
    status: str = "active"  # active, grace_period, suspended, cancelled
    
    # Dates
    billing_cycle_start: datetime = None
    billing_cycle_end: datetime = None
    next_invoice_date: datetime = None
    
    # Amounts
    flat_fee_usd: float = 1000.0
    pending_usage_usd: float = 0.0
    total_due_usd: float = 1000.0
    
    # Flags
    is_pilot: bool = False
    is_founding: bool = False
    auto_pay_enabled: bool = False


class SubscriptionReminderService:
    """
    Send billing reminders and manage subscriptions
    """
    
    def __init__(self):
        # In-memory subscription tracking (use database in production)
        self._subscriptions: Dict[str, SubscriptionStatus] = {}
        self._reminders_sent: Dict[str, List[str]] = {}  # company_id -> list of reminder types
        
        # Reminder schedule (days before due)
        self.REMINDER_SCHEDULE = {
            7: "friendly",
            3: "urgent", 
            1: "final",
            0: "invoice",
            -3: "grace_warning",
            -7: "suspension_warning",
        }
    
    # =========================================================================
    # SUBSCRIPTION MANAGEMENT
    # =========================================================================
    
    def get_subscription(self, company_id: str) -> Optional[SubscriptionStatus]:
        """Get subscription status for a company"""
        return self._subscriptions.get(company_id)
    
    def create_subscription(
        self,
        company_id: str,
        company_name: str,
        is_pilot: bool = False,
        is_founding: bool = False,
    ) -> SubscriptionStatus:
        """Create a new subscription"""
        now = datetime.utcnow()
        
        subscription = SubscriptionStatus(
            company_id=company_id,
            company_name=company_name,
            billing_cycle_start=now,
            billing_cycle_end=now + timedelta(days=30),
            next_invoice_date=now + timedelta(days=30),
            is_pilot=is_pilot,
            is_founding=is_founding,
            flat_fee_usd=0 if is_pilot else (750 if is_founding else 1000),
        )
        
        self._subscriptions[company_id] = subscription
        logger.info(f"📋 Subscription created for {company_name}")
        
        return subscription
    
    def update_usage(self, company_id: str, usage_usd: float):
        """Update pending usage charges"""
        if company_id in self._subscriptions:
            self._subscriptions[company_id].pending_usage_usd = usage_usd
            self._subscriptions[company_id].total_due_usd = (
                self._subscriptions[company_id].flat_fee_usd + usage_usd
            )
    
    # =========================================================================
    # REMINDER GENERATION
    # =========================================================================
    
    def check_reminders_due(self, company_id: str) -> List[Dict]:
        """Check what reminders are due for a company"""
        subscription = self._subscriptions.get(company_id)
        if not subscription:
            return []
        
        if subscription.is_pilot:
            return []  # No reminders for pilots
        
        now = datetime.utcnow()
        due_date = subscription.next_invoice_date
        
        if not due_date:
            return []
        
        days_until_due = (due_date - now).days
        
        reminders = []
        sent = self._reminders_sent.get(company_id, [])
        
        for days, reminder_type in self.REMINDER_SCHEDULE.items():
            if days_until_due <= days and reminder_type not in sent:
                reminders.append({
                    "type": reminder_type,
                    "days_until_due": days_until_due,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "amount_usd": subscription.total_due_usd,
                })
        
        return reminders
    
    def mark_reminder_sent(self, company_id: str, reminder_type: str):
        """Mark a reminder as sent"""
        if company_id not in self._reminders_sent:
            self._reminders_sent[company_id] = []
        self._reminders_sent[company_id].append(reminder_type)
    
    # =========================================================================
    # REMINDER MESSAGES
    # =========================================================================
    
    def format_reminder_message(
        self,
        reminder_type: str,
        company_name: str,
        amount_usd: float,
        due_date: str,
    ) -> str:
        """Format reminder message for WhatsApp"""
        
        amount_inr = amount_usd * 83
        
        messages = {
            "friendly": f"""📋 *SiteMind Billing Reminder*

Hi {company_name}!

Your SiteMind subscription will renew in 7 days.

💰 Amount: ${amount_usd:.2f} (₹{amount_inr:,.0f})
📅 Due Date: {due_date}

_No action needed if auto-pay is enabled._

Questions? Reply to this message.""",

            "urgent": f"""⏰ *Payment Due Soon*

Hi {company_name}!

Your SiteMind subscription renews in 3 days.

💰 Amount: ${amount_usd:.2f} (₹{amount_inr:,.0f})
📅 Due Date: {due_date}

Please ensure payment is ready to avoid interruption.

_Contact billing@sitemind.ai for questions._""",

            "final": f"""🔔 *Final Reminder - Payment Due Tomorrow*

Hi {company_name}!

Your SiteMind subscription renews TOMORROW.

💰 Amount: ${amount_usd:.2f} (₹{amount_inr:,.0f})
📅 Due Date: {due_date}

Please ensure payment is completed to maintain access.

_Contact billing@sitemind.ai for payment assistance._""",

            "invoice": f"""📄 *Invoice Ready*

Hi {company_name}!

Your SiteMind invoice is ready.

━━━━━━━━━━━━━━━━━━━━━━
SiteMind Enterprise     ${amount_usd:.2f}
━━━━━━━━━━━━━━━━━━━━━━
Total Due:              ${amount_usd:.2f}
                        ₹{amount_inr:,.0f}
━━━━━━━━━━━━━━━━━━━━━━

📅 Due Date: {due_date}

_Reply 'paid' once payment is complete._""",

            "grace_warning": f"""⚠️ *Payment Overdue - Grace Period*

Hi {company_name}!

Your SiteMind payment is 3 days overdue.

💰 Amount Due: ${amount_usd:.2f} (₹{amount_inr:,.0f})

Your service will continue for 4 more days. Please complete payment to avoid any interruption.

_Contact billing@sitemind.ai urgently._""",

            "suspension_warning": f"""🚨 *URGENT: Service Suspension Warning*

Hi {company_name}!

Your SiteMind payment is 7 days overdue.

💰 Amount Due: ${amount_usd:.2f} (₹{amount_inr:,.0f})

⚠️ Service will be suspended in 24 hours if payment is not received.

Your data will be preserved for 30 days.

_Contact billing@sitemind.ai immediately._""",
        }
        
        return messages.get(reminder_type, "")
    
    # =========================================================================
    # ADMIN NOTIFICATIONS
    # =========================================================================
    
    def format_member_added_notification(
        self,
        member_name: str,
        member_phone: str,
        added_by: str,
    ) -> str:
        """Notification when member is added"""
        return f"""👥 *Team Member Added*

✅ {member_name} has been added to your SiteMind team.

📱 Phone: {member_phone}
👤 Added by: {added_by}

They can now send messages to SiteMind."""

    def format_member_removed_notification(
        self,
        member_name: str,
        removed_by: str,
    ) -> str:
        """Notification when member is removed"""
        return f"""👥 *Team Member Removed*

❌ {member_name} has been removed from your SiteMind team.

👤 Removed by: {removed_by}

They will no longer be able to access SiteMind."""

    def format_usage_alert(
        self,
        company_name: str,
        usage_type: str,
        current: int,
        limit: int,
        percentage: float,
    ) -> str:
        """Alert when usage reaches threshold"""
        
        if percentage >= 100:
            return f"""🔴 *Usage Limit Reached*

{company_name} has exceeded the included {usage_type}.

📊 Used: {current} / {limit} ({percentage:.0f}%)

Additional usage will be charged at overage rates.

_Type 'status' to see current usage._"""
        
        elif percentage >= 80:
            return f"""🟡 *High Usage Alert*

{company_name} is approaching the {usage_type} limit.

📊 Used: {current} / {limit} ({percentage:.0f}%)

_Type 'status' to see current usage._"""
        
        return ""


# Singleton instance
subscription_reminder_service = SubscriptionReminderService()

