"""
SiteMind Pricing Service
ONE subscription per company. Unlimited projects.

CURSOR-STYLE PRICING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$1,000/month per COMPANY

Includes:
• Unlimited projects
• Unlimited users
• 1,000 queries/month
• 50 documents/month
• 200 photos/month
• 25 GB storage

Usage overage (billed next cycle):
• Query:    $0.10/query
• Document: $2.00/document
• Photo:    $0.40/photo
• Storage:  $0.50/GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS WORKS:
- Big company (10 projects): $1000 is nothing
- Small company (1 project): Still worth it
- Heavy usage: They pay more (fair)
- Simple billing: One invoice per company

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class PricingService:
    """
    Simple pricing: $1000/company + usage
    """
    
    def __init__(self):
        # =================================================================
        # THE ONE PLAN - PER COMPANY
        # =================================================================
        
        self.FLAT_FEE_USD = 1000  # $1000/month per company
        
        # What's included in the flat fee
        self.INCLUDED = {
            "projects": "unlimited",   # No limit on projects!
            "users": "unlimited",      # No limit on users!
            "queries": 1000,           # 1000 queries/month
            "documents": 50,           # 50 documents/month
            "photos": 200,             # 200 photos/month
            "storage_gb": 25,          # 25 GB storage
        }
        
        # =================================================================
        # USAGE PRICING (80%+ margins, slightly lower per-unit for volume)
        # =================================================================
        
        # Our costs
        self.COSTS = {
            "query": 0.02,       # Gemini API (bulk)
            "document": 0.40,    # Gemini Vision
            "photo": 0.08,       # Gemini Vision
            "storage_gb": 0.02,  # Supabase
        }
        
        # Our prices (80%+ margin)
        self.USAGE_PRICES = {
            "query": 0.10,       # $0.10/query (80% margin)
            "document": 2.00,    # $2.00/document (80% margin)
            "photo": 0.40,       # $0.40/photo (80% margin)
            "storage_gb": 0.50,  # $0.50/GB (96% margin)
        }
        
        # =================================================================
        # DISCOUNTS
        # =================================================================
        
        self.ANNUAL_DISCOUNT = 0.17      # 2 months free (pay 10, get 12)
        self.FOUNDING_DISCOUNT = 0.25    # 25% off for first 10 customers
        
        # =================================================================
        # CONVERSION
        # =================================================================
        
        self.USD_TO_INR = 83
    
    # =========================================================================
    # PRICING INFO
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
            "annual_price_usd": self.FLAT_FEE_USD * 12 * (1 - self.ANNUAL_DISCOUNT),
        }
    
    def get_pricing_page(self) -> str:
        """Formatted pricing for display"""
        annual = int(self.FLAT_FEE_USD * 12 * (1 - self.ANNUAL_DISCOUNT))
        
        return f"""
🏗️ **SiteMind Pricing**

ONE subscription. ALL your projects.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**${self.FLAT_FEE_USD}/month** per company

✓ **Unlimited projects** - 1 or 100, same price
✓ **Unlimited users** - Add your whole team
✓ {self.INCLUDED['queries']:,} queries/month
✓ {self.INCLUDED['documents']} documents/month
✓ {self.INCLUDED['photos']} photos/month
✓ {self.INCLUDED['storage_gb']} GB storage
✓ WhatsApp access 24/7
✓ Complete audit trail
✓ Personal onboarding

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Usage (when you exceed limits)**

• Query: ${self.USAGE_PRICES['query']}/query
• Document: ${self.USAGE_PRICES['document']}/document
• Photo: ${self.USAGE_PRICES['photo']}/photo
• Storage: ${self.USAGE_PRICES['storage_gb']}/GB

_Tracked during month, billed next cycle_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Annual:** ${annual:,}/year (save {int(self.ANNUAL_DISCOUNT * 100)}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # =========================================================================
    # USAGE CALCULATION
    # =========================================================================
    
    def calculate_usage(
        self,
        queries: int,
        documents: int,
        photos: int,
        storage_gb: float,
    ) -> Dict[str, Any]:
        """Calculate usage charges (overages only)"""
        
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
        
        return {
            "breakdown": breakdown,
            "total_usd": round(total, 2),
            "total_inr": round(total * self.USD_TO_INR, 2),
        }
    
    # =========================================================================
    # INVOICE GENERATION
    # =========================================================================
    
    def generate_invoice(
        self,
        company_name: str,
        previous_usage: Dict = None,
        is_founding: bool = False,
        is_annual: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate invoice:
        - Flat fee for THIS cycle
        - Usage from PREVIOUS cycle
        """
        
        # Flat fee
        if is_annual:
            flat_fee = self.FLAT_FEE_USD * 12 * (1 - self.ANNUAL_DISCOUNT)
            period = "Annual"
        else:
            flat_fee = self.FLAT_FEE_USD
            period = "Monthly"
        
        # Founding discount
        founding_discount = 0
        if is_founding:
            founding_discount = flat_fee * self.FOUNDING_DISCOUNT
            flat_fee = flat_fee - founding_discount
        
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
            "period": period,
            
            "flat_fee_usd": self.FLAT_FEE_USD if not is_annual else self.FLAT_FEE_USD * 12,
            "discount_type": "founding" if is_founding else ("annual" if is_annual else None),
            "discount_amount": founding_discount if is_founding else (self.FLAT_FEE_USD * 12 * self.ANNUAL_DISCOUNT if is_annual else 0),
            "net_flat_fee_usd": flat_fee,
            
            "usage": usage_charges,
            "usage_total_usd": usage_total,
            
            "total_usd": round(total, 2),
            "total_inr": round(total * self.USD_TO_INR, 2),
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
SUBSCRIPTION ({invoice['period']})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SiteMind Enterprise                      ${invoice['flat_fee_usd']:,.2f}
• Unlimited projects
• Unlimited users
• {self.INCLUDED['queries']:,} queries
• {self.INCLUDED['documents']} documents
• {self.INCLUDED['photos']} photos
• {self.INCLUDED['storage_gb']} GB storage"""

        if invoice.get('discount_type') == 'founding':
            msg += f"""

Founding Customer Discount (-25%)       -${invoice['discount_amount']:,.2f}"""
        elif invoice.get('discount_type') == 'annual':
            msg += f"""

Annual Discount (-17%)                  -${invoice['discount_amount']:,.2f}"""

        if invoice.get('discount_type'):
            msg += f"""
                                         ─────────
Subscription Total                       ${invoice['net_flat_fee_usd']:,.2f}"""

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
{label:12}  {data['used']:>6} used ({data['included']:,} included)
              {data['overage']:>6} extra × ${data['rate']:.2f}      ${data['charge']:>8.2f}"""
            
            msg += f"""

                                         ─────────
Usage Total                              ${usage['total_usd']:>8.2f}"""

        msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL DUE                                ${invoice['total_usd']:>8.2f}
                                         ₹{invoice['total_inr']:>,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return msg
    
    # =========================================================================
    # MARGIN VERIFICATION
    # =========================================================================
    
    def verify_margins(self) -> Dict[str, Any]:
        """Verify 80%+ margins on usage"""
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
