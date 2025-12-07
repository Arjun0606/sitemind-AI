"""
SiteMind Billing Service
Track usage and generate invoices

BILLING FLOW:
1. Track usage throughout the month
2. At month end, calculate overages
3. Generate invoice: $500 flat + usage from previous cycle
4. Bill in next cycle
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from config import settings
from utils.logger import logger
from services.pricing_service import pricing_service


@dataclass
class CompanyUsage:
    """Track usage for a company (unlimited projects)"""
    company_id: str
    company_name: str
    cycle_start: str
    cycle_end: str
    
    # Usage counts
    queries: int = 0
    documents: int = 0
    photos: int = 0
    storage_gb: float = 0
    
    # Included limits (per company)
    queries_included: int = 1000
    documents_included: int = 50
    photos_included: int = 200
    storage_included_gb: int = 25


class BillingService:
    """
    Track usage and generate invoices
    """
    
    def __init__(self):
        # In-memory usage tracking (use database in production)
        self._usage: Dict[str, CompanyUsage] = {}
        self._invoices: List[Dict] = []
        
        # USD to INR
        self.exchange_rate = 83
    
    # =========================================================================
    # USAGE TRACKING
    # =========================================================================
    
    def get_or_create_usage(self, company_id: str, company_name: str = "Company") -> CompanyUsage:
        """Get or create usage tracker for company"""
        if company_id not in self._usage:
            now = datetime.utcnow()
            self._usage[company_id] = CompanyUsage(
                company_id=company_id,
                company_name=company_name,
                cycle_start=now.strftime("%Y-%m-%d"),
                cycle_end=(now + timedelta(days=30)).strftime("%Y-%m-%d"),
            )
        
        return self._usage[company_id]
    
    def track_query(self, company_id: str, company_name: str = None):
        """Track a query"""
        usage = self.get_or_create_usage(company_id, company_name)
        usage.queries += 1
        logger.debug(f"Query tracked for {company_id}: {usage.queries}")
    
    def track_document(self, company_id: str, company_name: str = None):
        """Track a document"""
        usage = self.get_or_create_usage(company_id, company_name)
        usage.documents += 1
        logger.debug(f"Document tracked for {company_id}: {usage.documents}")
    
    def track_photo(self, company_id: str, company_name: str = None):
        """Track a photo"""
        usage = self.get_or_create_usage(company_id, company_name)
        usage.photos += 1
        logger.debug(f"Photo tracked for {company_id}: {usage.photos}")
    
    def track_storage(self, company_id: str, gb: float, company_name: str = None):
        """Track storage (peak usage)"""
        usage = self.get_or_create_usage(company_id, company_name)
        usage.storage_gb = max(usage.storage_gb, gb)
    
    def get_usage(self, company_id: str) -> Optional[Dict]:
        """Get current usage for company"""
        usage = self._usage.get(company_id)
        if not usage:
            return None
        
        return {
            "company_id": usage.company_id,
            "company_name": usage.company_name,
            "cycle_start": usage.cycle_start,
            "cycle_end": usage.cycle_end,
            "queries": usage.queries,
            "documents": usage.documents,
            "photos": usage.photos,
            "storage_gb": usage.storage_gb,
            "queries_included": usage.queries_included,
            "documents_included": usage.documents_included,
            "photos_included": usage.photos_included,
            "storage_included_gb": usage.storage_included_gb,
        }
    
    # =========================================================================
    # CALCULATE CHARGES
    # =========================================================================
    
    def calculate_charges(self, company_id: str) -> Dict[str, Any]:
        """Calculate usage charges for company"""
        usage = self._usage.get(company_id)
        if not usage:
            return {
                "flat_fee": settings.FLAT_FEE_USD,
                "usage_charges": 0,
                "total": settings.FLAT_FEE_USD,
                "breakdown": {},
            }
        
        # Calculate overages
        queries_overage = max(0, usage.queries - usage.queries_included)
        documents_overage = max(0, usage.documents - usage.documents_included)
        photos_overage = max(0, usage.photos - usage.photos_included)
        storage_overage = max(0, usage.storage_gb - usage.storage_included_gb)
        
        # Calculate charges
        query_charges = queries_overage * settings.QUERY_PRICE_USD
        document_charges = documents_overage * settings.DOCUMENT_PRICE_USD
        photo_charges = photos_overage * settings.PHOTO_PRICE_USD
        storage_charges = storage_overage * settings.STORAGE_PRICE_USD
        
        usage_total = query_charges + document_charges + photo_charges + storage_charges
        
        return {
            "flat_fee": settings.FLAT_FEE_USD,
            "usage_charges": round(usage_total, 2),
            "total": round(settings.FLAT_FEE_USD + usage_total, 2),
            "breakdown": {
                "queries": {
                    "used": usage.queries,
                    "included": usage.queries_included,
                    "overage": queries_overage,
                    "rate": settings.QUERY_PRICE_USD,
                    "charge": round(query_charges, 2),
                },
                "documents": {
                    "used": usage.documents,
                    "included": usage.documents_included,
                    "overage": documents_overage,
                    "rate": settings.DOCUMENT_PRICE_USD,
                    "charge": round(document_charges, 2),
                },
                "photos": {
                    "used": usage.photos,
                    "included": usage.photos_included,
                    "overage": photos_overage,
                    "rate": settings.PHOTO_PRICE_USD,
                    "charge": round(photo_charges, 2),
                },
                "storage_gb": {
                    "used": usage.storage_gb,
                    "included": usage.storage_included_gb,
                    "overage": storage_overage,
                    "rate": settings.STORAGE_PRICE_USD,
                    "charge": round(storage_charges, 2),
                },
            },
        }
    
    # =========================================================================
    # INVOICING
    # =========================================================================
    
    def generate_invoice(
        self,
        company_id: str,
        previous_cycle_usage: Dict = None,
        is_founding: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate invoice for company
        
        - Flat fee for current cycle
        - Usage charges from PREVIOUS cycle
        """
        usage = self._usage.get(company_id)
        company_name = usage.company_name if usage else "Company"
        
        # Flat fee
        flat_fee = settings.FLAT_FEE_USD
        founding_discount = 0
        
        if is_founding:
            founding_discount = flat_fee * 0.25  # 25% founding discount
            flat_fee = flat_fee - founding_discount
        
        # Usage from previous cycle
        usage_charges = 0
        usage_breakdown = {}
        
        if previous_cycle_usage:
            charges = pricing_service.calculate_usage(
                queries=previous_cycle_usage.get("queries", 0),
                documents=previous_cycle_usage.get("documents", 0),
                photos=previous_cycle_usage.get("photos", 0),
                storage_gb=previous_cycle_usage.get("storage_gb", 0),
            )
            usage_charges = charges["total_usd"]
            usage_breakdown = charges["breakdown"]
        
        total_usd = flat_fee + usage_charges
        total_inr = total_usd * self.exchange_rate
        
        invoice = {
            "invoice_id": f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company_id": company_id,
            "company_name": company_name,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "due_date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
            
            "flat_fee_usd": settings.FLAT_FEE_USD,
            "founding_discount_usd": founding_discount,
            "net_flat_fee_usd": flat_fee,
            
            "usage_charges_usd": round(usage_charges, 2),
            "usage_breakdown": usage_breakdown,
            
            "total_usd": round(total_usd, 2),
            "total_inr": round(total_inr, 2),
            
            "status": "pending",
        }
        
        self._invoices.append(invoice)
        
        return invoice
    
    def format_invoice(self, invoice: Dict) -> str:
        """Format invoice for display"""
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    SITEMIND INVOICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Invoice:  {invoice['invoice_id']}
Company:  {invoice['company_name']}
Date:     {invoice['date']}
Due:      {invoice['due_date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUBSCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SiteMind Enterprise                        ${invoice['flat_fee_usd']:.2f}"""

        if invoice.get('founding_discount_usd', 0) > 0:
            msg += f"""
Founding Customer Discount (-25%)         -${invoice['founding_discount_usd']:.2f}
                                           ─────────
Subscription Total                         ${invoice['net_flat_fee_usd']:.2f}"""

        if invoice.get('usage_charges_usd', 0) > 0:
            msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE (from previous billing cycle)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for item, data in invoice.get('usage_breakdown', {}).items():
                if data.get('overage', 0) > 0:
                    label = item.replace('_', ' ').title()
                    msg += f"""
{label:12}  {data['used']:>5} used ({data['included']} included)
              {data['overage']:>5} extra × ${data['rate']:.2f}        ${data['charge']:>8.2f}"""
            
            msg += f"""

                                           ─────────
Usage Total                                ${invoice['usage_charges_usd']:>8.2f}"""

        msg += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL DUE                                  ${invoice['total_usd']:>8.2f}
                                           ₹{invoice['total_inr']:>,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return msg
    
    # =========================================================================
    # RESET CYCLE
    # =========================================================================
    
    def close_cycle(self, company_id: str) -> Dict:
        """Close current billing cycle and return usage"""
        usage = self.get_usage(company_id)
        
        if company_id in self._usage:
            # Store for next cycle billing
            previous_usage = self._usage[company_id]
            
            # Reset for new cycle
            now = datetime.utcnow()
            self._usage[company_id] = CompanyUsage(
                company_id=company_id,
                company_name=previous_usage.company_name,
                cycle_start=now.strftime("%Y-%m-%d"),
                cycle_end=(now + timedelta(days=30)).strftime("%Y-%m-%d"),
            )
        
        return usage
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def get_usage_summary(self, company_id: str) -> str:
        """Get formatted usage summary"""
        usage = self.get_usage(company_id)
        if not usage:
            return "No usage data"
        
        charges = self.calculate_charges(company_id)
        
        return f"""📊 *Usage Summary*

*Cycle:* {usage['cycle_start']} to {usage['cycle_end']}

*Queries:* {usage['queries']} / {usage['queries_included']} included
*Documents:* {usage['documents']} / {usage['documents_included']} included
*Photos:* {usage['photos']} / {usage['photos_included']} included
*Storage:* {usage['storage_gb']:.2f} GB / {usage['storage_included_gb']} GB included

*Current Charges:*
Flat Fee: ${charges['flat_fee']:.2f}
Usage: ${charges['usage_charges']:.2f}
*Total: ${charges['total']:.2f}*"""


# Singleton instance
billing_service = BillingService()

