"""
SiteMind Pricing Service
Observable-metric based pricing (can't be gamed!)

PRICING PHILOSOPHY:
Price based on things WE CAN SEE, not what they tell us.
Nobody will honestly tell you their project value!

OBSERVABLE METRICS:
1. Number of buildings/towers (we see from drawings)
2. Number of active users (we track phone numbers)
3. Query volume (we count every message)

CAN'T BE GAMED:
- We know exactly how many users are active
- We count every query
- We process their drawings so we know building count
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class PricingService:
    """
    Pricing based on observable, verifiable metrics
    """
    
    def __init__(self):
        # =================================================================
        # SIMPLE PRICING: Buildings + Users
        # =================================================================
        
        # Base price per project (includes 1 building, 5 users)
        self.BASE_PRICE_USD = 500
        
        # Per additional building (we count from drawings)
        self.PER_BUILDING_USD = 200
        
        # Per additional user after first 5 (we track phone numbers)
        self.PER_USER_USD = 30
        
        # =================================================================
        # USAGE-BASED COMPONENT (Optional add-on)
        # =================================================================
        
        # Included queries per month
        self.INCLUDED_QUERIES = 1000
        
        # Overage (if they want to pay for more)
        self.PER_QUERY_OVERAGE_USD = 0.05  # $0.05 per query over limit
        
        # =================================================================
        # VOLUME DISCOUNTS
        # =================================================================
        
        # Discount by total buildings across all projects
        self.BUILDING_DISCOUNTS = {
            5: 0.05,    # 5+ buildings total: 5% off
            10: 0.10,   # 10+ buildings: 10% off
            20: 0.15,   # 20+ buildings: 15% off
            50: 0.20,   # 50+ buildings: 20% off
        }
        
        # =================================================================
        # PILOT & ARCHIVE
        # =================================================================
        
        self.PILOT_MONTHS = 3
        self.ARCHIVE_MONTHLY_USD = 100  # Flat rate for archived projects
        self.ARCHIVE_ONETIME_MONTHS = 12  # Pay 12 months, keep forever
        
        # USD to INR
        self.USD_TO_INR = 83
    
    # =========================================================================
    # MAIN PRICING CALCULATION
    # =========================================================================
    
    def calculate_project_price(
        self,
        num_buildings: int = 1,
        num_users: int = 5,
    ) -> Dict[str, Any]:
        """
        Calculate price for a single project
        
        Args:
            num_buildings: Number of buildings/towers (we verify from drawings)
            num_users: Number of WhatsApp users (we track exactly)
        """
        # Base price
        base = self.BASE_PRICE_USD
        
        # Additional buildings (first one included)
        extra_buildings = max(0, num_buildings - 1)
        buildings_cost = extra_buildings * self.PER_BUILDING_USD
        
        # Additional users (first 5 included)
        extra_users = max(0, num_users - 5)
        users_cost = extra_users * self.PER_USER_USD
        
        # Total
        monthly_usd = base + buildings_cost + users_cost
        monthly_inr = monthly_usd * self.USD_TO_INR
        
        return {
            "base_usd": base,
            "buildings": {
                "count": num_buildings,
                "extra": extra_buildings,
                "cost_usd": buildings_cost,
            },
            "users": {
                "count": num_users,
                "included": 5,
                "extra": extra_users,
                "cost_usd": users_cost,
            },
            "monthly_usd": monthly_usd,
            "monthly_inr": monthly_inr,
            "annual_usd": monthly_usd * 12,
            "annual_inr": monthly_inr * 12,
            "breakdown": self._format_breakdown(base, extra_buildings, buildings_cost, extra_users, users_cost),
        }
    
    def calculate_company_total(
        self,
        projects: List[Dict],
        is_pilot: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate total for a company with multiple projects
        
        Args:
            projects: List of {name, buildings, users}
            is_pilot: Pilot program (free for 3 months)
        """
        if is_pilot:
            return {
                "projects": projects,
                "total_monthly_usd": 0,
                "total_monthly_inr": 0,
                "discount_percent": 100,
                "status": "pilot",
                "note": f"FREE for {self.PILOT_MONTHS} months",
            }
        
        # Calculate each project
        project_prices = []
        total_buildings = 0
        total_monthly = 0
        
        for proj in projects:
            buildings = proj.get("buildings", 1)
            users = proj.get("users", 5)
            
            price = self.calculate_project_price(buildings, users)
            
            project_prices.append({
                "name": proj.get("name", "Project"),
                **price,
            })
            
            total_buildings += buildings
            total_monthly += price["monthly_usd"]
        
        # Apply volume discount based on total buildings
        discount_percent = 0
        for min_buildings, discount in sorted(self.BUILDING_DISCOUNTS.items(), reverse=True):
            if total_buildings >= min_buildings:
                discount_percent = discount * 100
                break
        
        discount_amount = total_monthly * (discount_percent / 100)
        final_monthly = total_monthly - discount_amount
        
        return {
            "projects": project_prices,
            "totals": {
                "buildings": total_buildings,
                "users": sum(p.get("users", 5) for p in projects),
            },
            "subtotal_monthly_usd": total_monthly,
            "volume_discount": {
                "reason": f"{total_buildings} total buildings",
                "percent": discount_percent,
                "amount_usd": discount_amount,
            },
            "total_monthly_usd": final_monthly,
            "total_monthly_inr": final_monthly * self.USD_TO_INR,
            "total_annual_usd": final_monthly * 12,
            "total_annual_inr": final_monthly * 12 * self.USD_TO_INR,
        }
    
    def _format_breakdown(
        self,
        base: int,
        extra_buildings: int,
        buildings_cost: int,
        extra_users: int,
        users_cost: int,
    ) -> str:
        """Format pricing breakdown"""
        lines = [f"Base (1 building, 5 users): ${base}"]
        
        if buildings_cost > 0:
            lines.append(f"+{extra_buildings} buildings × ${self.PER_BUILDING_USD} = ${buildings_cost}")
        
        if users_cost > 0:
            lines.append(f"+{extra_users} users × ${self.PER_USER_USD} = ${users_cost}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # PRICING EXAMPLES
    # =========================================================================
    
    def get_pricing_examples(self) -> List[Dict]:
        """Real-world pricing examples"""
        return [
            {
                "scenario": "Small Project",
                "description": "1 building, 5 users",
                **self.calculate_project_price(1, 5),
            },
            {
                "scenario": "Medium Project",
                "description": "3 buildings, 10 users",
                **self.calculate_project_price(3, 10),
            },
            {
                "scenario": "Large Township",
                "description": "12 buildings, 25 users",
                **self.calculate_project_price(12, 25),
            },
            {
                "scenario": "Mega Project",
                "description": "25 buildings, 50 users",
                **self.calculate_project_price(25, 50),
            },
        ]
    
    def get_pricing_table(self) -> str:
        """Get formatted pricing table"""
        return """
**SiteMind Pricing**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASE: $500/month per project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Includes:
• 1 building
• 5 team members
• 1,000 queries/month
• Unlimited storage
• Full features

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADDITIONAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• +$200/month per additional building
• +$30/month per additional user

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VOLUME DISCOUNTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 5+ buildings: 5% off
• 10+ buildings: 10% off
• 20+ buildings: 15% off
• 50+ buildings: 20% off

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Small (1 bldg, 5 users):     $500/mo
Medium (3 bldg, 10 users):   $1,050/mo
Township (12 bldg, 25 users): $2,900/mo
Mega (25 bldg, 50 users):    $6,550/mo
"""
    
    # =========================================================================
    # ARCHIVE
    # =========================================================================
    
    def get_archive_price(self) -> Dict[str, Any]:
        """Archive pricing for completed projects"""
        monthly = self.ARCHIVE_MONTHLY_USD
        onetime = monthly * self.ARCHIVE_ONETIME_MONTHS
        
        return {
            "monthly": {
                "usd": monthly,
                "inr": monthly * self.USD_TO_INR,
                "description": "Keep access to all project history",
            },
            "one_time": {
                "usd": onetime,
                "inr": onetime * self.USD_TO_INR,
                "description": f"Pay {self.ARCHIVE_ONETIME_MONTHS} months, keep forever",
            },
            "benefits": [
                "Full search of all decisions",
                "Export anytime",
                "Legal documentation",
                "Reference for future projects",
            ],
        }
    
    # =========================================================================
    # QUOTES
    # =========================================================================
    
    def generate_quote(
        self,
        company_name: str,
        projects: List[Dict],
        is_pilot: bool = False,
    ) -> Dict[str, Any]:
        """Generate formal quote"""
        pricing = self.calculate_company_total(projects, is_pilot)
        
        return {
            "quote_id": f"SM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company": company_name,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "valid_days": 30,
            "pricing": pricing,
            "includes": [
                "Unlimited WhatsApp queries",
                "Blueprint analysis",
                "Photo analysis",
                "Complete audit trail",
                "All team roles",
                "ROI reporting",
                "24/7 support",
                "Personal onboarding",
            ],
        }
    
    def format_quote_whatsapp(self, quote: Dict) -> str:
        """Format quote for WhatsApp"""
        p = quote["pricing"]
        
        msg = f"""**SiteMind Quote**
{quote['company']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Projects:**
"""
        for proj in p.get("projects", []):
            msg += f"• {proj['name']}: {proj['buildings']['count']} bldg, {proj['users']['count']} users → ${proj['monthly_usd']}/mo\n"
        
        vd = p.get("volume_discount", {})
        if vd.get("percent", 0) > 0:
            msg += f"\n**Volume Discount:** {vd['percent']:.0f}% off ({vd['reason']})\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Total: ${p['total_monthly_usd']:,.0f}/month**
(₹{p['total_monthly_inr']:,.0f}/month)

**Annual: ${p['total_annual_usd']:,.0f}**
(₹{p['total_annual_inr']:,.0f})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quote: {quote['quote_id']}
Valid: {quote['valid_days']} days

_Includes: Onboarding, training, 24/7 support_
"""
        return msg
    
    # =========================================================================
    # PILOT
    # =========================================================================
    
    def get_pilot_info(self) -> Dict[str, Any]:
        """Pilot program details"""
        return {
            "duration": f"{self.PILOT_MONTHS} months FREE",
            "slots": 3,
            "includes": [
                "Full access, all features",
                "Unlimited projects",
                "Personal onboarding",
                "Direct founder access",
            ],
            "requirements": [
                "Use on at least 1 real project",
                "Provide honest feedback",
                "Bi-weekly 30-min calls",
            ],
            "after_pilot": "20% founding customer discount forever",
        }


# Singleton instance  
pricing_service = PricingService()
