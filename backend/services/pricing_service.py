"""
SiteMind Pricing Service
Flexible project-based pricing for real estate developers

PRICING MODEL:
- Per PROJECT (not per building)
- A project can have 1 tower or 15 towers - same price
- Volume discounts for multiple projects
- Archive tier for completed projects

EXAMPLES:
- Township (15 buildings) = 1 project = $500/mo
- Villas (30 units) = 1 project = $500/mo  
- Single high-rise = 1 project = $500/mo
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class PlanType(str, Enum):
    PILOT = "pilot"           # Free for 3 months
    PROFESSIONAL = "professional"  # Standard pricing
    ARCHIVE = "archive"       # Completed projects


@dataclass
class PricingTier:
    name: str
    base_price_usd: float
    description: str
    features: List[str]


class PricingService:
    """
    Project-based pricing for SiteMind
    """
    
    def __init__(self):
        # Base pricing
        self.BASE_PRICE_USD = 500  # Per project per month
        self.ARCHIVE_PRICE_USD = 50  # Per archived project per month
        self.ARCHIVE_ONETIME_USD = 500  # One-time archive fee
        
        # Volume discounts (by number of ACTIVE projects)
        self.VOLUME_DISCOUNTS = {
            3: 0.10,   # 3+ projects: 10% off
            6: 0.15,   # 6+ projects: 15% off
            10: 0.25,  # 10+ projects: 25% off
            20: 0.30,  # 20+ projects: 30% off
        }
        
        # Pilot program
        self.PILOT_DURATION_MONTHS = 3
        self.PILOT_SLOTS = 3  # First 3 customers
        
        # Track subscriptions
        self._subscriptions: Dict[str, Dict] = {}
    
    # =========================================================================
    # PRICING CALCULATION
    # =========================================================================
    
    def calculate_monthly_cost(
        self,
        active_projects: int,
        archived_projects: int = 0,
        is_pilot: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate monthly cost for a customer
        
        Args:
            active_projects: Number of active projects
            archived_projects: Number of archived projects
            is_pilot: Whether this is a pilot customer
        """
        if is_pilot:
            return {
                "active_cost": 0,
                "archive_cost": 0,
                "total_usd": 0,
                "discount_percent": 100,
                "plan": "pilot",
                "note": "Pilot program - free for 3 months",
            }
        
        # Calculate base cost
        base_cost = active_projects * self.BASE_PRICE_USD
        
        # Apply volume discount
        discount_percent = 0
        for min_projects, discount in sorted(self.VOLUME_DISCOUNTS.items(), reverse=True):
            if active_projects >= min_projects:
                discount_percent = discount * 100
                break
        
        discount_amount = base_cost * (discount_percent / 100)
        active_cost = base_cost - discount_amount
        
        # Archive cost
        archive_cost = archived_projects * self.ARCHIVE_PRICE_USD
        
        total = active_cost + archive_cost
        
        return {
            "active_projects": active_projects,
            "archived_projects": archived_projects,
            "base_cost": base_cost,
            "discount_percent": discount_percent,
            "discount_amount": discount_amount,
            "active_cost": active_cost,
            "archive_cost": archive_cost,
            "total_usd": total,
            "total_inr": total * 83,  # Approximate conversion
            "breakdown": self._get_breakdown(active_projects, archived_projects, discount_percent),
        }
    
    def _get_breakdown(
        self,
        active: int,
        archived: int,
        discount: float,
    ) -> str:
        """Generate human-readable breakdown"""
        lines = []
        
        if active > 0:
            lines.append(f"{active} active project(s) × ${self.BASE_PRICE_USD} = ${active * self.BASE_PRICE_USD}")
            if discount > 0:
                lines.append(f"Volume discount ({discount:.0f}%): -${(active * self.BASE_PRICE_USD) * (discount/100):.0f}")
        
        if archived > 0:
            lines.append(f"{archived} archived project(s) × ${self.ARCHIVE_PRICE_USD} = ${archived * self.ARCHIVE_PRICE_USD}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # PRICING EXAMPLES
    # =========================================================================
    
    def get_pricing_examples(self) -> List[Dict]:
        """Get pricing examples for different scenarios"""
        return [
            {
                "scenario": "Single High-Rise Project",
                "description": "One 40-floor luxury tower",
                "projects": 1,
                **self.calculate_monthly_cost(1),
            },
            {
                "scenario": "Township Development",
                "description": "15 buildings, 2000+ units - still ONE project",
                "projects": 1,
                **self.calculate_monthly_cost(1),
            },
            {
                "scenario": "Villa Community",
                "description": "30 row houses/villas - ONE project",
                "projects": 1,
                **self.calculate_monthly_cost(1),
            },
            {
                "scenario": "Large Developer (5 projects)",
                "description": "5 active projects across the city",
                "projects": 5,
                **self.calculate_monthly_cost(5),
            },
            {
                "scenario": "Major Builder (12 projects)",
                "description": "12 active + 3 archived projects",
                "projects": 12,
                **self.calculate_monthly_cost(12, 3),
            },
        ]
    
    # =========================================================================
    # ARCHIVE PRICING
    # =========================================================================
    
    def get_archive_options(self) -> Dict[str, Any]:
        """Get archive pricing options"""
        return {
            "monthly": {
                "price_usd": self.ARCHIVE_PRICE_USD,
                "description": f"${self.ARCHIVE_PRICE_USD}/month per archived project",
                "benefits": [
                    "Full access to all project history",
                    "Search all decisions and Q&A",
                    "Export data anytime",
                    "Legal documentation support",
                ],
            },
            "one_time": {
                "price_usd": self.ARCHIVE_ONETIME_USD,
                "description": f"${self.ARCHIVE_ONETIME_USD} one-time per project",
                "benefits": [
                    "Permanent access to project history",
                    "Downloadable archive",
                    "No recurring fees",
                    "5-year data retention",
                ],
            },
            "volume_discount": {
                "5_plus": "10% off for 5+ archived projects",
                "10_plus": "20% off for 10+ archived projects",
            },
        }
    
    # =========================================================================
    # QUOTES
    # =========================================================================
    
    def generate_quote(
        self,
        company_name: str,
        active_projects: List[Dict],
        archived_projects: List[Dict] = None,
        is_pilot: bool = False,
    ) -> Dict[str, Any]:
        """Generate a formal quote"""
        active_count = len(active_projects)
        archived_count = len(archived_projects) if archived_projects else 0
        
        pricing = self.calculate_monthly_cost(active_count, archived_count, is_pilot)
        
        quote = {
            "quote_id": f"Q-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company": company_name,
            "date": datetime.utcnow().isoformat(),
            "valid_until": "30 days",
            
            "projects": {
                "active": [
                    {"name": p.get("name", "Project"), "type": p.get("type", "mixed")}
                    for p in active_projects
                ],
                "archived": [
                    {"name": p.get("name", "Project")}
                    for p in (archived_projects or [])
                ],
            },
            
            "pricing": pricing,
            
            "terms": [
                "Monthly billing, cancel anytime",
                "14-day free trial available",
                "Onboarding and training included",
                "24/7 WhatsApp support",
            ],
        }
        
        return quote
    
    def format_quote_for_whatsapp(self, quote: Dict) -> str:
        """Format quote for WhatsApp sharing"""
        p = quote["pricing"]
        
        return f"""**SiteMind Quote**
{quote['company']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**Projects:**
• Active: {p['active_projects']}
• Archived: {p['archived_projects']}

**Monthly Cost:**
{p['breakdown']}

**Total: ${p['total_usd']:.0f}/month**
(₹{p['total_inr']:,.0f}/month)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quote ID: {quote['quote_id']}
Valid: {quote['valid_until']}

_Includes: Onboarding, training, 24/7 support_
"""
    
    # =========================================================================
    # PILOT PROGRAM
    # =========================================================================
    
    def get_pilot_info(self) -> Dict[str, Any]:
        """Get pilot program information"""
        return {
            "duration_months": self.PILOT_DURATION_MONTHS,
            "slots_total": self.PILOT_SLOTS,
            "price": "FREE",
            "what_you_get": [
                "Full access to all features",
                "Unlimited projects during pilot",
                "Personal onboarding call",
                "Priority support via WhatsApp",
                "Feedback sessions with founder",
            ],
            "commitment": [
                "Use SiteMind actively on at least 1 project",
                "Provide honest feedback",
                "Optional: testimonial if satisfied",
            ],
            "after_pilot": {
                "continue": f"${self.BASE_PRICE_USD}/project/month",
                "volume_discounts": "Available for 3+ projects",
                "cancel": "No obligation, export your data",
            },
        }


# Singleton instance
pricing_service = PricingService()
