"""
SiteMind Pricing Service
Cursor-style: ONE flat fee for everyone + Usage

EXACTLY LIKE CURSOR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Cursor Pro: $20/month flat
→ Includes 500 fast requests
→ After that: $0.04/request

SiteMind Pro: $499/month flat (per company)
→ Includes: 500 queries, 20 docs, 100 photos, 10GB
→ After that: Pay per use

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BILLING:
- Flat fee: Start of cycle
- Usage: Tracked during cycle, charged NEXT cycle
- Full breakdown shown

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class PlanType(str, Enum):
    STARTER = "starter"       # Small teams
    PROFESSIONAL = "professional"  # Most customers
    ENTERPRISE = "enterprise"  # Large orgs


@dataclass
class UsageTracker:
    """Track usage for billing"""
    company_id: str
    cycle_start: str
    cycle_end: str
    queries: int = 0
    documents: int = 0
    photos: int = 0
    storage_gb: float = 0


class PricingService:
    """
    Cursor-style: Flat fee + Usage
    """
    
    def __init__(self):
        # =================================================================
        # PLANS (flat fee per company)
        # =================================================================
        
        self.PLANS = {
            PlanType.STARTER: {
                "name": "Starter",
                "price_usd": 299,
                "description": "For small teams getting started",
                "includes": {
                    "users": 10,
                    "projects": 2,
                    "queries": 300,
                    "documents": 10,
                    "photos": 50,
                    "storage_gb": 5,
                },
            },
            PlanType.PROFESSIONAL: {
                "name": "Professional",
                "price_usd": 499,
                "description": "For growing construction companies",
                "includes": {
                    "users": 25,
                    "projects": 5,
                    "queries": 500,
                    "documents": 20,
                    "photos": 100,
                    "storage_gb": 10,
                },
            },
            PlanType.ENTERPRISE: {
                "name": "Enterprise",
                "price_usd": 999,
                "description": "For large developers",
                "includes": {
                    "users": 100,
                    "projects": 20,
                    "queries": 2000,
                    "documents": 100,
                    "photos": 500,
                    "storage_gb": 50,
                },
            },
        }
        
        # =================================================================
        # USAGE PRICING (80%+ margins)
        # =================================================================
        
        # Our costs
        self.COSTS = {
            "user": 0,           # No marginal cost
            "project": 0,        # No marginal cost
            "query": 0.03,       # Gemini API
            "document": 0.50,    # Gemini Vision
            "photo": 0.10,       # Gemini Vision
            "storage_gb": 0.02,  # Supabase
        }
        
        # Our prices (80%+ margin on all)
        self.USAGE_PRICES = {
            "user": 10,          # $10/additional user
            "project": 100,      # $100/additional project
            "query": 0.15,       # $0.15/query (80% margin)
            "document": 2.50,    # $2.50/doc (80% margin)
            "photo": 0.50,       # $0.50/photo (80% margin)
            "storage_gb": 1.00,  # $1.00/GB (98% margin)
        }
        
        # =================================================================
        # OTHER
        # =================================================================
        
        self.ANNUAL_DISCOUNT = 0.17  # 2 months free
        self.USD_TO_INR = 83
        
        # Usage tracking
        self._usage: Dict[str, UsageTracker] = {}
    
    # =========================================================================
    # GET PLAN INFO
    # =========================================================================
    
    def get_plans(self) -> List[Dict]:
        """Get all plans for pricing page"""
        return [
            {
                "plan": plan.value,
                **info,
                "popular": plan == PlanType.PROFESSIONAL,
            }
            for plan, info in self.PLANS.items()
        ]
    
    def get_plan(self, plan: PlanType) -> Dict:
        """Get specific plan details"""
        return {
            "plan": plan.value,
            **self.PLANS[plan],
        }
    
    # =========================================================================
    # USAGE TRACKING
    # =========================================================================
    
    def track_usage(
        self,
        company_id: str,
        queries: int = 0,
        documents: int = 0,
        photos: int = 0,
        storage_gb: float = 0,
    ):
        """Track usage during billing cycle"""
        if company_id not in self._usage:
            now = datetime.utcnow()
            self._usage[company_id] = UsageTracker(
                company_id=company_id,
                cycle_start=now.isoformat(),
                cycle_end=(now + timedelta(days=30)).isoformat(),
            )
        
        tracker = self._usage[company_id]
        tracker.queries += queries
        tracker.documents += documents
        tracker.photos += photos
        tracker.storage_gb = max(tracker.storage_gb, storage_gb)
    
    def get_usage(self, company_id: str) -> Dict[str, Any]:
        """Get current usage"""
        tracker = self._usage.get(company_id)
        if not tracker:
            return {"queries": 0, "documents": 0, "photos": 0, "storage_gb": 0}
        
        return {
            "queries": tracker.queries,
            "documents": tracker.documents,
            "photos": tracker.photos,
            "storage_gb": tracker.storage_gb,
            "cycle_start": tracker.cycle_start,
            "cycle_end": tracker.cycle_end,
        }
    
    # =========================================================================
    # CALCULATE USAGE CHARGES
    # =========================================================================
    
    def calculate_usage_charges(
        self,
        plan: PlanType,
        actual_users: int,
        actual_projects: int,
        queries: int,
        documents: int,
        photos: int,
        storage_gb: float,
    ) -> Dict[str, Any]:
        """
        Calculate usage charges for the cycle
        (billed in NEXT cycle, like Cursor)
        """
        included = self.PLANS[plan]["includes"]
        
        # Calculate overages
        overages = {
            "users": {
                "used": actual_users,
                "included": included["users"],
                "overage": max(0, actual_users - included["users"]),
                "rate": self.USAGE_PRICES["user"],
            },
            "projects": {
                "used": actual_projects,
                "included": included["projects"],
                "overage": max(0, actual_projects - included["projects"]),
                "rate": self.USAGE_PRICES["project"],
            },
            "queries": {
                "used": queries,
                "included": included["queries"],
                "overage": max(0, queries - included["queries"]),
                "rate": self.USAGE_PRICES["query"],
            },
            "documents": {
                "used": documents,
                "included": included["documents"],
                "overage": max(0, documents - included["documents"]),
                "rate": self.USAGE_PRICES["document"],
            },
            "photos": {
                "used": photos,
                "included": included["photos"],
                "overage": max(0, photos - included["photos"]),
                "rate": self.USAGE_PRICES["photo"],
            },
            "storage_gb": {
                "used": storage_gb,
                "included": included["storage_gb"],
                "overage": max(0, storage_gb - included["storage_gb"]),
                "rate": self.USAGE_PRICES["storage_gb"],
            },
        }
        
        # Calculate charges
        charges = {}
        total = 0
        our_cost = 0
        
        for item, data in overages.items():
            charge = data["overage"] * data["rate"]
            charges[item] = {
                **data,
                "charge_usd": charge,
            }
            total += charge
            
            # Our cost for margin calc
            if item in self.COSTS:
                our_cost += data["used"] * self.COSTS[item]
        
        margin = ((total - our_cost) / total * 100) if total > 0 else 100
        
        return {
            "breakdown": charges,
            "total_usage_usd": round(total, 2),
            "total_usage_inr": round(total * self.USD_TO_INR, 2),
            "our_cost": round(our_cost, 2),
            "margin_percent": round(margin, 1),
        }
    
    # =========================================================================
    # GENERATE INVOICE
    # =========================================================================
    
    def generate_invoice(
        self,
        company_name: str,
        plan: PlanType,
        actual_users: int,
        actual_projects: int,
        current_usage: Dict,
        previous_usage: Dict = None,
    ) -> Dict[str, Any]:
        """
        Generate invoice like Cursor does:
        - Flat fee for THIS cycle
        - Usage from PREVIOUS cycle
        """
        plan_info = self.PLANS[plan]
        
        # Flat fee for this cycle
        flat_fee = plan_info["price_usd"]
        
        # Usage charges from previous cycle
        usage_charges = None
        usage_total = 0
        
        if previous_usage:
            usage_charges = self.calculate_usage_charges(
                plan=plan,
                actual_users=actual_users,
                actual_projects=actual_projects,
                queries=previous_usage.get("queries", 0),
                documents=previous_usage.get("documents", 0),
                photos=previous_usage.get("photos", 0),
                storage_gb=previous_usage.get("storage_gb", 0),
            )
            usage_total = usage_charges["total_usage_usd"]
        
        total = flat_fee + usage_total
        
        return {
            "invoice_id": f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company": company_name,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "due_date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
            
            "plan": {
                "name": plan_info["name"],
                "price_usd": flat_fee,
            },
            
            "usage_charges": usage_charges,
            
            "summary": {
                "flat_fee_usd": flat_fee,
                "usage_usd": usage_total,
                "total_usd": total,
                "total_inr": total * self.USD_TO_INR,
            },
            
            "current_usage": current_usage,
            "note": "Usage charges are from last billing cycle. Current usage will be billed next cycle.",
        }
    
    def format_invoice(self, invoice: Dict) -> str:
        """Format invoice for display/WhatsApp"""
        plan = invoice["plan"]
        summary = invoice["summary"]
        usage = invoice.get("usage_charges")
        
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    SITEMIND INVOICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Invoice: {invoice['invoice_id']}
Company: {invoice['company']}
Date: {invoice['date']}
Due: {invoice['due_date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUBSCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{plan['name']} Plan                          ${plan['price_usd']:.2f}

"""

        if usage and usage["total_usage_usd"] > 0:
            msg += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE (from previous cycle)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            for item, data in usage["breakdown"].items():
                if data["overage"] > 0:
                    msg += f"{item.title():12} {data['overage']:>6} × ${data['rate']:.2f}    ${data['charge_usd']:>8.2f}\n"
            
            msg += f"""
                                    ─────────
Usage Subtotal                              ${usage['total_usage_usd']:>8.2f}

"""

        msg += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Subscription                               ${summary['flat_fee_usd']:>8.2f}
