"""
SiteMind Demo Script
Test the services locally without full setup
"""

import asyncio
from datetime import datetime

# Import services
from services.pricing_service import pricing_service
from services.billing_service import billing_service


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


async def main():
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    🏗️ SITEMIND DEMO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    # =========================================================================
    # PRICING
    # =========================================================================
    print_header("PRICING")
    print(pricing_service.get_pricing_page())
    
    # =========================================================================
    # USAGE SIMULATION
    # =========================================================================
    print_header("USAGE SIMULATION")
    
    company_id = "demo-company-123"
    company_name = "ABC Developers"
    
    print(f"Simulating usage for: {company_name}")
    print()
    
    # Simulate queries
    for i in range(650):  # 150 over limit
        billing_service.track_query(company_id, company_name)
    print(f"✓ Tracked 650 queries (500 included, 150 overage)")
    
    # Simulate documents
    for i in range(28):  # 8 over limit
        billing_service.track_document(company_id)
    print(f"✓ Tracked 28 documents (20 included, 8 overage)")
    
    # Simulate photos
    for i in range(130):  # 30 over limit
        billing_service.track_photo(company_id)
    print(f"✓ Tracked 130 photos (100 included, 30 overage)")
    
    # Simulate storage
    billing_service.track_storage(company_id, 12.5)  # 2.5 over limit
    print(f"✓ Tracked 12.5 GB storage (10 GB included, 2.5 GB overage)")
    
    # =========================================================================
    # USAGE SUMMARY
    # =========================================================================
    print_header("USAGE SUMMARY")
    print(billing_service.get_usage_summary(company_id))
    
    # =========================================================================
    # CHARGES
    # =========================================================================
    print_header("CHARGES BREAKDOWN")
    charges = billing_service.calculate_charges(company_id)
    
    print(f"Flat Fee:      ${charges['flat_fee']:.2f}")
    print(f"Usage Charges: ${charges['usage_charges']:.2f}")
    print(f"Total:         ${charges['total']:.2f}")
    print()
    print("Breakdown:")
    for item, data in charges['breakdown'].items():
        if data['overage'] > 0:
            print(f"  {item}: {data['used']} used, {data['overage']} overage × ${data['rate']} = ${data['charge']:.2f}")
    
    # =========================================================================
    # INVOICE
    # =========================================================================
    print_header("SAMPLE INVOICE")
    
    # Simulate closing cycle (usage becomes "previous cycle")
    previous_usage = billing_service.close_cycle(company_id)
    
    # Generate invoice for new cycle with previous usage
    invoice = billing_service.generate_invoice(
        company_id=company_id,
        previous_cycle_usage=previous_usage,
        is_founding=True,  # Founding customer discount
    )
    
    print(billing_service.format_invoice(invoice))
    
    # =========================================================================
    # PRICING CALCULATOR
    # =========================================================================
    print_header("PRICING CALCULATOR")
    
    scenarios = [
        {"queries": 500, "documents": 20, "photos": 100, "storage_gb": 10},  # Exactly at limits
        {"queries": 1000, "documents": 50, "photos": 200, "storage_gb": 20},  # Heavy usage
        {"queries": 2000, "documents": 100, "photos": 500, "storage_gb": 50},  # Enterprise usage
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        result = pricing_service.calculate_usage(**scenario)
        
        total = pricing_service.FLAT_FEE_USD + result['total_usd']
        
        print(f"\nScenario {i}:")
        print(f"  Queries: {scenario['queries']}, Docs: {scenario['documents']}, Photos: {scenario['photos']}, Storage: {scenario['storage_gb']}GB")
        print(f"  Flat Fee:      ${pricing_service.FLAT_FEE_USD:.2f}")
        print(f"  Usage:         ${result['total_usd']:.2f}")
        print(f"  Total:         ${total:.2f} (₹{total * 83:,.0f})")
    
    # =========================================================================
    # MARGINS
    # =========================================================================
    print_header("MARGIN VERIFICATION (80%+ Target)")
    
    margins = pricing_service.verify_margins()
    for item, data in margins.items():
        print(f"  {item:12}: Cost {data['cost']:>6} → Price {data['price']:>6} = {data['margin']:>5} {data['ok']}")
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("                    Demo Complete! 🎉")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    asyncio.run(main())

