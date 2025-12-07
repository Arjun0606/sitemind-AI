"""
SiteMind Pricing Service
Enterprise pricing with usage-based components

PRICING PHILOSOPHY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A ₹300 Cr project paying $500/month is ABSURD.
That's 0.002% of project value. We're leaving money on the table.

If we prevent 0.1% rework = ₹30 Lakhs saved = $36,000
We should capture at least 5-10% of value delivered = $1,800-3,600/month

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEW PRICING MODEL:

1. BASE: Per seat + Per project (higher than before)
2. USAGE: Queries, storage, documents (pay for what you use)
3. TRANSPARENT: Show them their actual usage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUR COSTS (per project/month):
- Gemini: ~$60-150 (depending on queries)
- Supermemory: ~$5-20 (share of plan)
- Storage: ~$1-5
- Twilio: ~$10-30
- Total: ~$100-200/project

We should be making 5-10x margin = $500-2000 minimum per project

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import math


class ProjectStage(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    FINISHING = "finishing"
    HANDOVER = "handover"
    ARCHIVED = "archived"


class PricingService:
    """
    Enterprise pricing with usage-based components
    """
    
    def __init__(self):
        # =================================================================
        # BASE PRICING (HIGHER!)
        # =================================================================
        
        # Per seat (unique user by phone)
        self.PER_SEAT_USD = 75  # Was $50, now $75
        self.INCLUDED_SEATS = 5  # First 5 included
        
        # Per project base
        self.PROJECT_BASE = {
            ProjectStage.PLANNING: 300,     # $300/mo
            ProjectStage.ACTIVE: 750,       # $750/mo - main revenue
            ProjectStage.FINISHING: 750,    # $750/mo
            ProjectStage.HANDOVER: 400,     # $400/mo
            ProjectStage.ARCHIVED: 150,     # $150/mo flat
        }
        
        # =================================================================
        # USAGE-BASED PRICING
        # =================================================================
        
        # Queries
        self.INCLUDED_QUERIES = 500  # Per project
        self.PER_QUERY_USD = 0.10    # $0.10 per query over limit
        
        # Document processing
        self.INCLUDED_DOCUMENTS = 20  # Per project
        self.PER_DOCUMENT_USD = 2.00  # $2 per document (drawings, PDFs)
        
        # Storage
        self.INCLUDED_STORAGE_GB = 5  # Per project
        self.PER_GB_USD = 1.00        # $1 per GB over limit
        
        # Photo analysis
        self.INCLUDED_PHOTOS = 100    # Per project
        self.PER_PHOTO_USD = 0.25     # $0.25 per photo analyzed
        
        # =================================================================
        # VOLUME DISCOUNTS
        # =================================================================
        
        self.VOLUME_DISCOUNTS = {
            3000: 0.05,    # $3K+/mo: 5% off
            7500: 0.10,    # $7.5K+/mo: 10% off
            15000: 0.15,   # $15K+/mo: 15% off
            30000: 0.20,   # $30K+/mo: 20% off
        }
        
        # Annual discount
        self.ANNUAL_DISCOUNT = 0.17  # 17% off (2 months free)
        
        # =================================================================
        # PILOT & FOUNDING
        # =================================================================
        
        self.PILOT_MONTHS = 3
        self.FOUNDING_DISCOUNT = 0.25  # 25% forever for pilots
        
        # =================================================================
        # OUR COSTS (for margin calculation)
        # =================================================================
        
        self.COST_PER_QUERY = 0.03      # Gemini
        self.COST_PER_DOCUMENT = 0.50   # Gemini vision + processing
        self.COST_PER_GB = 0.02         # Storage
        self.COST_PER_MESSAGE = 0.005   # Twilio
        
        # USD to INR
        self.USD_TO_INR = 83
    
    # =========================================================================
    # PRICING CALCULATOR
    # =========================================================================
    
    def calculate_project_price(
        self,
        stage: str = "active",
        num_users: int = 10,
        monthly_queries: int = 500,
        documents: int = 20,
        storage_gb: float = 5,
        photos: int = 100,
    ) -> Dict[str, Any]:
        """
        Calculate price for a single project with usage
        """
        stage_enum = ProjectStage(stage)
        
        # Base project cost
        base = self.PROJECT_BASE[stage_enum]
        
        # Seat cost (for this project's allocation)
        # In company context, seats are shared - handled separately
        
        # Usage costs
        query_overage = max(0, monthly_queries - self.INCLUDED_QUERIES)
        query_cost = query_overage * self.PER_QUERY_USD
        
        doc_overage = max(0, documents - self.INCLUDED_DOCUMENTS)
        doc_cost = doc_overage * self.PER_DOCUMENT_USD
        
        storage_overage = max(0, storage_gb - self.INCLUDED_STORAGE_GB)
        storage_cost = storage_overage * self.PER_GB_USD
        
        photo_overage = max(0, photos - self.INCLUDED_PHOTOS)
        photo_cost = photo_overage * self.PER_PHOTO_USD
        
        usage_total = query_cost + doc_cost + storage_cost + photo_cost
        total = base + usage_total
        
        # Our cost calculation
        our_cost = (
            monthly_queries * self.COST_PER_QUERY +
            documents * self.COST_PER_DOCUMENT +
            storage_gb * self.COST_PER_GB +
            monthly_queries * self.COST_PER_MESSAGE
        )
        
        margin = ((total - our_cost) / total) * 100 if total > 0 else 0
        
        return {
            "stage": stage,
            "base_usd": base,
            
            "usage": {
                "queries": {
                    "count": monthly_queries,
                    "included": self.INCLUDED_QUERIES,
                    "overage": query_overage,
                    "cost_usd": query_cost,
                },
                "documents": {
                    "count": documents,
                    "included": self.INCLUDED_DOCUMENTS,
                    "overage": doc_overage,
                    "cost_usd": doc_cost,
                },
                "storage_gb": {
                    "used": storage_gb,
                    "included": self.INCLUDED_STORAGE_GB,
                    "overage": storage_overage,
                    "cost_usd": storage_cost,
                },
                "photos": {
                    "count": photos,
                    "included": self.INCLUDED_PHOTOS,
                    "overage": photo_overage,
                    "cost_usd": photo_cost,
                },
                "total_usd": usage_total,
            },
            
            "monthly_usd": total,
            "monthly_inr": total * self.USD_TO_INR,
            
            "cost_analysis": {
                "our_cost_usd": round(our_cost, 2),
                "margin_percent": round(margin, 1),
            },
        }
    
    def calculate_company_price(
        self,
        unique_users: int,
        projects: List[Dict],
        is_pilot: bool = False,
        is_founding: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate total company price
        
        Args:
            unique_users: Total unique users across all projects
            projects: List of {name, stage, queries, documents, storage_gb, photos}
        """
        if is_pilot:
            return self._pilot_pricing(unique_users, projects)
        
        # Seat cost (company-level)
        billable_seats = max(0, unique_users - self.INCLUDED_SEATS)
        seats_cost = billable_seats * self.PER_SEAT_USD
        
        # Project costs
        projects_detail = []
        projects_total = 0
        
        for proj in projects:
            proj_price = self.calculate_project_price(
                stage=proj.get("stage", "active"),
                num_users=proj.get("users", 10),
                monthly_queries=proj.get("queries", 500),
                documents=proj.get("documents", 20),
                storage_gb=proj.get("storage_gb", 5),
                photos=proj.get("photos", 100),
            )
            
            projects_detail.append({
                "name": proj.get("name", "Project"),
                **proj_price,
            })
            
            projects_total += proj_price["monthly_usd"]
        
        # Subtotal
        subtotal = seats_cost + projects_total
        
        # Volume discount
        discount_percent = 0
        for threshold, discount in sorted(self.VOLUME_DISCOUNTS.items()):
            if subtotal >= threshold:
                discount_percent = discount * 100
        
        volume_discount = subtotal * (discount_percent / 100)
        
        # Founding discount
        founding_discount = 0
        if is_founding:
            founding_discount = (subtotal - volume_discount) * self.FOUNDING_DISCOUNT
        
        # Final
        monthly = subtotal - volume_discount - founding_discount
        
        return {
            "summary": {
                "unique_users": unique_users,
                "billable_seats": billable_seats,
                "projects": len(projects),
            },
            
            "seats": {
                "total": unique_users,
                "included": self.INCLUDED_SEATS,
                "billable": billable_seats,
                "rate_usd": self.PER_SEAT_USD,
                "cost_usd": seats_cost,
            },
            
            "projects": projects_detail,
            "projects_total_usd": projects_total,
            
            "subtotal_usd": subtotal,
            
            "discounts": {
                "volume": {
                    "percent": discount_percent,
                    "amount_usd": volume_discount,
                },
                "founding": {
                    "percent": self.FOUNDING_DISCOUNT * 100 if is_founding else 0,
                    "amount_usd": founding_discount,
                },
            },
            
            "monthly_usd": monthly,
            "monthly_inr": monthly * self.USD_TO_INR,
            "annual_usd": monthly * 12 * (1 - self.ANNUAL_DISCOUNT),
            "annual_savings_percent": self.ANNUAL_DISCOUNT * 100,
        }
    
    def _pilot_pricing(self, users: int, projects: List[Dict]) -> Dict[str, Any]:
        """Pilot pricing"""
        return {
            "summary": {"unique_users": users, "projects": len(projects)},
            "monthly_usd": 0,
            "monthly_inr": 0,
            "status": "pilot",
            "note": f"FREE for {self.PILOT_MONTHS} months",
            "after_pilot": f"{int(self.FOUNDING_DISCOUNT * 100)}% founding discount forever",
        }
    
    # =========================================================================
    # PRICING ESTIMATOR (for sales calls)
    # =========================================================================
    
    def estimate_price(
        self,
        company_size: str,  # small, medium, large, enterprise
    ) -> Dict[str, Any]:
        """
        Quick estimate based on company size
        """
        profiles = {
            "small": {
                "description": "1-2 projects, 10-15 users",
                "users": 12,
                "projects": [
                    {"name": "Project A", "stage": "active", "queries": 400, "documents": 15, "storage_gb": 3, "photos": 50},
                ],
            },
            "medium": {
                "description": "3-5 projects, 25-40 users",
                "users": 30,
                "projects": [
                    {"name": "Project A", "stage": "active", "queries": 600, "documents": 30, "storage_gb": 8, "photos": 150},
                    {"name": "Project B", "stage": "active", "queries": 500, "documents": 25, "storage_gb": 6, "photos": 100},
                    {"name": "Project C", "stage": "planning", "queries": 200, "documents": 10, "storage_gb": 2, "photos": 30},
                ],
            },
            "large": {
                "description": "6-10 projects, 50-80 users",
                "users": 65,
                "projects": [
                    {"name": "Township", "stage": "active", "queries": 1500, "documents": 80, "storage_gb": 25, "photos": 400},
                    {"name": "Commercial", "stage": "active", "queries": 800, "documents": 40, "storage_gb": 12, "photos": 200},
                    {"name": "Residential A", "stage": "active", "queries": 600, "documents": 30, "storage_gb": 8, "photos": 150},
                    {"name": "Residential B", "stage": "finishing", "queries": 400, "documents": 20, "storage_gb": 6, "photos": 100},
                    {"name": "Villas", "stage": "active", "queries": 500, "documents": 25, "storage_gb": 7, "photos": 120},
                    {"name": "Old Project", "stage": "archived", "queries": 50, "documents": 5, "storage_gb": 10, "photos": 10},
                ],
            },
            "enterprise": {
                "description": "10+ projects, 100+ users",
                "users": 120,
                "projects": [
                    {"name": "Mega Township", "stage": "active", "queries": 3000, "documents": 150, "storage_gb": 50, "photos": 800},
                    {"name": "IT Park", "stage": "active", "queries": 1200, "documents": 60, "storage_gb": 20, "photos": 300},
                    {"name": "Mall", "stage": "active", "queries": 1000, "documents": 50, "storage_gb": 15, "photos": 250},
                    {"name": "Residential Complex", "stage": "active", "queries": 800, "documents": 40, "storage_gb": 12, "photos": 200},
                    {"name": "Luxury Villas", "stage": "active", "queries": 600, "documents": 30, "storage_gb": 10, "photos": 150},
                    {"name": "Commercial Hub", "stage": "finishing", "queries": 500, "documents": 25, "storage_gb": 8, "photos": 120},
                    {"name": "Affordable Housing", "stage": "active", "queries": 700, "documents": 35, "storage_gb": 10, "photos": 180},
                    {"name": "Project X", "stage": "planning", "queries": 300, "documents": 15, "storage_gb": 3, "photos": 50},
                ],
            },
        }
        
        profile = profiles.get(company_size, profiles["medium"])
        pricing = self.calculate_company_price(profile["users"], profile["projects"])
        
        return {
            "company_size": company_size,
            "profile": profile["description"],
            **pricing,
        }
    
    # =========================================================================
    # PRICING TABLE
    # =========================================================================
    
    def get_pricing_table(self) -> str:
        """Formatted pricing for website/sales"""
        return f"""
**SiteMind Enterprise Pricing**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASE PRICING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Per Seat** (unique users by phone)
• First {self.INCLUDED_SEATS} users: Included
• Additional: ${self.PER_SEAT_USD}/user/month

**Per Project** (by stage)
• Active construction: ${self.PROJECT_BASE[ProjectStage.ACTIVE]}/month
• Planning phase: ${self.PROJECT_BASE[ProjectStage.PLANNING]}/month
• Finishing/Handover: ${self.PROJECT_BASE[ProjectStage.HANDOVER]}/month
• Archived: ${self.PROJECT_BASE[ProjectStage.ARCHIVED]}/month

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INCLUDED PER PROJECT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• {self.INCLUDED_QUERIES} queries/month
• {self.INCLUDED_DOCUMENTS} documents analyzed
• {self.INCLUDED_STORAGE_GB} GB storage
• {self.INCLUDED_PHOTOS} photos analyzed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE OVERAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Additional queries: ${self.PER_QUERY_USD}/query
• Additional documents: ${self.PER_DOCUMENT_USD}/document
• Additional storage: ${self.PER_GB_USD}/GB
• Additional photos: ${self.PER_PHOTO_USD}/photo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VOLUME DISCOUNTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• $3,000+/month: 5% off
• $7,500+/month: 10% off
• $15,000+/month: 15% off
• $30,000+/month: 20% off

Annual payment: {int(self.ANNUAL_DISCOUNT * 100)}% off

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLE PRICING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Small (12 users, 1 project):      ~$1,200/month
Medium (30 users, 3 projects):    ~$3,800/month
Large (65 users, 6 projects):     ~$8,500/month
Enterprise (120 users, 8 projects): ~$18,000/month
"""
    
    # =========================================================================
    # EXAMPLES
    # =========================================================================
    
    def get_pricing_examples(self) -> List[Dict]:
        """Detailed pricing examples"""
        return [
            self.estimate_price("small"),
            self.estimate_price("medium"),
            self.estimate_price("large"),
            self.estimate_price("enterprise"),
        ]
    
    # =========================================================================
    # QUOTE GENERATION
    # =========================================================================
    
    def generate_quote(
        self,
        company_name: str,
        unique_users: int,
        projects: List[Dict],
        is_founding: bool = False,
    ) -> Dict[str, Any]:
        """Generate formal quote"""
        pricing = self.calculate_company_price(unique_users, projects, False, is_founding)
        
        return {
            "quote_id": f"SM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company": company_name,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "valid_days": 30,
            "pricing": pricing,
            "includes": [
                "Unlimited WhatsApp access",
                "AI blueprint analysis",
                "Photo & document processing",
                "Complete audit trail",
                "Team management",
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
Quote: {quote['quote_id']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Team:** {p['seats']['total']} users
• {p['seats']['included']} included
• {p['seats']['billable']} × ${self.PER_SEAT_USD} = ${p['seats']['cost_usd']}

**Projects:** {len(p['projects'])}
"""
        
        for proj in p["projects"]:
            msg += f"• {proj['name']} ({proj['stage']}): ${proj['monthly_usd']:,.0f}\n"
        
        disc = p["discounts"]
        if disc["volume"]["percent"] > 0:
            msg += f"\n**Volume discount:** {disc['volume']['percent']:.0f}% off\n"
        if disc["founding"]["percent"] > 0:
            msg += f"**Founding discount:** {disc['founding']['percent']:.0f}% off\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Monthly: ${p['monthly_usd']:,.0f}**
(₹{p['monthly_inr']:,.0f})

**Annual: ${p['annual_usd']:,.0f}**
(Save {p['annual_savings_percent']:.0f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Valid: {quote['valid_days']} days
"""
        return msg
    
    # =========================================================================
    # PILOT PROGRAM
    # =========================================================================
    
    def get_pilot_info(self) -> Dict[str, Any]:
        """Pilot program info"""
        return {
            "name": "Founder's Pilot",
            "duration": f"{self.PILOT_MONTHS} months FREE",
            "slots": 3,
            "includes": [
                "Full access to all features",
                "Unlimited usage during pilot",
                "Personal onboarding",
                "Direct founder access",
                "Shape the roadmap",
            ],
            "after_pilot": f"{int(self.FOUNDING_DISCOUNT * 100)}% discount forever",
        }


# Singleton instance
pricing_service = PricingService()