Usage                                      ${summary['usage_usd']:>8.2f}
                                           ══════════
TOTAL DUE                                  ${summary['total_usd']:>8.2f}
                                           (₹{summary['total_inr']:,.0f})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # Current usage preview
        current = invoice.get("current_usage", {})
        if any(current.values()):
            msg += """
CURRENT CYCLE USAGE (will be billed next cycle)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            for item, value in current.items():
                if value and item != "cycle_start" and item != "cycle_end":
                    msg += f"• {item.title()}: {value}\n"

        return msg
    
    # =========================================================================
    # PRICING PAGE
    # =========================================================================
    
    def get_pricing_page(self) -> str:
        """Get formatted pricing for website"""
        return f"""
**SiteMind Pricing**
Simple, transparent, like Cursor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**STARTER** — $299/month
For small teams getting started

✓ 10 users
✓ 2 projects  
✓ 300 queries/month
✓ 10 documents
✓ 50 photos
✓ 5 GB storage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**PROFESSIONAL** — $499/month  ⭐ POPULAR
For growing construction companies

✓ 25 users
✓ 5 projects
✓ 500 queries/month
✓ 20 documents
✓ 100 photos
✓ 10 GB storage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ENTERPRISE** — $999/month
For large developers

✓ 100 users
✓ 20 projects
✓ 2,000 queries/month
✓ 100 documents
✓ 500 photos
✓ 50 GB storage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**USAGE PRICING** (when you exceed included limits)

• Additional user: $10/user/month
• Additional project: $100/project/month
• Additional query: $0.15/query
• Additional document: $2.50/document
• Additional photo: $0.50/photo
• Additional storage: $1.00/GB

_Usage is tracked during your billing cycle and charged 
in the following month's invoice (just like Cursor)_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Annual billing:** Save 17% (2 months free)

All plans include:
• 24/7 WhatsApp support
• Complete audit trail
• Personal onboarding
• ROI reporting
"""
    
    # =========================================================================
    # MARGIN VERIFICATION
    # =========================================================================
    
    def verify_margins(self) -> Dict[str, Any]:
        """Verify 80%+ margins on usage pricing"""
        results = {}
        for item in ["query", "document", "photo", "storage_gb"]:
            cost = self.COSTS.get(item, 0)
            price = self.USAGE_PRICES[item]
            margin = ((price - cost) / price) * 100 if price > 0 else 100
            results[item] = {
                "cost": cost,
                "price": price,
                "margin": f"{margin:.0f}%",
                "status": "✅" if margin >= 80 else "❌",
            }
        return results


# Singleton instance
pricing_service = PricingService()
