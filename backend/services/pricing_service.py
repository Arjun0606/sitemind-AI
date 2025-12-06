"""
SiteMind Pricing Service
Simple, transparent pricing. One product, one price.

Philosophy:
- One product with EVERYTHING included
- No confusing tiers
- Usage-based upsell for heavy users (query tokens)
- Volume discounts for large builders
- Founding partner program for pilots
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class PricingConfig:
    """
    SiteMind Pricing Configuration
    
    Base: ₹25,000/site/month (~$300)
    Includes 500 queries/month
    Everything else unlimited
    """
    
    # Base pricing (INR)
    BASE_PRICE_INR = 25_000
    BASE_PRICE_USD = 300
    
    # Included queries per month
    INCLUDED_QUERIES = 500
    
    # Query packs for heavy users
    QUERY_PACKS = {
        "standard": {"queries": 500, "price_inr": 5_000, "price_usd": 60},
        "heavy": {"queries": 1500, "price_inr": 12_000, "price_usd": 145},
        "unlimited": {"queries": float('inf'), "price_inr": 15_000, "price_usd": 180, "recurring": True},
    }
    
    # Volume discounts
    VOLUME_DISCOUNTS = {
        10: 0.10,   # 10% off for 10+ sites
        25: 0.20,   # 20% off for 25+ sites
        50: 0.25,   # 25% off for 50+ sites
    }
    
    # Founding partner discount (forever)
    FOUNDING_PARTNER_DISCOUNT = 0.20  # 20% off forever
    
    # Pilot program
    PILOT_DURATION_MONTHS = 3
    PILOT_MAX_SITES = 5
    PILOT_SLOTS_TOTAL = 3  # Only 3 founding partners


class PilotStatus(str, Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    CONVERTED = "converted"


class PricingService:
    """
    Handles all pricing calculations and pilot program management
    """
    
    def __init__(self):
        self.config = PricingConfig()
        self._pilot_partners: Dict[str, Dict] = {}
        self._pilots_used = 0
    
    def get_price(
        self,
        num_sites: int,
        is_founding_partner: bool = False,
        currency: str = "INR"
    ) -> Dict[str, Any]:
        """
        Calculate price for a given number of sites
        
        Args:
            num_sites: Number of sites
            is_founding_partner: Whether they're a founding partner (20% off forever)
            currency: INR or USD
        """
        base_price = self.config.BASE_PRICE_INR if currency == "INR" else self.config.BASE_PRICE_USD
        
        # Apply volume discount
        volume_discount = 0
        for threshold, discount in sorted(self.config.VOLUME_DISCOUNTS.items(), reverse=True):
            if num_sites >= threshold:
                volume_discount = discount
                break
        
        # Apply founding partner discount
        founding_discount = self.config.FOUNDING_PARTNER_DISCOUNT if is_founding_partner else 0
        
        # Total discount (volume + founding don't stack, take the better one)
        total_discount = max(volume_discount, founding_discount)
        
        # Calculate prices
        price_per_site = base_price * (1 - total_discount)
        total_monthly = price_per_site * num_sites
        total_annual = total_monthly * 12
        
        # Format currency
        symbol = "₹" if currency == "INR" else "$"
        
        return {
            "num_sites": num_sites,
            "currency": currency,
            "base_price_per_site": base_price,
            "discount_applied": f"{total_discount * 100:.0f}%",
            "discount_reason": "founding_partner" if founding_discount > volume_discount else f"volume_{num_sites}_sites",
            "price_per_site": price_per_site,
            "price_per_site_formatted": f"{symbol}{price_per_site:,.0f}",
            "total_monthly": total_monthly,
            "total_monthly_formatted": f"{symbol}{total_monthly:,.0f}",
            "total_annual": total_annual,
            "total_annual_formatted": f"{symbol}{total_annual:,.0f}",
            "included_queries_per_site": self.config.INCLUDED_QUERIES,
            "total_included_queries": self.config.INCLUDED_QUERIES * num_sites,
        }
    
    def get_query_pack_options(self, currency: str = "INR") -> Dict[str, Any]:
        """
        Get available query pack options for upsell
        """
        symbol = "₹" if currency == "INR" else "$"
        price_key = "price_inr" if currency == "INR" else "price_usd"
        
        packs = {}
        for name, details in self.config.QUERY_PACKS.items():
            queries = details["queries"]
            price = details[price_key]
            packs[name] = {
                "queries": "Unlimited" if queries == float('inf') else queries,
                "price": price,
                "price_formatted": f"{symbol}{price:,.0f}",
                "recurring": details.get("recurring", False),
                "cost_per_query": None if queries == float('inf') else f"{symbol}{price/queries:.1f}",
            }
        
        return {
            "included_free": self.config.INCLUDED_QUERIES,
            "packs": packs,
            "note": "Most sites use 200-400 queries/month. Packs are for power users only.",
        }
    
    def create_pilot(
        self,
        builder_id: str,
        builder_name: str,
        contact_name: str,
        contact_phone: str,
        sites: list,
    ) -> Dict[str, Any]:
        """
        Create a founding partner pilot (3 months free)
        
        Limited to 3 builders total!
        """
        # Check if slots available
        if self._pilots_used >= self.config.PILOT_SLOTS_TOTAL:
            return {
                "success": False,
                "error": "All founding partner slots are taken",
                "message": "We only offer 3 founding partner slots. Regular pricing applies.",
            }
        
        # Check site limit
        if len(sites) > self.config.PILOT_MAX_SITES:
            return {
                "success": False,
                "error": f"Pilot limited to {self.config.PILOT_MAX_SITES} sites",
                "message": f"Please select up to {self.config.PILOT_MAX_SITES} sites for the pilot.",
            }
        
        # Create pilot
        pilot_id = f"pilot_{builder_id}"
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=90)  # 3 months
        
        pilot = {
            "pilot_id": pilot_id,
            "builder_id": builder_id,
            "builder_name": builder_name,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "sites": sites,
            "num_sites": len(sites),
            "status": PilotStatus.ACTIVE,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "founding_partner_discount": "20% forever after pilot",
            "pilot_value": f"₹{self.config.BASE_PRICE_INR * len(sites) * 3:,.0f} (3 months free)",
        }
        
        self._pilot_partners[builder_id] = pilot
        self._pilots_used += 1
        
        return {
            "success": True,
            "pilot": pilot,
            "message": f"🎉 Welcome to the Founding Partner Program, {builder_name}!",
            "what_you_get": [
                f"✅ Full SiteMind access for {len(sites)} sites",
                "✅ 3 months completely FREE",
                "✅ Unlimited queries during pilot",
                "✅ Direct WhatsApp access to founder",
                "✅ 20% discount forever after pilot",
            ],
            "what_we_ask": [
                "📝 Weekly 15-min feedback call",
                "📸 Permission to use as case study (optional)",
                "🤝 Honest review after pilot",
            ],
            "after_pilot": self.get_price(len(sites), is_founding_partner=True),
            "slots_remaining": self.config.PILOT_SLOTS_TOTAL - self._pilots_used,
        }
    
    def get_pilot_status(self) -> Dict[str, Any]:
        """
        Get status of pilot program
        """
        return {
            "total_slots": self.config.PILOT_SLOTS_TOTAL,
            "slots_used": self._pilots_used,
            "slots_remaining": self.config.PILOT_SLOTS_TOTAL - self._pilots_used,
            "active_pilots": [
                {
                    "builder_name": p["builder_name"],
                    "num_sites": p["num_sites"],
                    "end_date": p["end_date"],
                    "status": p["status"],
                }
                for p in self._pilot_partners.values()
            ],
        }
    
    def generate_quote(
        self,
        builder_name: str,
        num_sites: int,
        is_founding_partner: bool = False,
    ) -> str:
        """
        Generate a shareable quote for a builder
        """
        pricing = self.get_price(num_sites, is_founding_partner)
        
        quote = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        SITEMIND QUOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prepared for: {builder_name}
Date: {datetime.utcnow().strftime("%d %B %Y")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUBSCRIPTION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sites: {num_sites}
Price per site: {pricing['price_per_site_formatted']}/month
Discount: {pricing['discount_applied']}

MONTHLY TOTAL: {pricing['total_monthly_formatted']}
ANNUAL TOTAL: {pricing['total_annual_formatted']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INCLUDED (per site)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ {pricing['included_queries_per_site']} AI queries/month
✅ Unlimited engineers
✅ Blueprint analysis
✅ Site photo verification  
✅ Complete audit trail
✅ Weekly & monthly reports
✅ Conflict detection
✅ ROI dashboard
✅ WhatsApp support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TERMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Monthly billing, cancel anytime
• Each site = separate subscription
• Query packs available if needed
• Volume discounts applied automatically

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions? WhatsApp: +91-XXXXXXXXXX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return quote


# Singleton instance
pricing_service = PricingService()

