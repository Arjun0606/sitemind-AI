"""
SiteMind Pricing Service
Company-level pricing with per-seat and per-project components

PRICING PHILOSOPHY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE OVERLAP PROBLEM:
- Same PM manages 3 projects → should pay 1x, not 3x
- Same architect consults on all projects → 1 seat
- But more projects = more value = should pay more

SOLUTION: Company-level subscription with two components:
1. PER SEAT (unique users) → $50/user/month
2. PER PROJECT (active projects) → $200/project/month

This handles overlap naturally:
- Rajesh on 3 projects = 1 seat = $50
- 3 projects = 3 × $200 = $600
- Total = $650, not $1,950 (if we charged per project×user)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARAMETERS WE CAN VERIFY:
✅ Unique users (phone numbers - we track exactly)
✅ Active projects (they can't hide, we see queries)
✅ Query volume (we count every message)

PARAMETERS WE CAN'T VERIFY:
❌ Project value (they'll lie)
❌ Built-up area (they'll lie)
❌ Number of floors (somewhat verifiable from drawings)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT STAGES:
- Active (construction): Full price
- Pre-construction (planning): 50% price
- Handover/Maintenance: 50% price
- Archived (completed): Flat $100/month or one-time
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ProjectStage(str, Enum):
    PLANNING = "planning"          # Pre-construction
    ACTIVE = "active"              # Under construction
    FINISHING = "finishing"        # Final stages
    HANDOVER = "handover"          # Handing over to buyers
    ARCHIVED = "archived"          # Completed


class PricingService:
    """
    Company-level pricing: Per Seat + Per Project
    """
    
    def __init__(self):
        # =================================================================
        # CORE PRICING
        # =================================================================
        
        # Per unique user (seat)
        self.PER_SEAT_USD = 50  # $50/user/month
        
        # Per active project
        self.PER_PROJECT_USD = 200  # $200/project/month
        
        # Minimum seats included in base
        self.INCLUDED_SEATS = 3  # First 3 users free
        
        # =================================================================
        # PROJECT STAGE MULTIPLIERS
        # =================================================================
        
        self.STAGE_MULTIPLIERS = {
            ProjectStage.PLANNING: 0.5,      # 50% - less activity
            ProjectStage.ACTIVE: 1.0,        # 100% - full construction
            ProjectStage.FINISHING: 1.0,     # 100% - still active
            ProjectStage.HANDOVER: 0.5,      # 50% - winding down
            ProjectStage.ARCHIVED: 0.0,      # Separate pricing
        }
        
        # Archive pricing
        self.ARCHIVE_MONTHLY_USD = 100       # Flat $100/month
        self.ARCHIVE_ONETIME_USD = 1000      # One-time, keep forever
        
        # =================================================================
        # VOLUME DISCOUNTS (by total monthly spend)
        # =================================================================
        
        self.VOLUME_DISCOUNTS = {
            1000: 0.00,   # < $1K: no discount
            2000: 0.05,   # $2K+: 5% off
            5000: 0.10,   # $5K+: 10% off
            10000: 0.15,  # $10K+: 15% off
            25000: 0.20,  # $25K+: 20% off
        }
        
        # Annual payment discount
        self.ANNUAL_DISCOUNT = 0.15  # 15% off (2 months free)
        
        # =================================================================
        # PILOT PROGRAM
        # =================================================================
        
        self.PILOT_MONTHS = 3
        self.PILOT_SLOTS = 3
        self.FOUNDING_DISCOUNT = 0.20  # 20% forever for pilots
        
        # USD to INR
        self.USD_TO_INR = 83
    
    # =========================================================================
    # MAIN PRICING CALCULATION
    # =========================================================================
    
    def calculate_company_price(
        self,
        unique_users: int,
        projects: List[Dict],
        is_pilot: bool = False,
        is_founding_customer: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate pricing for a company
        
        Args:
            unique_users: Total unique users across ALL projects (by phone)
            projects: List of {name, stage} - stage affects pricing
            is_pilot: Free pilot program
            is_founding_customer: Gets permanent discount
            
        Example:
            unique_users=15,
            projects=[
                {"name": "Township A", "stage": "active"},
                {"name": "High-rise B", "stage": "active"},
                {"name": "Villas C", "stage": "planning"},
            ]
        """
        if is_pilot:
            return self._pilot_pricing(unique_users, projects)
        
        # Calculate seat cost
        billable_seats = max(0, unique_users - self.INCLUDED_SEATS)
        seats_cost = billable_seats * self.PER_SEAT_USD
        
        # Calculate project cost (with stage multipliers)
        projects_breakdown = []
        projects_cost = 0
        
        for proj in projects:
            stage = ProjectStage(proj.get("stage", "active"))
            
            if stage == ProjectStage.ARCHIVED:
                # Archived projects have separate pricing
                proj_cost = self.ARCHIVE_MONTHLY_USD
            else:
                multiplier = self.STAGE_MULTIPLIERS[stage]
                proj_cost = self.PER_PROJECT_USD * multiplier
            
            projects_breakdown.append({
                "name": proj.get("name", "Project"),
                "stage": stage.value,
                "multiplier": self.STAGE_MULTIPLIERS.get(stage, 1.0),
                "cost_usd": proj_cost,
            })
            
            projects_cost += proj_cost
        
        # Subtotal
        subtotal = seats_cost + projects_cost
        
        # Volume discount
        discount_percent = 0
        for threshold, discount in sorted(self.VOLUME_DISCOUNTS.items()):
            if subtotal >= threshold:
                discount_percent = discount * 100
        
        discount_amount = subtotal * (discount_percent / 100)
        
        # Founding customer discount
        founding_discount = 0
        if is_founding_customer:
            founding_discount = (subtotal - discount_amount) * self.FOUNDING_DISCOUNT
        
        # Final monthly
        monthly_usd = subtotal - discount_amount - founding_discount
        monthly_inr = monthly_usd * self.USD_TO_INR
        
        return {
            "company_summary": {
                "unique_users": unique_users,
                "billable_seats": billable_seats,
                "active_projects": len([p for p in projects if p.get("stage") != "archived"]),
                "archived_projects": len([p for p in projects if p.get("stage") == "archived"]),
            },
            
            "seats": {
                "total_users": unique_users,
                "included_free": self.INCLUDED_SEATS,
                "billable": billable_seats,
                "rate_usd": self.PER_SEAT_USD,
                "cost_usd": seats_cost,
            },
            
            "projects": {
                "breakdown": projects_breakdown,
                "cost_usd": projects_cost,
            },
            
            "subtotal_usd": subtotal,
            
            "discounts": {
                "volume": {
                    "percent": discount_percent,
                    "amount_usd": discount_amount,
                },
                "founding_customer": {
                    "percent": self.FOUNDING_DISCOUNT * 100 if is_founding_customer else 0,
                    "amount_usd": founding_discount,
                },
            },
            
            "monthly_usd": monthly_usd,
            "monthly_inr": monthly_inr,
            "annual_usd": monthly_usd * 12 * (1 - self.ANNUAL_DISCOUNT),
            "annual_inr": monthly_usd * 12 * (1 - self.ANNUAL_DISCOUNT) * self.USD_TO_INR,
            "annual_savings": f"{self.ANNUAL_DISCOUNT * 100:.0f}% off (pay for 10 months)",
        }
    
    def _pilot_pricing(self, users: int, projects: List[Dict]) -> Dict[str, Any]:
        """Pilot program pricing (free)"""
        return {
            "company_summary": {
                "unique_users": users,
                "active_projects": len(projects),
            },
            "monthly_usd": 0,
            "monthly_inr": 0,
            "status": "pilot",
            "note": f"FREE for {self.PILOT_MONTHS} months",
            "after_pilot": f"{self.FOUNDING_DISCOUNT * 100:.0f}% founding customer discount forever",
        }
    
    # =========================================================================
    # PRICING EXAMPLES
    # =========================================================================
    
    def get_pricing_examples(self) -> List[Dict]:
        """Real-world examples with overlap handled"""
        
        examples = [
            {
                "scenario": "Small Developer",
                "description": "1 active project, 8 team members",
                **self.calculate_company_price(
                    unique_users=8,
                    projects=[{"name": "Sunrise Apartments", "stage": "active"}]
                ),
            },
            {
                "scenario": "Medium Developer",
                "description": "3 projects (2 active, 1 planning), 20 users with overlap",
                **self.calculate_company_price(
                    unique_users=20,
                    projects=[
                        {"name": "Green Valley", "stage": "active"},
                        {"name": "City Heights", "stage": "active"},
                        {"name": "Lake View", "stage": "planning"},
                    ]
                ),
            },
            {
                "scenario": "Large Developer",
                "description": "6 projects (4 active, 1 finishing, 1 archived), 45 users",
                **self.calculate_company_price(
                    unique_users=45,
                    projects=[
                        {"name": "Township Phase 1", "stage": "finishing"},
                        {"name": "Township Phase 2", "stage": "active"},
                        {"name": "Commercial Hub", "stage": "active"},
                        {"name": "Luxury Villas", "stage": "active"},
                        {"name": "Tech Park", "stage": "active"},
                        {"name": "Old Project", "stage": "archived"},
                    ]
                ),
            },
        ]
        
        return examples
    
    def get_pricing_table(self) -> str:
        """Formatted pricing table"""
        return f"""
**SiteMind Pricing**
Company-level subscription

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**PER SEAT (unique users)**
• First {self.INCLUDED_SEATS} users: FREE
• Additional users: ${self.PER_SEAT_USD}/user/month

**PER PROJECT**
• Active/Finishing: ${self.PER_PROJECT_USD}/project/month
• Planning/Handover: ${int(self.PER_PROJECT_USD * 0.5)}/project/month
• Archived: ${self.ARCHIVE_MONTHLY_USD}/project/month (or ${self.ARCHIVE_ONETIME_USD} one-time)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**WHY THIS IS FAIR:**

Same person on 3 projects = 1 seat, not 3
→ PM managing 5 projects pays $50, not $250

More projects = more value = more project fees
→ But overlap is handled fairly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**VOLUME DISCOUNTS:**
• $2,000+/mo: 5% off
• $5,000+/mo: 10% off
• $10,000+/mo: 15% off
• $25,000+/mo: 20% off

**ANNUAL PAYMENT:** {int(self.ANNUAL_DISCOUNT * 100)}% off (2 months free)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**EXAMPLES:**

Small (1 project, 8 users):
  5 extra seats × $50 = $250
  1 project × $200 = $200
  Total: $450/month

Medium (3 projects, 20 users with overlap):
  17 extra seats × $50 = $850
  2 active × $200 + 1 planning × $100 = $500
  Total: $1,350/month

Large (6 projects, 45 users):
  42 extra seats × $50 = $2,100
  4 active × $200 + 1 finishing × $200 + 1 archived × $100 = $1,100
  Subtotal: $3,200
  Volume discount (5%): -$160
  Total: $3,040/month
"""
    
    # =========================================================================
    # SEAT COUNTING
    # =========================================================================
    
    def count_unique_seats(self, project_users: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Count unique users across projects
        
        Args:
            project_users: {project_id: [phone1, phone2, ...]}
            
        Returns:
            Unique count and breakdown
        """
        all_phones: Set[str] = set()
        project_counts = {}
        
        for project_id, phones in project_users.items():
            project_counts[project_id] = len(phones)
            all_phones.update(phones)
        
        # Find overlap
        total_if_no_overlap = sum(project_counts.values())
        overlap = total_if_no_overlap - len(all_phones)
        
        return {
            "unique_users": len(all_phones),
            "total_if_counted_separately": total_if_no_overlap,
            "overlap_saved": overlap,
            "projects": project_counts,
            "explanation": f"{overlap} users work across multiple projects (counted once)",
        }
    
    # =========================================================================
    # QUOTES
    # =========================================================================
    
    def generate_quote(
        self,
        company_name: str,
        unique_users: int,
        projects: List[Dict],
        is_pilot: bool = False,
        is_founding: bool = False,
    ) -> Dict[str, Any]:
        """Generate formal quote"""
        pricing = self.calculate_company_price(unique_users, projects, is_pilot, is_founding)
        
        return {
            "quote_id": f"SM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company": company_name,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "valid_days": 30,
            "pricing": pricing,
            "includes": [
                "Unlimited WhatsApp queries",
                "Blueprint & photo analysis",
                "Complete audit trail",
                "All team roles & permissions",
                "ROI & usage reporting",
                "24/7 WhatsApp support",
                "Personal onboarding & training",
            ],
        }
    
    def format_quote_whatsapp(self, quote: Dict) -> str:
        """Format quote for WhatsApp"""
        p = quote["pricing"]
        s = p.get("seats", {})
        proj = p.get("projects", {})
        
        msg = f"""**SiteMind Quote**
{quote['company']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Team:** {s.get('total_users', 0)} users
• {s.get('included_free', 3)} included free
• {s.get('billable', 0)} × ${self.PER_SEAT_USD} = ${s.get('cost_usd', 0)}

**Projects:**
"""
        for pr in proj.get("breakdown", []):
            msg += f"• {pr['name']} ({pr['stage']}): ${pr['cost_usd']:.0f}\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Monthly:** ${p.get('monthly_usd', 0):,.0f}
(₹{p.get('monthly_inr', 0):,.0f})

**Annual:** ${p.get('annual_usd', 0):,.0f}
({p.get('annual_savings', '')})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Quote: {quote['quote_id']}
Valid: {quote['valid_days']} days
"""
        return msg
    
    # =========================================================================
    # ARCHIVE
    # =========================================================================
    
    def get_archive_options(self) -> Dict[str, Any]:
        """Archive pricing for completed projects"""
        return {
            "monthly": {
                "usd": self.ARCHIVE_MONTHLY_USD,
                "inr": self.ARCHIVE_MONTHLY_USD * self.USD_TO_INR,
                "description": "Keep full access to project history",
            },
            "one_time": {
                "usd": self.ARCHIVE_ONETIME_USD,
                "inr": self.ARCHIVE_ONETIME_USD * self.USD_TO_INR,
                "description": "Pay once, keep forever",
            },
            "benefits": [
                "Search all decisions & Q&A",
                "Legal documentation",
                "Export anytime",
                "Reference for future projects",
            ],
        }
    
    # =========================================================================
    # PILOT
    # =========================================================================
    
    def get_pilot_info(self) -> Dict[str, Any]:
        """Pilot program details"""
        return {
            "name": "Founder's Pilot Program",
            "duration": f"{self.PILOT_MONTHS} months FREE",
            "slots_remaining": self.PILOT_SLOTS,
            "includes": [
                "Full access to all features",
                "Unlimited users and projects",
                "Personal onboarding with founder",
                "Direct WhatsApp to founder",
                "Shape the roadmap",
            ],
            "requirements": [
                "Use on at least 1 active project",
                "Honest feedback",
                "30-min call every 2 weeks",
            ],
            "after_pilot": f"{int(self.FOUNDING_DISCOUNT * 100)}% founding customer discount forever",
        }


# Singleton instance
pricing_service = PricingService()
