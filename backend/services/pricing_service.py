"""
SiteMind Pricing Service
Simple, transparent pricing. One product, one price.

Philosophy:
- One product with EVERYTHING included
- No confusing tiers
- No token/query limits - UNLIMITED usage
- Volume discounts for multiple sites
- Founding partner program for pilots
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class PricingConfig:
    """
    SiteMind Pricing Configuration
    
    Base: $500/site/month (₹41,500)
    UNLIMITED queries - no limits, no upsells
    """
    
    # Base pricing
    BASE_PRICE_USD = 500
    BASE_PRICE_INR = 41_500  # ~$500 at 83 INR/USD
    
    # Volume discounts (simple tiers)
    VOLUME_DISCOUNTS = {
        3: 0.10,    # 10% off for 3+ sites
        6: 0.15,    # 15% off for 6+ sites
        10: 0.25,   # 25% off for 10+ sites
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
    
    Simple pricing:
    - $500/site/month
    - 3+ sites: 10% off
    - 6+ sites: 15% off  
    - 10+ sites: 25% off
    - Unlimited usage, no query limits
    """
    
    def __init__(self):
        self.config = PricingConfig()
        self._pilot_partners: Dict[str, Dict] = {}
        self._pilots_used = 0
    
    def get_price(
        self,
        num_sites: int,
        is_founding_partner: bool = False,
        currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Calculate price for a given number of sites
        
        Args:
            num_sites: Number of sites
            is_founding_partner: Whether they're a founding partner (20% off forever)
            currency: USD or INR
        """
        base_price = self.config.BASE_PRICE_USD if currency == "USD" else self.config.BASE_PRICE_INR
        
        # Apply volume discount
        volume_discount = 0
        volume_tier = None
        for threshold, discount in sorted(self.config.VOLUME_DISCOUNTS.items(), reverse=True):
            if num_sites >= threshold:
                volume_discount = discount
                volume_tier = threshold
                break
        
        # Apply founding partner discount (stacks with volume for founding partners)
        if is_founding_partner:
            # Founding partners get the BETTER of volume or founding discount
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
        
        # Calculate prices
        price_per_site = base_price * (1 - total_discount)
        total_monthly = price_per_site * num_sites
        total_annual = total_monthly * 12
        
        # Savings calculation
        savings_per_site = base_price - price_per_site
        total_savings_monthly = savings_per_site * num_sites
        
        # Format currency
        symbol = "$" if currency == "USD" else "₹"
        
        return {
            "num_sites": num_sites,
            "currency": currency,
            "base_price_per_site": base_price,
            "base_price_formatted": f"{symbol}{base_price:,.0f}",
            "discount_percent": total_discount * 100,
            "discount_applied": f"{total_discount * 100:.0f}%" if total_discount > 0 else "None",
            "discount_reason": discount_reason,
            "price_per_site": price_per_site,
            "price_per_site_formatted": f"{symbol}{price_per_site:,.0f}",
            "total_monthly": total_monthly,
            "total_monthly_formatted": f"{symbol}{total_monthly:,.0f}",
            "total_annual": total_annual,
            "total_annual_formatted": f"{symbol}{total_annual:,.0f}",
            "savings_per_site": savings_per_site,
            "savings_per_site_formatted": f"{symbol}{savings_per_site:,.0f}" if savings_per_site > 0 else "N/A",
            "total_savings_monthly": total_savings_monthly,
            "total_savings_formatted": f"{symbol}{total_savings_monthly:,.0f}/month" if total_savings_monthly > 0 else "N/A",
            "usage": "UNLIMITED - No query limits",
        }
    
    def get_pricing_table(self, currency: str = "USD") -> Dict[str, Any]:
        """
        Get the complete pricing table for display
        """
        symbol = "$" if currency == "USD" else "₹"
        base = self.config.BASE_PRICE_USD if currency == "USD" else self.config.BASE_PRICE_INR
        
        return {
            "base_price": f"{symbol}{base:,.0f}/site/month",
            "volume_discounts": [
                {
                    "sites": "1-2 sites",
                    "discount": "0%",
                    "price_per_site": f"{symbol}{base:,.0f}",
                },
                {
                    "sites": "3-5 sites",
                    "discount": "10%",
                    "price_per_site": f"{symbol}{base * 0.90:,.0f}",
                },
                {
                    "sites": "6-9 sites",
                    "discount": "15%",
                    "price_per_site": f"{symbol}{base * 0.85:,.0f}",
                },
                {
                    "sites": "10+ sites",
                    "discount": "25%",
                    "price_per_site": f"{symbol}{base * 0.75:,.0f}",
                },
            ],
            "whats_included": [
                "✅ UNLIMITED AI queries",
                "✅ Unlimited engineers per site",
                "✅ Blueprint analysis (Gemini 2.5 Pro)",
                "✅ Site photo verification",
                "✅ Complete audit trail with citations",
                "✅ Weekly & monthly reports",
                "✅ Conflict detection",
                "✅ ROI dashboard",
                "✅ WhatsApp support",
                "✅ No hidden fees, no query limits",
            ],
            "terms": [
                "Monthly billing, cancel anytime",
                "Each site = separate subscription",
                "Volume discounts applied automatically",
                "Annual billing available (2 months free)",
            ],
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
        
        # Calculate pilot value
        pilot_value_usd = self.config.BASE_PRICE_USD * len(sites) * 3
        pilot_value_inr = self.config.BASE_PRICE_INR * len(sites) * 3
        
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
            "pilot_value_usd": f"${pilot_value_usd:,}",
            "pilot_value_inr": f"₹{pilot_value_inr:,}",
            "founding_partner_discount": "20% forever after pilot",
        }
        
        self._pilot_partners[builder_id] = pilot
        self._pilots_used += 1
        
        # Calculate post-pilot pricing
        post_pilot_pricing = self.get_price(len(sites), is_founding_partner=True)
        
        return {
            "success": True,
            "pilot": pilot,
            "message": f"🎉 Welcome to the Founding Partner Program, {builder_name}!",
            "what_you_get": [
                f"✅ Full SiteMind access for {len(sites)} sites",
                "✅ 3 months completely FREE",
                "✅ UNLIMITED queries - no limits",
                "✅ Direct WhatsApp access to founder",
                "✅ 20% discount forever after pilot",
            ],
            "what_we_ask": [
                "📝 Weekly 15-min feedback call",
                "📸 Permission to use as case study (optional)",
                "🤝 Honest review after pilot",
            ],
            "pilot_value": f"${pilot_value_usd:,} ({pilot_value_inr:,} INR) - FREE for you",
            "after_pilot": {
                "price_per_site": post_pilot_pricing["price_per_site_formatted"],
                "total_monthly": post_pilot_pricing["total_monthly_formatted"],
                "discount": "20% founding partner discount (forever)",
            },
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
        currency: str = "USD",
    ) -> str:
        """
        Generate a shareable quote for a builder
        """
        pricing = self.get_price(num_sites, is_founding_partner, currency)
        symbol = "$" if currency == "USD" else "₹"
        
        discount_line = ""
        if pricing["discount_percent"] > 0:
            discount_line = f"""
Discount: {pricing['discount_applied']} ({pricing['discount_reason']})
You Save: {pricing['total_savings_formatted']}
"""
        
        quote = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        SITEMIND QUOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prepared for: {builder_name}
Date: {datetime.utcnow().strftime("%d %B %Y")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRICING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sites: {num_sites}
Base Price: {pricing['base_price_formatted']}/site/month
{discount_line}
Price per site: {pricing['price_per_site_formatted']}/month

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONTHLY TOTAL: {pricing['total_monthly_formatted']}
ANNUAL TOTAL: {pricing['total_annual_formatted']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ UNLIMITED AI queries (no limits!)
✅ Unlimited engineers per site
✅ Blueprint analysis (Gemini 2.5 Pro)
✅ Site photo verification
✅ Complete audit trail with citations
✅ Weekly & monthly reports
✅ Conflict detection
✅ ROI dashboard
✅ WhatsApp support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VOLUME DISCOUNTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3+ sites:  10% off
6+ sites:  15% off
10+ sites: 25% off

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TERMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Monthly billing, cancel anytime
• Each construction site = 1 subscription
• No hidden fees, no query limits
• Annual billing: 2 months free

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions? WhatsApp: +91-XXXXXXXXXX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return quote


# Singleton instance
pricing_service = PricingService()
