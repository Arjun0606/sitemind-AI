"""
SiteMind Pricing Service
$1,000/company + usage-based billing with 90% margins

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COST STRUCTURE - ALL SERVICES WITH OVERAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SUPERMEMORY.AI ($19/month Pro plan):
   - Included: 3M tokens, 100K searches
   - Token overage: $0.01/1K tokens = $10/M tokens
   - Search overage: $0.10/1K queries

2. GEMINI 3 PRO:
   - Input: $2/million tokens
   - Output: $12/million tokens
   - Per query (~1K input, 500 output): ~$0.008

3. SUPABASE:
   - Pro plan: $25/month
   - Storage: $0.021/GB/month
   - Bandwidth: $0.09/GB
   - Database egress: included in pro

4. TWILIO (WhatsApp):
   - WhatsApp message: $0.005/message sent
   - Incoming: Free

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRICING FORMULA: Our Price = Our Cost × 10 (90% margin)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class PricingService:
    """
    Pricing with 90% margins on ALL costs including overages
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
            "storage_gb": 50,         # 50 GB included (generous!)
        }
        
        # =================================================================
        # OUR ACTUAL COSTS (PER UNIT) - INCLUDING ALL OVERAGES
        # =================================================================
        # 
        # Sources:
        # - Gemini 3 Pro: https://ai.google.dev/gemini-api/docs/gemini-3
        #   Input: $2/M, Output: $12/M (under 200k context)
        # - Supermemory: https://console.supermemory.ai/billing
        #   Tokens: $0.01/1K, Searches: $0.10/1K
        # - Supabase: $0.021/GB storage, $0.09/GB bandwidth
        # - Twilio WhatsApp: $0.005/message
        #
        self.COSTS = {
            # ----- PER QUERY -----
            # Gemini 3 Pro: 1K input ($0.002) + 500 output ($0.006) = $0.008
            # Supermemory search: $0.10/1000 = $0.0001
            # Supermemory tokens: 500 tokens × $0.01/1000 = $0.005
            # WhatsApp: 2 messages × $0.005 = $0.01
            # TOTAL: $0.0231
            "query": 0.008 + 0.0001 + 0.005 + 0.01,  # = $0.0231
            
            # ----- PER DOCUMENT -----
            # Gemini Vision: 5K input ($0.01) + 1K output ($0.012) = $0.022
            # Supermemory tokens: 2K × $0.01/1K = $0.02
            # Supabase storage: ~1MB = negligible
            # TOTAL: $0.043
            "document": 0.022 + 0.02 + 0.001,  # = $0.043
            
            # ----- PER PHOTO -----
            # Gemini Vision: 2K input ($0.004) + 500 output ($0.006) = $0.01
            # Supermemory tokens: 500 × $0.01/1K = $0.005
            # Supabase storage: ~2MB = negligible
            # TOTAL: $0.015
            "photo": 0.01 + 0.005 + 0.0001,  # = $0.0151
            
            # ----- STORAGE (per GB/month) -----
            # From supabase.com/pricing:
            # - File storage: $0.021/GB (beyond 100 GB included)
            # - Egress: $0.09/GB (beyond 250 GB included)
            # Assuming 2x reads per storage = $0.18 egress per GB stored
            # TOTAL: $0.021 + $0.18 = $0.201
            # BUT at scale with many customers, we exceed included limits fast
            # Worst case: $0.021 storage + $0.09 egress (per read, not 2x)
            # Conservative: $0.111/GB (storage + 1x egress)
            "storage_gb": 0.021 + 0.09,  # = $0.111 (conservative)
            
            # ----- WHATSAPP (already included in query) -----
            "whatsapp_message": 0.005,
        }
        
        # =================================================================
        # FIXED MONTHLY COSTS (OUR BASE)
        # =================================================================
        
        self.FIXED_COSTS = {
            "supermemory_pro": 19.0,    # $19/month
            "supabase_pro": 25.0,        # $25/month
            "railway_hosting": 20.0,     # ~$20/month
            "twilio_number": 15.0,       # ~$15/month for WhatsApp number
        }
        
        self.TOTAL_FIXED_COST = sum(self.FIXED_COSTS.values())  # = $79/month
        
        # =================================================================
        # OUR PRICES (Cost × 10 = 90% margin)
        # =================================================================
        
        self.USAGE_PRICES = {
            # Query: Cost $0.0231 × 10 = $0.25 (90% margin)
            "query": 0.25,
            
            # Document: Cost $0.043 × 10 = $0.45 (90% margin)
            "document": 0.45,
            
            # Photo: Cost $0.015 × 10 = $0.15 (90% margin)
            "photo": 0.15,
            
            # Storage: Cost $0.201 × 10 = $2.00 (90% margin)
            "storage_gb": 2.00,
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
    # COST CALCULATION
    # =========================================================================
    
    def calculate_our_cost(
        self,
        queries: int,
        documents: int,
        photos: int,
        storage_gb: float,
    ) -> Dict[str, Any]:
        """Calculate what WE actually pay for this usage (all overages included)"""
        
        # Variable costs (WhatsApp is included in query cost)
        query_cost = queries * self.COSTS["query"]  # Includes Gemini + Supermemory + WhatsApp
        document_cost = documents * self.COSTS["document"]
        photo_cost = photos * self.COSTS["photo"]
        storage_cost = storage_gb * self.COSTS["storage_gb"]
        
        variable_total = query_cost + document_cost + photo_cost + storage_cost
        
        # Total including fixed costs
        total = self.TOTAL_FIXED_COST + variable_total
        
        return {
            "fixed_costs": {
                "supermemory": self.FIXED_COSTS["supermemory_pro"],
                "supabase": self.FIXED_COSTS["supabase_pro"],
                "railway": self.FIXED_COSTS["railway_hosting"],
                "twilio": self.FIXED_COSTS["twilio_number"],
                "subtotal": self.TOTAL_FIXED_COST,
            },
            "variable_costs": {
                "queries": round(query_cost, 2),
                "documents": round(document_cost, 2),
                "photos": round(photo_cost, 2),
                "storage": round(storage_cost, 2),
                "subtotal": round(variable_total, 2),
            },
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
            ("query", "Query", "per query"),
            ("document", "Document", "per doc"),
            ("photo", "Photo", "per photo"),
            ("storage_gb", "Storage", "per GB"),
        ]
        
        for key, label, unit in items:
            cost = self.COSTS.get(key, 0)
            price = self.USAGE_PRICES.get(key, 0)
            
            if price > 0:
                margin = ((price - cost) / price) * 100
                profit_per_unit = price - cost
            else:
                margin = 0
                profit_per_unit = 0
            
            results[key] = {
                "label": label,
                "unit": unit,
                "our_cost": f"${cost:.4f}",
                "our_price": f"${price:.2f}",
                "profit": f"${profit_per_unit:.4f}",
                "margin": f"{margin:.0f}%",
                "status": "✅" if margin >= 85 else "⚠️" if margin >= 70 else "❌",
            }
        
        return results
    
    def print_margin_report(self) -> str:
        """Print detailed margin report"""
        margins = self.verify_margins()
        
        lines = [
            "",
            "━" * 70,
            "                    MARGIN VERIFICATION REPORT",
            "━" * 70,
            "",
            f"{'Item':<12} {'Our Cost':<14} {'Our Price':<12} {'Profit':<12} {'Margin':<10} {'OK'}",
            "─" * 70,
        ]
        
        for key, data in margins.items():
            lines.append(
                f"{data['label']:<12} {data['our_cost']:<14} {data['our_price']:<12} {data['profit']:<12} {data['margin']:<10} {data['status']}"
            )
        
        lines.extend([
            "",
            "─" * 70,
            "COST BREAKDOWN PER UNIT:",
            "─" * 70,
            "",
            "Query ($0.0082 total):",
            f"  • Gemini 3 Pro:     $0.008 (1K input + 500 output tokens)",
            f"  • Supermemory:      $0.0001 (search) + $0.000005 (tokens)",
            "",
            "Document ($0.035 total):",
            f"  • Gemini Vision:    $0.035 (PDF processing ~5K tokens)",
            f"  • Supermemory:      $0.00002 (storage)",
            f"  • Supabase:         $0.00002 (file storage)",
            "",
            "Photo ($0.016 total):",
            f"  • Gemini Vision:    $0.016 (image analysis ~2K tokens)",
            f"  • Supermemory:      $0.000005 (storage)",
            f"  • Supabase:         $0.00004 (file storage)",
            "",
            "Storage per GB ($0.20 total):",
            f"  • Supabase storage: $0.021",
            f"  • Bandwidth (2x):   $0.18",
            "",
            "━" * 70,
            f"FIXED MONTHLY COSTS: ${self.TOTAL_FIXED_COST:.2f}",
            "━" * 70,
            f"  • Supermemory Pro:  ${self.FIXED_COSTS['supermemory_pro']:.2f}",
            f"  • Supabase Pro:     ${self.FIXED_COSTS['supabase_pro']:.2f}",
            f"  • Railway:          ${self.FIXED_COSTS['railway_hosting']:.2f}",
            f"  • Twilio:           ${self.FIXED_COSTS['twilio_number']:.2f}",
            "",
            "━" * 70,
        ])
        
        return "\n".join(lines)
    
    # =========================================================================
    # WHALE SIMULATION
    # =========================================================================
    
    def simulate_whale(
        self,
        name: str,
        projects: int,
        users: int,
        queries_per_user: int = 30,
        docs_per_project: int = 30,
        photos_per_project: int = 150,
        storage_gb: float = 100,
    ) -> Dict[str, Any]:
        """Simulate a whale customer's monthly bill and our profit"""
        
        # Calculate usage
        queries = users * queries_per_user
        documents = projects * docs_per_project
        photos = projects * photos_per_project
        
        # Our costs (WhatsApp included in query cost)
        our_cost = self.calculate_our_cost(
            queries, documents, photos, storage_gb
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
            "company": name,
            "projects": projects,
            "users": users,
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
    
    def print_whale_simulation(self, sim: Dict) -> str:
        """Print whale simulation"""
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         {sim['company'].upper()} - MONTHLY SIMULATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCALE: {sim['projects']} projects, {sim['users']} users

USAGE:
• Queries:         {sim['usage']['queries']:,}
• Documents:       {sim['usage']['documents']:,}
• Photos:          {sim['usage']['photos']:,}
• Storage:         {sim['usage']['storage_gb']} GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUR COSTS (what we actually pay):

Fixed:
  • Supermemory:    ${sim['our_cost']['fixed_costs']['supermemory']:.2f}
  • Supabase:       ${sim['our_cost']['fixed_costs']['supabase']:.2f}
  • Railway:        ${sim['our_cost']['fixed_costs']['railway']:.2f}
  • Twilio:         ${sim['our_cost']['fixed_costs']['twilio']:.2f}
  ─────────────────────────────
  Fixed subtotal:   ${sim['our_cost']['fixed_costs']['subtotal']:.2f}

Variable (includes Gemini + Supermemory + WhatsApp overages):
  • Queries:        ${sim['our_cost']['variable_costs']['queries']:.2f}
  • Documents:      ${sim['our_cost']['variable_costs']['documents']:.2f}
  • Photos:         ${sim['our_cost']['variable_costs']['photos']:.2f}
  • Storage:        ${sim['our_cost']['variable_costs']['storage']:.2f}
  ─────────────────────────────
  Variable subtotal: ${sim['our_cost']['variable_costs']['subtotal']:.2f}

─────────────────────────────────────────────────────────────────────
TOTAL OUR COST:     ${sim['our_cost']['total']:.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CUSTOMER BILL:

  Flat Fee:         ${sim['flat_fee']:,.2f}
  Usage Charges:    ${sim['usage_charges']:,.2f}
  ─────────────────────────────
  TOTAL REVENUE:    ${sim['total_revenue']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 PROFIT:          ${sim['profit']:,.2f}
📈 MARGIN:          {sim['margin']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANNUAL: ${sim['total_revenue'] * 12:,.0f} revenue, ${sim['profit'] * 12:,.0f} profit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
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

✓ **Unlimited projects**
✓ **Unlimited users**  
✓ {self.INCLUDED['queries']:,} AI queries/month
✓ {self.INCLUDED['documents']} documents/month
✓ {self.INCLUDED['photos']} photo analyses/month
✓ {self.INCLUDED['storage_gb']} GB storage
✓ WhatsApp 24/7

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Usage (when you exceed limits)**

• Query: ${self.USAGE_PRICES['query']:.2f}/query
• Document: ${self.USAGE_PRICES['document']:.2f}/document
• Photo: ${self.USAGE_PRICES['photo']:.2f}/photo
• Storage: ${self.USAGE_PRICES['storage_gb']:.2f}/GB

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Annual:** ${annual:,}/year (save {int(self.ANNUAL_DISCOUNT * 100)}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # =========================================================================
    # INVOICE
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
        
        if is_pilot:
            return {
                "invoice_id": f"INV-PILOT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "company": company_name,
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "period": "Pilot",
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
        discount_amount = 0
        discount_type = None
        if is_founding:
            discount_amount = flat_fee * self.FOUNDING_DISCOUNT
            flat_fee = flat_fee - discount_amount
            discount_type = "founding"
        elif is_annual:
            discount_type = "annual"
            discount_amount = self.FLAT_FEE_USD * 12 * self.ANNUAL_DISCOUNT
        
        # Usage charges
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
            "discount_amount": discount_amount,
            "net_flat_fee_usd": flat_fee,
            "usage": usage_charges,
            "usage_total_usd": usage_total,
            "total_usd": round(total, 2),
            "total_inr": round(total * self.USD_TO_INR, 2),
        }


# Singleton instance
pricing_service = PricingService()


# Quick test
if __name__ == "__main__":
    print(pricing_service.print_margin_report())
    
    # Simulate Urbanrise
    urbanrise = pricing_service.simulate_whale(
        name="Urbanrise",
        projects=30,
        users=500,
        queries_per_user=30,
        docs_per_project=30,
        photos_per_project=150,
        storage_gb=100,
    )
    print(pricing_service.print_whale_simulation(urbanrise))
