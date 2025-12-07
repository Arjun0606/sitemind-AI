"""
SiteMind Pricing Service
ONE PLAN: $500/month flat + Usage

SIMPLE PRICING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SiteMind Enterprise: $500/month
+ Usage charges (billed next cycle)

That's it. One plan. For everyone.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass


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
    Simple pricing: $500 flat + usage
    """
    
    def __init__(self):
        # =================================================================
        # THE ONE PLAN
        # =================================================================
        
        self.FLAT_FEE_USD = 500  # $500/month flat
        
        # What's included in the flat fee
        self.INCLUDED = {
            "users": "unlimited",      # No limit on users
            "projects": "unlimited",   # No limit on projects
            "queries": 500,            # 500 queries/month
            "documents": 20,           # 20 documents/month
            "photos": 100,             # 100 photos/month
            "storage_gb": 10,          # 10 GB storage
        }
        
        # =================================================================
        # USAGE PRICING (80%+ margins)
        # =================================================================
        
        # Our costs
        self.COSTS = {
            "query": 0.03,       # Gemini API
            "document": 0.50,    # Gemini Vision
            "photo": 0.10,       # Gemini Vision
            "storage_gb": 0.02,  # Supabase
        }
        
        # Our prices (80%+ margin)
        self.USAGE_PRICES = {
            "query": 0.15,       # $0.15/query
            "document": 2.50,    # $2.50/document
            "photo": 0.50,       # $0.50/photo
            "storage_gb": 1.00,  # $1.00/GB
        }
        
        # =================================================================
        # OTHER
        # =================================================================
        
        self.ANNUAL_DISCOUNT = 0.17  # 2 months free
        self.FOUNDING_DISCOUNT = 0.25  # 25% off for pilots
        self.USD_TO_INR = 83
        
        # Usage tracking
        self._usage: Dict[str, UsageTracker] = {}
    
    # =========================================================================
    # USAGE TRACKING
    # =========================================================================
    
    def track_query(self, company_id: str):
        """Track a query"""
        self._ensure_tracker(company_id)
        self._usage[company_id].queries += 1
    
    def track_document(self, company_id: str):
        """Track a document processed"""
        self._ensure_tracker(company_id)
        self._usage[company_id].documents += 1
    
    def track_photo(self, company_id: str):
        """Track a photo analyzed"""
        self._ensure_tracker(company_id)
        self._usage[company_id].photos += 1
    
    def track_storage(self, company_id: str, gb: float):
        """Track storage (peak usage)"""
        self._ensure_tracker(company_id)
        self._usage[company_id].storage_gb = max(
            self._usage[company_id].storage_gb, gb
        )
    
    def _ensure_tracker(self, company_id: str):
        """Ensure tracker exists"""
        if company_id not in self._usage:
            now = datetime.utcnow()
            self._usage[company_id] = UsageTracker(
                company_id=company_id,
                cycle_start=now.isoformat(),
                cycle_end=(now + timedelta(days=30)).isoformat(),
            )
    
    def get_current_usage(self, company_id: str) -> Dict[str, Any]:
        """Get current cycle usage"""
        tracker = self._usage.get(company_id)
        if not tracker:
            return {
                "queries": 0,
                "documents": 0,
                "photos": 0,
                "storage_gb": 0,
            }
        
        return {
            "queries": tracker.queries,
            "documents": tracker.documents,
            "photos": tracker.photos,
            "storage_gb": tracker.storage_gb,
            "cycle_start": tracker.cycle_start,
            "cycle_end": tracker.cycle_end,
        }
    
    def reset_cycle(self, company_id: str) -> Dict[str, Any]:
        """Reset cycle and return final usage"""
        usage = self.get_current_usage(company_id)
        if company_id in self._usage:
            del self._usage[company_id]
        return usage
    
    # =========================================================================
    # CALCULATE USAGE CHARGES
    # =========================================================================
    
    def calculate_usage(
        self,
        queries: int,
        documents: int,
        photos: int,
        storage_gb: float,
    ) -> Dict[str, Any]:
        """Calculate usage charges"""
        
        breakdown = {
            "queries": {
                "used": queries,
                "included": self.INCLUDED["queries"],
                "overage": max(0, queries - self.INCLUDED["queries"]),
                "rate": self.USAGE_PRICES["query"],
                "charge": max(0, queries - self.INCLUDED["queries"]) * self.USAGE_PRICES["query"],
            },
            "documents": {
                "used": documents,
                "included": self.INCLUDED["documents"],
                "overage": max(0, documents - self.INCLUDED["documents"]),
                "rate": self.USAGE_PRICES["document"],
                "charge": max(0, documents - self.INCLUDED["documents"]) * self.USAGE_PRICES["document"],
            },
            "photos": {
                "used": photos,
                "included": self.INCLUDED["photos"],
                "overage": max(0, photos - self.INCLUDED["photos"]),
                "rate": self.USAGE_PRICES["photo"],
                "charge": max(0, photos - self.INCLUDED["photos"]) * self.USAGE_PRICES["photo"],
            },
            "storage_gb": {
                "used": storage_gb,
                "included": self.INCLUDED["storage_gb"],
                "overage": max(0, storage_gb - self.INCLUDED["storage_gb"]),
                "rate": self.USAGE_PRICES["storage_gb"],
                "charge": max(0, storage_gb - self.INCLUDED["storage_gb"]) * self.USAGE_PRICES["storage_gb"],
            },
        }
        
        total = sum(item["charge"] for item in breakdown.values())
        
        # Our cost calculation
        our_cost = (
            queries * self.COSTS["query"] +
            documents * self.COSTS["document"] +
            photos * self.COSTS["photo"] +
            storage_gb * self.COSTS["storage_gb"]
        )
        
        margin = ((total - our_cost) / total * 100) if total > 0 else 100
        
        return {
            "breakdown": breakdown,
            "total_usd": round(total, 2),
            "total_inr": round(total * self.USD_TO_INR, 2),
            "our_cost": round(our_cost, 2),
            "margin_percent": round(margin, 1),
        }
    
    # =========================================================================
    # GENERATE INVOICE
    # =========================================================================
    
    def generate_invoice(
        self,
        company_name: str,
        previous_usage: Dict = None,
        is_founding: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate invoice:
        - $500 flat fee for THIS cycle
        - Usage from PREVIOUS cycle
        """
        
        # Flat fee
        flat_fee = self.FLAT_FEE_USD
        if is_founding:
            flat_fee = flat_fee * (1 - self.FOUNDING_DISCOUNT)
        
        # Usage from previous cycle
        usage_charges = None
        usage_total = 0
        
        if previous_usage:
            usage_charges = self.calculate_usage(
                queries=previous_usage.get("queries", 0),
                documents=previous_usage.get("documents", 0),
                photos=previous_usage.get("photos", 0),
                storage_gb=previous_usage.get("storage_gb", 0),
            )
            usage_total = usage_charges["total_usd"]
        
        total = flat_fee + usage_total
        
        return {
            "invoice_id": f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company": company_name,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "due_date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
            
            "flat_fee_usd": flat_fee,
            "is_founding": is_founding,
            "founding_discount": self.FOUNDING_DISCOUNT if is_founding else 0,
            
            "usage": usage_charges,
            "usage_total_usd": usage_total,
            
            "total_usd": total,
            "total_inr": total * self.USD_TO_INR,
        }
    
    def format_invoice(self, invoice: Dict) -> str:
        """Format invoice for display"""
        
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    SITEMIND INVOICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Invoice:  {invoice['invoice_id']}
Company:  {invoice['company']}
Date:     {invoice['date']}
Due:      {invoice['due_date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUBSCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SiteMind Enterprise                        ${self.FLAT_FEE_USD:.2f}"""

        if invoice.get('is_founding'):
            msg += f"""
Founding Customer Discount (-{int(invoice['founding_discount']*100)}%)   -${self.FLAT_FEE_USD * invoice['founding_discount']:.2f}
                                           ─────────
Subscription Total                         ${invoice['flat_fee_usd']:.2f}"""

        usage = invoice.get('usage')
        if usage and usage['total_usd'] > 0:
            msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE (from previous billing cycle)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for item, data in usage['breakdown'].items():
                if data['overage'] > 0:
                    label = item.replace('_', ' ').title()
                    msg += f"""
{label:12}  {data['used']:>5} used ({data['included']} included)
              {data['overage']:>5} extra × ${data['rate']:.2f}        ${data['charge']:>8.2f}"""
            
            msg += f"""

                                           ─────────
Usage Total                                ${usage['total_usd']:>8.2f}"""

        msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL DUE                                  ${invoice['total_usd']:>8.2f}
                                           ₹{invoice['total_inr']:>,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return msg
    
    # =========================================================================
    # PRICING PAGE
    # =========================================================================
    
    def get_pricing(self) -> Dict[str, Any]:
        """Get pricing info"""
        return {
            "plan": "SiteMind Enterprise",
            "flat_fee_usd": self.FLAT_FEE_USD,
            "flat_fee_inr": self.FLAT_FEE_USD * self.USD_TO_INR,
            "included": self.INCLUDED,
            "usage_prices": self.USAGE_PRICES,
            "annual_discount": self.ANNUAL_DISCOUNT,
        }
    
    def get_pricing_page(self) -> str:
        """Formatted pricing"""
        return f"""
**SiteMind Pricing**
One plan. Simple.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**${self.FLAT_FEE_USD}/month**

Everything you need:
✓ Unlimited users
✓ Unlimited projects
✓ {self.INCLUDED['queries']} queries/month
✓ {self.INCLUDED['documents']} documents/month
✓ {self.INCLUDED['photos']} photos/month
✓ {self.INCLUDED['storage_gb']} GB storage
✓ 24/7 WhatsApp support
✓ Complete audit trail
✓ Personal onboarding

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Usage (when you exceed included limits)**

• Query: ${self.USAGE_PRICES['query']}/query
• Document: ${self.USAGE_PRICES['document']}/document
• Photo: ${self.USAGE_PRICES['photo']}/photo
• Storage: ${self.USAGE_PRICES['storage_gb']}/GB

_Usage tracked during cycle, billed next month_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Annual:** Save {int(self.ANNUAL_DISCOUNT * 100)}% (${int(self.FLAT_FEE_USD * 12 * (1 - self.ANNUAL_DISCOUNT))}/year)
"""
    
    # =========================================================================
    # MARGIN CHECK
    # =========================================================================
    
    def verify_margins(self) -> Dict[str, Any]:
        """Verify 80%+ margins"""
        results = {}
        for item in ["query", "document", "photo", "storage_gb"]:
            cost = self.COSTS[item]
            price = self.USAGE_PRICES[item]
            margin = ((price - cost) / price) * 100
            results[item] = {
                "cost": f"${cost}",
                "price": f"${price}",
                "margin": f"{margin:.0f}%",
                "ok": "✅" if margin >= 80 else "❌",
            }
        return results


# Singleton instance
pricing_service = PricingService()
