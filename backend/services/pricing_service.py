"""
SiteMind Pricing Service
$1,000/company + usage-based billing with 90% margins

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COST STRUCTURE (Our actual costs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUPERMEMORY.AI ($19/month Pro plan):
- 3M tokens included
- 100K searches included
- Overage: $0.01/1K tokens = $10/M tokens
- Overage: $0.10/1K queries = $100/M queries

GEMINI 3 PRO:
- Input: $2/million tokens
- Output: $12/million tokens
- Average ~$7/M blended (60% input, 40% output)

SUPABASE:
- Storage: ~$0.021/GB/month
- Bandwidth: ~$0.09/GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class PricingService:
    """
    Cursor-style pricing: Flat fee + usage overages at 90% margin
    """
    
    def __init__(self):
        # =================================================================
        # FLAT FEE - PER COMPANY
        # =================================================================
        
        self.FLAT_FEE_USD = 1000  # $1000/month per company
        
        # What's included in the flat fee
        self.INCLUDED = {
            "projects": "unlimited",
            "users": "unlimited",
            "queries": 1000,          # AI queries/month
            "documents": 50,          # Document uploads/month
            "photos": 200,            # Photo analyses/month
            "storage_gb": 25,         # Storage
            "memory_searches": 5000,  # Supermemory searches
        }
        
        # =================================================================
        # OUR COSTS (what we actually pay)
        # =================================================================
        
        self.COSTS = {
            # Gemini 3 Pro costs
            "query": 0.015,           # ~$15/1000 queries (avg tokens per query)
            
            # Per document (Gemini vision for PDF + Supermemory storage)
            "document": 0.05,         # ~$50/1000 docs
            
            # Per photo (Gemini vision analysis)
            "photo": 0.02,            # ~$20/1000 photos
            
            # Storage (Supabase)
            "storage_gb": 0.021,      # ~$0.02/GB/month
            
            # Supermemory (beyond included)
            "memory_token": 0.00001,  # $0.01/1K = $0.00001/token
            "memory_search": 0.0001,  # $0.10/1K = $0.0001/search
        }
        
        # =================================================================
        # OUR PRICES (10x cost = 90% margin)
        # =================================================================
        
        self.USAGE_PRICES = {
            # Query overage: Cost $0.015 → Price $0.15 (90% margin)
            "query": 0.15,
            
            # Document overage: Cost $0.05 → Price $0.50 (90% margin)
            "document": 0.50,
            
            # Photo overage: Cost $0.02 → Price $0.20 (90% margin)
            "photo": 0.20,
            
            # Storage overage: Cost $0.021 → Price $0.25 (92% margin)
            "storage_gb": 0.25,
            
            # Memory search overage: Cost $0.0001 → Price $0.001 (90% margin)
            "memory_search": 0.001,
        }
        
        # =================================================================
        # DISCOUNTS
        # =================================================================
        
        self.ANNUAL_DISCOUNT = 0.17      # 2 months free
        self.FOUNDING_DISCOUNT = 0.25    # First 10 customers
        self.PILOT_DISCOUNT = 1.0        # 100% off for pilots
        
        # Currency
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
✓ {self.INCLUDED['queries']:,} AI queries/month
✓ {self.INCLUDED['documents']} documents/month
✓ {self.INCLUDED['photos']} photo analyses/month
✓ {self.INCLUDED['storage_gb']} GB storage
✓ WhatsApp access 24/7
✓ Complete audit trail
✓ IS code database
✓ Safety detection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Usage (when you exceed limits)**

• Query: ${self.USAGE_PRICES['query']:.2f}/query
• Document: ${self.USAGE_PRICES['document']:.2f}/document
• Photo: ${self.USAGE_PRICES['photo']:.2f}/photo
• Storage: ${self.USAGE_PRICES['storage_gb']:.2f}/GB

_Tracked during month, billed next cycle_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Annual:** ${annual:,}/year (save {int(self.ANNUAL_DISCOUNT * 100)}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # =========================================================================
    # COST CALCULATION
    # =========================================================================
    
    def calculate_our_cost(
        self,
        queries: int,
        documents: int,
        photos: int,
        storage_gb: float,
        memory_searches: int = 0,
    ) -> Dict[str, Any]:
        """Calculate what WE pay for this usage"""
        
        # Supermemory base cost (Pro plan)
        supermemory_base = 19.0  # $19/month
        
        # Gemini costs
        gemini_cost = (
            queries * self.COSTS["query"] +
            documents * self.COSTS["document"] +
            photos * self.COSTS["photo"]
        )
        
        # Storage cost (Supabase)
        storage_cost = storage_gb * self.COSTS["storage_gb"]
        
        # Memory overage (beyond Pro plan included)
        memory_overage_cost = 0
        if memory_searches > 100000:  # Pro plan includes 100K
            excess = memory_searches - 100000
            memory_overage_cost = excess * self.COSTS["memory_search"]
        
        total = supermemory_base + gemini_cost + storage_cost + memory_overage_cost
        
        return {
            "supermemory_base": supermemory_base,
            "gemini": round(gemini_cost, 2),
            "storage": round(storage_cost, 2),
            "memory_overage": round(memory_overage_cost, 2),
            "total": round(total, 2),
        }
    
    def calculate_usage_charges(
        self,
        queries: int,
        documents: int,
        photos: int,
        storage_gb: float,
    ) -> Dict[str, Any]:
        """Calculate usage charges for customer (overages only)"""
        
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
    # MARGIN VERIFICATION
    # =========================================================================
    
    def verify_margins(self) -> Dict[str, Any]:
        """Verify we maintain 90%+ margins on all usage"""
        results = {}
        
        items = [
            ("query", "Query"),
            ("document", "Document"),
            ("photo", "Photo"),
            ("storage_gb", "Storage"),
        ]
        
        for key, label in items:
            cost = self.COSTS.get(key, 0)
            price = self.USAGE_PRICES.get(key, 0)
            
            if price > 0:
                margin = ((price - cost) / price) * 100
            else:
                margin = 0
            
            results[key] = {
                "label": label,
                "cost": f"${cost:.4f}",
                "price": f"${price:.2f}",
                "margin": f"{margin:.0f}%",
                "status": "✅" if margin >= 85 else "⚠️" if margin >= 70 else "❌",
            }
        
        return results
    
    def print_margin_report(self) -> str:
        """Print margin report"""
        margins = self.verify_margins()
        
        lines = [
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "             MARGIN VERIFICATION REPORT",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"{'Item':<12} {'Our Cost':<12} {'Our Price':<12} {'Margin':<10} {'Status'}",
            "─" * 55,
        ]
        
        for key, data in margins.items():
            lines.append(
                f"{data['label']:<12} {data['cost']:<12} {data['price']:<12} {data['margin']:<10} {data['status']}"
            )
        
        lines.extend([
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
        ])
        
        return "\n".join(lines)
    
    # =========================================================================
    # URBANRISE SIMULATION
    # =========================================================================
    
    def simulate_urbanrise_month(self) -> Dict[str, Any]:
        """
        Simulate Urbanrise usage to verify profitability
        
        Assumptions:
        - 30 active projects
        - 500 users
        - Heavy usage
        """
        # Expected usage for a whale like Urbanrise
        queries = 8000        # 8K queries (heavy usage)
        documents = 150       # 150 documents
        photos = 600          # 600 photos
        storage_gb = 40       # 40 GB
        memory_searches = 200000  # Heavy memory usage
        
        # Our costs
        our_cost = self.calculate_our_cost(
            queries, documents, photos, storage_gb, memory_searches
        )
        
        # Customer charges
        customer_charges = self.calculate_usage_charges(
            queries, documents, photos, storage_gb
        )
        
        # Total revenue
        revenue = self.FLAT_FEE_USD + customer_charges["total_usd"]
        
        # Profit
        profit = revenue - our_cost["total"]
        margin = (profit / revenue) * 100 if revenue > 0 else 0
        
        return {
            "company": "Urbanrise (Simulated)",
            "usage": {
                "queries": queries,
                "documents": documents,
                "photos": photos,
                "storage_gb": storage_gb,
            },
            "our_cost": our_cost,
            "flat_fee": self.FLAT_FEE_USD,
            "usage_charges": customer_charges["total_usd"],
            "total_revenue": round(revenue, 2),
            "profit": round(profit, 2),
            "margin": f"{margin:.0f}%",
        }
    
    def print_urbanrise_simulation(self) -> str:
        """Print Urbanrise simulation"""
        sim = self.simulate_urbanrise_month()
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         URBANRISE MONTHLY SIMULATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USAGE (30 projects, 500 users):
• Queries:     {sim['usage']['queries']:,}
• Documents:   {sim['usage']['documents']}
• Photos:      {sim['usage']['photos']}
• Storage:     {sim['usage']['storage_gb']} GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUR COSTS:
• Supermemory:  ${sim['our_cost']['supermemory_base']:.2f}
• Gemini API:   ${sim['our_cost']['gemini']:.2f}
• Storage:      ${sim['our_cost']['storage']:.2f}
• Memory extra: ${sim['our_cost']['memory_overage']:.2f}
─────────────────────────────────
• TOTAL COST:   ${sim['our_cost']['total']:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REVENUE:
• Flat Fee:     ${sim['flat_fee']:,.2f}
• Usage:        ${sim['usage_charges']:.2f}
─────────────────────────────────
• TOTAL:        ${sim['total_revenue']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROFIT:         ${sim['profit']:,.2f}
MARGIN:         {sim['margin']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANNUAL PROJECTION:
• Revenue:      ${sim['total_revenue'] * 12:,.0f}/year
• Profit:       ${sim['profit'] * 12:,.0f}/year

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # =========================================================================
    # INVOICE GENERATION
    # =========================================================================
    
    def generate_invoice(
        self,
        company_name: str,
        previous_usage: Dict = None,
        is_founding: bool = False,
        is_annual: bool = False,
        is_pilot: bool = False,
    ) -> Dict[str, Any]:
        """Generate invoice"""
        
        # Pilot = free
        if is_pilot:
            return {
                "invoice_id": f"INV-PILOT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "company": company_name,
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "period": "Pilot",
                "flat_fee_usd": 0,
                "discount_type": "pilot",
                "discount_amount": self.FLAT_FEE_USD,
                "usage": None,
                "total_usd": 0,
                "total_inr": 0,
                "note": "Pilot program - first 3 months free",
            }
        
        # Calculate flat fee
        if is_annual:
            flat_fee = self.FLAT_FEE_USD * 12 * (1 - self.ANNUAL_DISCOUNT)
            period = "Annual"
        else:
            flat_fee = self.FLAT_FEE_USD
            period = "Monthly"
        
        # Founding discount
        founding_discount = 0
        discount_type = None
        if is_founding:
            founding_discount = flat_fee * self.FOUNDING_DISCOUNT
            flat_fee = flat_fee - founding_discount
            discount_type = "founding"
        elif is_annual:
            discount_type = "annual"
        
        # Usage charges from previous cycle
        usage_charges = None
        usage_total = 0
        
        if previous_usage:
            usage_charges = self.calculate_usage_charges(
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
            "discount_type": discount_type,
            "discount_amount": founding_discount if is_founding else (
                self.FLAT_FEE_USD * 12 * self.ANNUAL_DISCOUNT if is_annual else 0
            ),
            "net_flat_fee_usd": flat_fee,
            "usage": usage_charges,
            "usage_total_usd": usage_total,
            "total_usd": round(total, 2),
            "total_inr": round(total * self.USD_TO_INR, 2),
        }
    
    def format_invoice(self, invoice: Dict) -> str:
        """Format invoice for display"""
        
        if invoice.get("note") and "Pilot" in invoice.get("period", ""):
            return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    SITEMIND INVOICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Invoice:  {invoice['invoice_id']}
Company:  {invoice['company']}
Date:     {invoice['date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 PILOT PROGRAM

{invoice['note']}

SiteMind Enterprise                      $1,000.00
Pilot Discount (100%)                   -$1,000.00
                                         ─────────
TOTAL DUE                                    $0.00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
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
        if usage and usage.get('total_usd', 0) > 0:
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


# Singleton instance
pricing_service = PricingService()


# Quick test
if __name__ == "__main__":
    print(pricing_service.print_margin_report())
    print(pricing_service.print_urbanrise_simulation())
