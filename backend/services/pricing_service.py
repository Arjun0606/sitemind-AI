"""
SiteMind Pricing Service
Simple, transparent pricing. One product, one price.

PRICING TIERS:
1. ACTIVE SITE: $500/month - Full access, unlimited queries
2. ARCHIVED PROJECT: $50/month - Legal retention, read-only access

Why archive matters:
- Construction disputes happen 5-10 years after completion
- Full audit trail with citations = legal protection
- Reference for future projects
- Compliance requirements
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum


class ProjectStatus(str, Enum):
    """Project lifecycle stages"""
    ACTIVE = "active"           # Full access, unlimited queries
    PAUSED = "paused"           # Temporarily paused (not billed)
    COMPLETED = "completed"     # Project done, moving to archive
    ARCHIVED = "archived"       # Archive tier - read-only access


class PricingConfig:
    """
    SiteMind Pricing Configuration
    
    ACTIVE: $500/site/month - Full power
    ARCHIVED: $50/site/month - Legal retention
    """
    
    # ============================
    # ACTIVE SITE PRICING
    # ============================
    BASE_PRICE_USD = 500
    BASE_PRICE_INR = 41_500  # ~$500 at 83 INR/USD
    
    # Volume discounts for active sites
    VOLUME_DISCOUNTS = {
        3: 0.10,    # 10% off for 3+ sites
        6: 0.15,    # 15% off for 6+ sites
        10: 0.25,   # 25% off for 10+ sites
    }
    
    # ============================
    # ARCHIVE PRICING (UPSELL!)
    # ============================
    ARCHIVE_PRICE_USD = 50      # $50/project/month
    ARCHIVE_PRICE_INR = 4_150   # ₹4,150/project/month
    
    # Or one-time archive fee (5 years retention)
    ARCHIVE_ONETIME_USD = 2_000    # $2,000 for 5 years
    ARCHIVE_ONETIME_INR = 166_000  # ₹1.66 Lakhs for 5 years
    
    # Archive volume discounts
    ARCHIVE_VOLUME_DISCOUNTS = {
        5: 0.10,    # 10% off for 5+ archived projects
        10: 0.20,   # 20% off for 10+ archived projects
        20: 0.30,   # 30% off for 20+ archived projects
    }
    
    # ============================
    # FOUNDING PARTNER PROGRAM
    # ============================
    FOUNDING_PARTNER_DISCOUNT = 0.20  # 20% off forever
    PILOT_DURATION_MONTHS = 3
    PILOT_MAX_SITES = 5
    PILOT_SLOTS_TOTAL = 3


class PricingService:
    """
    Handles all pricing calculations
    
    ACTIVE SITES:
    - $500/site/month
    - 3+ sites: 10% off
    - 6+ sites: 15% off  
    - 10+ sites: 25% off
    - Unlimited usage
    
    ARCHIVED PROJECTS (Upsell):
    - $50/project/month OR
    - $2,000 one-time (5 years)
    - Read-only access to all data
    - Legal protection with audit trail
    - Reference for future projects
    """
    
    def __init__(self):
        self.config = PricingConfig()
        self._pilot_partners: Dict[str, Dict] = {}
        self._pilots_used = 0
    
    # ============================
    # ACTIVE SITE PRICING
    # ============================
    
    def get_price(
        self,
        num_sites: int,
        is_founding_partner: bool = False,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """Calculate price for active sites"""
        base_price = self.config.BASE_PRICE_USD if currency == "USD" else self.config.BASE_PRICE_INR
        
        # Apply volume discount
        volume_discount = 0
        volume_tier = None
        for threshold, discount in sorted(self.config.VOLUME_DISCOUNTS.items(), reverse=True):
            if num_sites >= threshold:
                volume_discount = discount
                volume_tier = threshold
                break
        
        # Founding partner gets better of volume or founding discount
        if is_founding_partner:
            founding_discount = self.config.FOUNDING_PARTNER_DISCOUNT
            if founding_discount > volume_discount:
                total_discount = founding_discount
                discount_reason = "founding_partner"
            else:
                total_discount = volume_discount
                discount_reason = f"volume_{volume_tier}+_sites"
        else:
            total_discount = volume_discount
            discount_reason = f"volume_{volume_tier}+_sites" if volume_tier else "none"
        
        price_per_site = base_price * (1 - total_discount)
        total_monthly = price_per_site * num_sites
        savings_per_site = base_price - price_per_site
        
        symbol = "$" if currency == "USD" else "₹"
        
        return {
            "tier": "active",
            "num_sites": num_sites,
            "currency": currency,
            "base_price_per_site": base_price,
            "discount_percent": total_discount * 100,
            "discount_reason": discount_reason,
            "price_per_site": price_per_site,
            "price_per_site_formatted": f"{symbol}{price_per_site:,.0f}",
            "total_monthly": total_monthly,
            "total_monthly_formatted": f"{symbol}{total_monthly:,.0f}",
            "total_annual": total_monthly * 12,
            "savings_per_site": savings_per_site,
            "usage": "UNLIMITED - No query limits",
        }
    
    # ============================
    # ARCHIVE PRICING (UPSELL!)
    # ============================
    
    def get_archive_price(
        self,
        num_projects: int,
        payment_type: str = "monthly",  # "monthly" or "onetime"
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Calculate archive pricing for completed projects
        
        GREAT UPSELL because:
        - Construction disputes happen 5-10 years later
        - All decisions, changes, approvals preserved
        - Legal protection with full citations
        - Low cost to us (just storage)
        - High value to builder
        """
        if payment_type == "onetime":
            base_price = self.config.ARCHIVE_ONETIME_USD if currency == "USD" else self.config.ARCHIVE_ONETIME_INR
            period = "5 years"
        else:
            base_price = self.config.ARCHIVE_PRICE_USD if currency == "USD" else self.config.ARCHIVE_PRICE_INR
            period = "month"
        
        # Apply volume discount
        volume_discount = 0
        for threshold, discount in sorted(self.config.ARCHIVE_VOLUME_DISCOUNTS.items(), reverse=True):
            if num_projects >= threshold:
                volume_discount = discount
                break
        
        price_per_project = base_price * (1 - volume_discount)
        total = price_per_project * num_projects
        
        symbol = "$" if currency == "USD" else "₹"
        
        return {
            "tier": "archive",
            "num_projects": num_projects,
            "payment_type": payment_type,
            "currency": currency,
            "base_price": base_price,
            "discount_percent": volume_discount * 100,
            "price_per_project": price_per_project,
            "price_per_project_formatted": f"{symbol}{price_per_project:,.0f}/{period}",
            "total": total,
            "total_formatted": f"{symbol}{total:,.0f}",
            "period": period,
            "whats_included": [
                "✅ Full read-only access to all project data",
                "✅ Complete audit trail preserved",
                "✅ All decisions with citations",
                "✅ All change orders & RFIs",
                "✅ All WhatsApp conversation history",
                "✅ Export to PDF/Excel anytime",
                "✅ Legal-ready documentation",
                "✅ Reference for future projects",
            ],
            "why_archive": [
                "⚖️ Legal disputes can happen 5-10 years later",
                "📋 Compliance & audit requirements",
                "🔍 Reference specs for similar projects",
                "📜 Proof of decisions & approvals",
            ],
        }
    
    def get_archive_pricing_table(self, currency: str = "USD") -> Dict[str, Any]:
        """Get archive pricing table for display"""
        symbol = "$" if currency == "USD" else "₹"
        monthly = self.config.ARCHIVE_PRICE_USD if currency == "USD" else self.config.ARCHIVE_PRICE_INR
        onetime = self.config.ARCHIVE_ONETIME_USD if currency == "USD" else self.config.ARCHIVE_ONETIME_INR
        
        return {
            "options": [
                {
                    "name": "Monthly Archive",
                    "price": f"{symbol}{monthly:,.0f}/project/month",
                    "best_for": "Projects that might need frequent access",
                    "features": [
                        "Cancel anytime",
                        "Full read-only access",
                        "Export capabilities",
                    ],
                },
                {
                    "name": "5-Year Archive",
                    "price": f"{symbol}{onetime:,.0f} one-time",
                    "best_for": "Long-term legal protection",
                    "savings": f"Save {symbol}{(monthly * 60) - onetime:,.0f} vs monthly",
                    "features": [
                        "Pay once, 5 years access",
                        "Full read-only access",
                        "Export capabilities",
                        "Best value for legal retention",
                    ],
                },
            ],
            "volume_discounts": [
                {"projects": "5+", "discount": "10%"},
                {"projects": "10+", "discount": "20%"},
                {"projects": "20+", "discount": "30%"},
            ],
        }
    
    # ============================
    # COMPLETE PRICING TABLE
    # ============================
    
    def get_full_pricing_table(self, currency: str = "USD") -> Dict[str, Any]:
        """Get complete pricing table with both tiers"""
        symbol = "$" if currency == "USD" else "₹"
        base = self.config.BASE_PRICE_USD if currency == "USD" else self.config.BASE_PRICE_INR
        archive = self.config.ARCHIVE_PRICE_USD if currency == "USD" else self.config.ARCHIVE_PRICE_INR
        
        return {
            "active_sites": {
                "description": "Full power for construction in progress",
                "base_price": f"{symbol}{base:,.0f}/site/month",
                "volume_discounts": [
                    {"sites": "1-2", "discount": "0%", "price": f"{symbol}{base:,.0f}"},
                    {"sites": "3-5", "discount": "10%", "price": f"{symbol}{base * 0.90:,.0f}"},
                    {"sites": "6-9", "discount": "15%", "price": f"{symbol}{base * 0.85:,.0f}"},
                    {"sites": "10+", "discount": "25%", "price": f"{symbol}{base * 0.75:,.0f}"},
                ],
                "includes": [
                    "UNLIMITED AI queries",
                    "Unlimited engineers",
                    "Gemini 3.0 Pro (best AI)",
                    "Site photo verification",
                    "Complete audit trail",
                    "Auto reports",
                    "WhatsApp integration",
                    "Web dashboard",
                ],
            },
            "archived_projects": {
                "description": "Legal retention after project completion",
                "monthly_price": f"{symbol}{archive:,.0f}/project/month",
                "onetime_price": f"{symbol}{self.config.ARCHIVE_ONETIME_USD if currency == 'USD' else self.config.ARCHIVE_ONETIME_INR:,.0f} (5 years)",
                "volume_discounts": [
                    {"projects": "5+", "discount": "10%"},
                    {"projects": "10+", "discount": "20%"},
                    {"projects": "20+", "discount": "30%"},
                ],
                "includes": [
                    "Read-only access to all data",
                    "Full audit trail preserved",
                    "All decisions & citations",
                    "Export to PDF/Excel",
                    "Legal-ready documentation",
                ],
                "why": [
                    "Legal disputes happen years later",
                    "Compliance requirements",
                    "Reference for future projects",
                ],
            },
        }
    
    # ============================
    # PROJECT LIFECYCLE
    # ============================
    
    def transition_to_archive(
        self,
        project_id: str,
        project_name: str,
        completion_date: str,
        payment_type: str = "monthly",
        currency: str = "USD",
    ) -> Dict[str, Any]:
        """
        Transition a completed project to archive tier
        
        Called when:
        - Project construction is completed
        - Builder wants to retain data for legal/reference
        """
        archive_pricing = self.get_archive_price(1, payment_type, currency)
        
        return {
            "project_id": project_id,
            "project_name": project_name,
            "previous_status": ProjectStatus.ACTIVE,
            "new_status": ProjectStatus.ARCHIVED,
            "completion_date": completion_date,
            "archive_started": datetime.utcnow().isoformat(),
            "pricing": archive_pricing,
            "message": f"""
🏗️ Project Completed: {project_name}

Your project has been moved to Archive status.

WHAT'S PRESERVED:
✅ All {archive_pricing['whats_included'][0].split('✅ ')[1]}
✅ Complete decision history
✅ All change orders & RFIs
✅ Full audit trail with citations
✅ WhatsApp conversation history

ARCHIVE PRICING:
{archive_pricing['price_per_project_formatted']}

WHY KEEP ARCHIVE:
⚖️ Legal disputes can happen 5-10 years later
📋 All approvals and decisions documented
📜 Export anytime for compliance

To access archive: Use dashboard (read-only)
            """,
            "next_steps": [
                "Confirm archive subscription",
                "Download full project export (optional)",
                "Data preserved indefinitely while subscribed",
            ],
        }
    
    # ============================
    # PILOT PROGRAM (unchanged)
    # ============================
    
    def create_pilot(
        self,
        builder_id: str,
        builder_name: str,
        contact_name: str,
        contact_phone: str,
        sites: list,
    ) -> Dict[str, Any]:
        """Create a founding partner pilot (3 months free)"""
        if self._pilots_used >= self.config.PILOT_SLOTS_TOTAL:
            return {
                "success": False,
                "error": "All founding partner slots are taken",
            }
        
        if len(sites) > self.config.PILOT_MAX_SITES:
            return {
                "success": False,
                "error": f"Pilot limited to {self.config.PILOT_MAX_SITES} sites",
            }
        
        pilot_id = f"pilot_{builder_id}"
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=90)
        
        pilot_value_usd = self.config.BASE_PRICE_USD * len(sites) * 3
        
        pilot = {
            "pilot_id": pilot_id,
            "builder_id": builder_id,
            "builder_name": builder_name,
            "sites": sites,
            "num_sites": len(sites),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "pilot_value": f"${pilot_value_usd:,}",
            "founding_partner_discount": "20% forever",
        }
        
        self._pilot_partners[builder_id] = pilot
        self._pilots_used += 1
        
        return {
            "success": True,
            "pilot": pilot,
            "slots_remaining": self.config.PILOT_SLOTS_TOTAL - self._pilots_used,
        }
    
    # ============================
    # QUOTE GENERATION
    # ============================
    
    def generate_quote(
        self,
        builder_name: str,
        num_active_sites: int,
        num_archived_projects: int = 0,
        is_founding_partner: bool = False,
        currency: str = "USD",
    ) -> str:
        """Generate a complete quote including active + archived"""
        symbol = "$" if currency == "USD" else "₹"
        
        # Active sites pricing
        active = self.get_price(num_active_sites, is_founding_partner, currency)
        
        # Archive pricing (if any)
        archive_section = ""
        archive_total = 0
        if num_archived_projects > 0:
            archive = self.get_archive_price(num_archived_projects, "monthly", currency)
            archive_total = archive["total"]
            archive_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVED PROJECTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Archived Projects: {num_archived_projects}
Price: {archive['price_per_project_formatted']}
Archive Monthly: {archive['total_formatted']}

(Legal retention, read-only access)
"""
        
        grand_total = active["total_monthly"] + archive_total
        
        quote = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          SITEMIND QUOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prepared for: {builder_name}
Date: {datetime.utcnow().strftime("%d %B %Y")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVE SITES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active Sites: {num_active_sites}
Base Price: {symbol}{active['base_price_per_site']:,.0f}/site/month
Discount: {active['discount_percent']:.0f}%
Your Price: {active['price_per_site_formatted']}/site/month

Active Monthly: {active['total_monthly_formatted']}

✅ UNLIMITED AI queries
✅ Gemini 3.0 Pro (best AI)
✅ Complete audit trail
✅ WhatsApp + Dashboard
{archive_section}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONTHLY TOTAL: {symbol}{grand_total:,.0f}
ANNUAL TOTAL: {symbol}{grand_total * 12:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return quote


# Singleton instance
pricing_service = PricingService()
