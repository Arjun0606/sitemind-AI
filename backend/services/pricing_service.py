"""
SiteMind Pricing Service
Value-based enterprise pricing for construction projects

PRICING PHILOSOPHY:
- Price based on VALUE delivered, not flat fee
- Larger projects = more risk = more value from SiteMind
- More complexity = more queries = more savings

PRICING FACTORS:
1. Project Value (development cost)
2. Complexity (number of buildings/units)
3. Number of users
4. Project duration

TIERS:
- Starter: Small projects < ₹50 Cr
- Professional: Medium ₹50-200 Cr
- Enterprise: Large ₹200-500 Cr
- Premium: Mega > ₹500 Cr
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ProjectTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


@dataclass
class TierPricing:
    name: str
    min_value_cr: float
    max_value_cr: float
    base_price_usd: int
    per_building_usd: int
    per_user_usd: int
    description: str


class PricingService:
    """
    Value-based pricing for SiteMind
    """
    
    def __init__(self):
        # Define tiers
        self.TIERS = {
            ProjectTier.STARTER: TierPricing(
                name="Starter",
                min_value_cr=0,
                max_value_cr=50,
                base_price_usd=500,
                per_building_usd=0,
                per_user_usd=0,
                description="Small projects, single buildings",
            ),
            ProjectTier.PROFESSIONAL: TierPricing(
                name="Professional",
                min_value_cr=50,
                max_value_cr=200,
                base_price_usd=1000,
                per_building_usd=200,
                per_user_usd=25,
                description="Medium projects, multiple buildings",
            ),
            ProjectTier.ENTERPRISE: TierPricing(
                name="Enterprise",
                min_value_cr=200,
                max_value_cr=500,
                base_price_usd=2500,
                per_building_usd=300,
                per_user_usd=20,
                description="Large complexes, townships",
            ),
            ProjectTier.PREMIUM: TierPricing(
                name="Premium",
                min_value_cr=500,
                max_value_cr=float('inf'),
                base_price_usd=5000,
                per_building_usd=400,
                per_user_usd=15,
                description="Mega projects, dedicated support",
            ),
        }
        
        # Volume discounts (by total monthly spend)
        self.VOLUME_DISCOUNTS = {
            5000: 0.05,    # $5K+/mo: 5% off
            10000: 0.10,   # $10K+/mo: 10% off
            25000: 0.15,   # $25K+/mo: 15% off
            50000: 0.20,   # $50K+/mo: 20% off
        }
        
        # Pilot program
        self.PILOT_DURATION_MONTHS = 3
        self.PILOT_DISCOUNT = 1.0  # 100% off (free)
        
        # Archive pricing
        self.ARCHIVE_PERCENT = 0.10  # 10% of active price
        self.ARCHIVE_MIN_USD = 100
        
        # USD to INR
        self.USD_TO_INR = 83
    
    # =========================================================================
    # TIER DETERMINATION
    # =========================================================================
    
    def get_tier(self, project_value_cr: float) -> ProjectTier:
        """Determine tier based on project value"""
        for tier, pricing in self.TIERS.items():
            if pricing.min_value_cr <= project_value_cr < pricing.max_value_cr:
                return tier
        return ProjectTier.PREMIUM
    
    # =========================================================================
    # PRICING CALCULATION
    # =========================================================================
    
    def calculate_project_price(
        self,
        project_value_cr: float,
        num_buildings: int = 1,
        num_users: int = 5,
        duration_months: int = 24,
    ) -> Dict[str, Any]:
        """
        Calculate price for a single project
        
        Args:
            project_value_cr: Project development cost in Crores (₹)
            num_buildings: Number of buildings/towers
            num_users: Number of team members using SiteMind
            duration_months: Expected project duration
        """
        tier = self.get_tier(project_value_cr)
        tier_pricing = self.TIERS[tier]
        
        # Base calculation
        base = tier_pricing.base_price_usd
        buildings_cost = max(0, num_buildings - 1) * tier_pricing.per_building_usd
        users_cost = max(0, num_users - 5) * tier_pricing.per_user_usd  # First 5 users included
        
        monthly_usd = base + buildings_cost + users_cost
        monthly_inr = monthly_usd * self.USD_TO_INR
        
        # Project value percentage (for context)
        project_value_inr = project_value_cr * 10000000  # Cr to INR
        monthly_percent = (monthly_inr / project_value_inr) * 100
        
        # Total project cost
        total_usd = monthly_usd * duration_months
        total_inr = total_usd * self.USD_TO_INR
        
        # ROI calculation (conservative estimate)
        # Assume SiteMind saves 0.1% of project cost through error prevention
        estimated_savings_inr = project_value_inr * 0.001  # 0.1% savings
        roi_multiple = estimated_savings_inr / total_inr
        
        return {
            "tier": tier.value,
            "tier_name": tier_pricing.name,
            
            "project": {
                "value_cr": project_value_cr,
                "value_inr": project_value_inr,
                "buildings": num_buildings,
                "users": num_users,
                "duration_months": duration_months,
            },
            
            "pricing": {
                "base_usd": base,
                "buildings_usd": buildings_cost,
                "users_usd": users_cost,
                "monthly_usd": monthly_usd,
                "monthly_inr": monthly_inr,
                "monthly_percent_of_value": round(monthly_percent, 4),
            },
            
            "total": {
                "usd": total_usd,
                "inr": total_inr,
                "percent_of_value": round((total_inr / project_value_inr) * 100, 3),
            },
            
            "roi": {
                "estimated_savings_inr": estimated_savings_inr,
                "roi_multiple": round(roi_multiple, 1),
                "note": "Based on 0.1% error prevention savings (very conservative)",
            },
            
            "breakdown": self._format_breakdown(tier_pricing, base, buildings_cost, users_cost, num_buildings, num_users),
        }
    
    def calculate_company_price(
        self,
        projects: List[Dict],
        is_pilot: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate total price for a company with multiple projects
        
        Args:
            projects: List of project dicts with value_cr, buildings, users
            is_pilot: Whether this is a pilot customer
        """
        if is_pilot:
            return {
                "total_monthly_usd": 0,
                "total_monthly_inr": 0,
                "discount_percent": 100,
                "plan": "pilot",
                "note": f"Pilot program - FREE for {self.PILOT_DURATION_MONTHS} months",
                "projects": projects,
            }
        
        project_prices = []
        total_monthly = 0
        
        for proj in projects:
            price = self.calculate_project_price(
                project_value_cr=proj.get("value_cr", 50),
                num_buildings=proj.get("buildings", 1),
                num_users=proj.get("users", 5),
            )
            project_prices.append({
                "name": proj.get("name", "Project"),
                **price,
            })
            total_monthly += price["pricing"]["monthly_usd"]
        
        # Apply volume discount
        discount_percent = 0
        for threshold, discount in sorted(self.VOLUME_DISCOUNTS.items(), reverse=True):
            if total_monthly >= threshold:
                discount_percent = discount * 100
                break
        
        discount_amount = total_monthly * (discount_percent / 100)
        final_monthly = total_monthly - discount_amount
        
        return {
            "projects": project_prices,
            "subtotal_monthly_usd": total_monthly,
            "volume_discount_percent": discount_percent,
            "discount_amount_usd": discount_amount,
            "total_monthly_usd": final_monthly,
            "total_monthly_inr": final_monthly * self.USD_TO_INR,
            "total_annual_usd": final_monthly * 12,
            "total_annual_inr": final_monthly * 12 * self.USD_TO_INR,
        }
    
    def _format_breakdown(
        self,
        tier: TierPricing,
        base: int,
        buildings_cost: int,
        users_cost: int,
        num_buildings: int,
        num_users: int,
    ) -> str:
        """Format pricing breakdown"""
        lines = [f"{tier.name} tier base: ${base}"]
        
        if buildings_cost > 0:
            extra_buildings = num_buildings - 1
            lines.append(f"Additional buildings ({extra_buildings} × ${tier.per_building_usd}): ${buildings_cost}")
        
        if users_cost > 0:
            extra_users = num_users - 5
            lines.append(f"Additional users ({extra_users} × ${tier.per_user_usd}): ${users_cost}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # PRICING EXAMPLES
    # =========================================================================
    
    def get_pricing_examples(self) -> List[Dict]:
        """Get pricing examples for different scenarios"""
        examples = [
            {
                "scenario": "Small Residential Building",
                "description": "Single 15-floor building, ₹35 Cr project",
                **self.calculate_project_price(35, 1, 5),
            },
            {
                "scenario": "Mid-size Commercial Complex",
                "description": "3 buildings, ₹120 Cr project, 12 team members",
                **self.calculate_project_price(120, 3, 12),
            },
            {
                "scenario": "Large Township",
                "description": "12 buildings, ₹350 Cr project, 25 team members",
                **self.calculate_project_price(350, 12, 25),
            },
            {
                "scenario": "Mega Integrated Township",
                "description": "25 buildings, ₹800 Cr project, 50 team members",
                **self.calculate_project_price(800, 25, 50),
            },
        ]
        
        return examples
    
    def get_tier_comparison(self) -> List[Dict]:
        """Get tier comparison table"""
        return [
            {
                "tier": tier.value,
                "name": pricing.name,
                "project_value": f"₹{pricing.min_value_cr}-{pricing.max_value_cr if pricing.max_value_cr != float('inf') else '500+'} Cr",
                "base_price": f"${pricing.base_price_usd}/mo",
                "per_building": f"+${pricing.per_building_usd}/building" if pricing.per_building_usd else "Included",
                "per_user": f"+${pricing.per_user_usd}/user (after 5)" if pricing.per_user_usd else "Included",
                "description": pricing.description,
            }
            for tier, pricing in self.TIERS.items()
        ]
    
    # =========================================================================
    # ARCHIVE PRICING
    # =========================================================================
    
    def calculate_archive_price(self, active_monthly_usd: float) -> Dict[str, Any]:
        """Calculate archive price for a completed project"""
        archive_monthly = max(
            self.ARCHIVE_MIN_USD,
            active_monthly_usd * self.ARCHIVE_PERCENT
        )
        
        return {
            "monthly_usd": archive_monthly,
            "monthly_inr": archive_monthly * self.USD_TO_INR,
            "annual_usd": archive_monthly * 12,
            "discount_annual": "2 months free with annual",
            "one_time_usd": archive_monthly * 10,  # 10 months = lifetime
            "one_time_note": "Pay 10 months, keep forever",
        }
    
    # =========================================================================
    # QUOTES
    # =========================================================================
    
    def generate_quote(
        self,
        company_name: str,
        projects: List[Dict],
        is_pilot: bool = False,
        valid_days: int = 30,
    ) -> Dict[str, Any]:
        """Generate a formal quote"""
        pricing = self.calculate_company_price(projects, is_pilot)
        
        total_value = sum(p.get("value_cr", 0) for p in projects) * 10000000
        total_monthly_inr = pricing.get("total_monthly_inr", 0)
        
        quote = {
            "quote_id": f"SM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company": company_name,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "valid_until": f"{valid_days} days",
            "pricing": pricing,
            "value_proposition": {
                "total_project_value": f"₹{total_value/10000000:.0f} Cr",
                "sitemind_cost_percent": f"{(total_monthly_inr * 12 / total_value) * 100:.3f}% of project value annually",
                "estimated_savings": f"₹{total_value * 0.001 / 100000:.1f} Lakhs (0.1% error prevention)",
            },
            "includes": [
                "Unlimited queries via WhatsApp",
                "Blueprint analysis & Q&A",
                "Full team access (PMs, Engineers, Consultants)",
                "Complete audit trail with citations",
                "ROI reporting",
                "24/7 WhatsApp support",
                "Personal onboarding & training",
            ],
            "terms": [
                "Monthly billing, cancel with 30-day notice",
                "Annual payment: 2 months free",
                "14-day free trial available",
            ],
        }
        
        return quote
    
    def format_quote_whatsapp(self, quote: Dict) -> str:
        """Format quote for WhatsApp"""
        p = quote["pricing"]
        v = quote["value_proposition"]
        
        msg = f"""**SiteMind Quote**
{quote['company']}
Quote: {quote['quote_id']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Your Projects:**
"""
        
        for proj in p.get("projects", []):
            msg += f"• {proj.get('name', 'Project')} ({proj['tier_name']}): ${proj['pricing']['monthly_usd']}/mo\n"
        
        if p.get("volume_discount_percent", 0) > 0:
            msg += f"\n**Volume Discount:** {p['volume_discount_percent']:.0f}% off\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Total: ${p['total_monthly_usd']:,.0f}/month**
(₹{p['total_monthly_inr']:,.0f}/month)

**Annual: ${p['total_annual_usd']:,.0f}**
(₹{p['total_annual_inr']:,.0f})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Value:**
• Project Value: {v['total_project_value']}
• SiteMind: {v['sitemind_cost_percent']}
• Est. Savings: {v['estimated_savings']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Valid: {quote['valid_until']}

_Reply to accept or ask questions!_
"""
        return msg
    
    # =========================================================================
    # PILOT PROGRAM
    # =========================================================================
    
    def get_pilot_info(self) -> Dict[str, Any]:
        """Get pilot program information"""
        return {
            "name": "Founder's Pilot Program",
            "duration": f"{self.PILOT_DURATION_MONTHS} months",
            "price": "FREE",
            "slots": 3,
            "what_you_get": [
                "Full access to all features",
                "No project limits",
                "Personal onboarding with founder",
                "Direct WhatsApp access to founder",
                "Shape the product roadmap",
            ],
            "what_we_ask": [
                "Active use on at least 1 real project",
                "Honest feedback (what works, what doesn't)",
                "30-min call every 2 weeks",
                "Testimonial if satisfied (optional)",
            ],
            "after_pilot": "Continue at standard pricing with 20% founding customer discount",
        }


# Singleton instance
pricing_service = PricingService()
