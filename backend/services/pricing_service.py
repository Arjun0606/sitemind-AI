"""
SiteMind Pricing Service
Cursor-style: Flat fee + Usage with 80%+ margins

PRICING MODEL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FLAT FEE (base subscription):
- Per seat: $50/user/month
- Per project: $500/month (active)

USAGE (billed next cycle, like Cursor):
- Queries: $0.15 each (after included)
- Documents: $2.50 each (after included)
- Photos: $0.50 each (after included)
- Storage: $1.00/GB (after included)

MARGIN CALCULATION:
Our cost → Price (margin)
$0.03/query → $0.15 (80%)
$0.50/document → $2.50 (80%)
$0.10/photo → $0.50 (80%)
$0.02/GB → $1.00 (98%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BILLING:
- Flat fee: Charged at start of cycle
- Usage: Tracked during cycle, charged NEXT cycle
- Just like Cursor Pro works

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class ProjectStage(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    FINISHING = "finishing"
    HANDOVER = "handover"
    ARCHIVED = "archived"


@dataclass
class UsageRecord:
    """Track usage for a billing cycle"""
    project_id: str
    cycle_start: str
    cycle_end: str
    queries: int = 0
    documents: int = 0
    photos: int = 0
    storage_gb: float = 0
    
    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "cycle": f"{self.cycle_start} to {self.cycle_end}",
            "queries": self.queries,
            "documents": self.documents,
            "photos": self.photos,
            "storage_gb": self.storage_gb,
        }


class PricingService:
    """
    Cursor-style pricing: Flat fee + Usage
    """
    
    def __init__(self):
        # =================================================================
        # FLAT FEES (charged at start of cycle)
        # =================================================================
        
        # Per seat
        self.PER_SEAT_USD = 50
        self.INCLUDED_SEATS = 3  # First 3 free
        
        # Per project (by stage)
        self.PROJECT_FEES = {
            ProjectStage.PLANNING: 250,    # Less activity
            ProjectStage.ACTIVE: 500,      # Full price
            ProjectStage.FINISHING: 500,   # Still active
            ProjectStage.HANDOVER: 300,    # Winding down
            ProjectStage.ARCHIVED: 100,    # Minimal
        }
        
        # =================================================================
        # INCLUDED USAGE (per project per month)
        # =================================================================
        
        self.INCLUDED = {
            "queries": 300,      # 300 queries/project/month
            "documents": 10,     # 10 documents/project/month
            "photos": 50,        # 50 photos/project/month
            "storage_gb": 2,     # 2 GB/project
        }
        
        # =================================================================
        # USAGE PRICING (charged NEXT cycle, 80%+ margin)
        # =================================================================
        
        # Our costs
        self.COSTS = {
            "query": 0.03,       # Gemini API
            "document": 0.50,    # Gemini Vision + processing
            "photo": 0.10,       # Gemini Vision
            "storage_gb": 0.02,  # Supabase storage
        }
        
        # Our prices (80%+ margin)
        self.USAGE_PRICES = {
            "query": 0.15,       # $0.15/query (80% margin)
            "document": 2.50,    # $2.50/doc (80% margin)
            "photo": 0.50,       # $0.50/photo (80% margin)
            "storage_gb": 1.00,  # $1.00/GB (98% margin)
        }
        
        # =================================================================
        # DISCOUNTS
        # =================================================================
        
        # Volume discounts (by monthly flat fee)
        self.VOLUME_DISCOUNTS = {
            2000: 0.05,    # $2K+: 5% off flat fee
            5000: 0.10,    # $5K+: 10% off
            10000: 0.15,   # $10K+: 15% off
            25000: 0.20,   # $25K+: 20% off
        }
        
        # Annual discount
        self.ANNUAL_DISCOUNT = 0.17  # ~2 months free
        
        # =================================================================
        # PILOT
        # =================================================================
        
        self.PILOT_MONTHS = 3
        self.FOUNDING_DISCOUNT = 0.25  # 25% off forever
        
        # =================================================================
        # TRACKING
        # =================================================================
        
        self._usage: Dict[str, UsageRecord] = {}  # project_id -> current cycle usage
        
        # USD to INR
        self.USD_TO_INR = 83
    
    # =========================================================================
    # MARGIN VERIFICATION
    # =========================================================================
    
    def verify_margins(self) -> Dict[str, Any]:
        """Verify all usage prices maintain 80%+ margin"""
        margins = {}
        for item in ["query", "document", "photo", "storage_gb"]:
            cost = self.COSTS[item]
            price = self.USAGE_PRICES[item]
            margin = ((price - cost) / price) * 100
            margins[item] = {
                "cost": cost,
                "price": price,
                "margin_percent": round(margin, 1),
                "status": "✅" if margin >= 80 else "❌",
            }
        return margins
    
    # =========================================================================
    # FLAT FEE CALCULATION
    # =========================================================================
    
    def calculate_flat_fee(
        self,
        unique_users: int,
        projects: List[Dict],
        is_pilot: bool = False,
        is_founding: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculate flat monthly fee (charged at start of cycle)
        
        Args:
            unique_users: Total unique users (by phone)
            projects: List of {name, stage}
        """
        if is_pilot:
            return {
                "flat_fee_usd": 0,
                "status": "pilot",
                "note": f"FREE for {self.PILOT_MONTHS} months",
            }
        
        # Seat fees
        billable_seats = max(0, unique_users - self.INCLUDED_SEATS)
        seats_fee = billable_seats * self.PER_SEAT_USD
        
        # Project fees
        projects_detail = []
        projects_fee = 0
        
        for proj in projects:
            stage = ProjectStage(proj.get("stage", "active"))
            fee = self.PROJECT_FEES[stage]
            
            projects_detail.append({
                "name": proj.get("name", "Project"),
                "stage": stage.value,
                "fee_usd": fee,
            })
            projects_fee += fee
        
        subtotal = seats_fee + projects_fee
        
        # Volume discount on flat fees
        discount_percent = 0
        for threshold, discount in sorted(self.VOLUME_DISCOUNTS.items()):
            if subtotal >= threshold:
                discount_percent = discount * 100
        
        volume_discount = subtotal * (discount_percent / 100)
        
        # Founding discount
        founding_discount = 0
        if is_founding:
            founding_discount = (subtotal - volume_discount) * self.FOUNDING_DISCOUNT
        
        flat_fee = subtotal - volume_discount - founding_discount
        
        return {
            "seats": {
                "total": unique_users,
                "included": self.INCLUDED_SEATS,
                "billable": billable_seats,
                "rate": self.PER_SEAT_USD,
                "fee_usd": seats_fee,
            },
            "projects": projects_detail,
            "projects_fee_usd": projects_fee,
            "subtotal_usd": subtotal,
            "discounts": {
                "volume_percent": discount_percent,
                "volume_usd": volume_discount,
                "founding_percent": self.FOUNDING_DISCOUNT * 100 if is_founding else 0,
                "founding_usd": founding_discount,
            },
            "flat_fee_usd": flat_fee,
            "flat_fee_inr": flat_fee * self.USD_TO_INR,
        }
    
    # =========================================================================
    # USAGE TRACKING (during cycle)
    # =========================================================================
    
    def track_usage(
        self,
        project_id: str,
        queries: int = 0,
        documents: int = 0,
        photos: int = 0,
        storage_gb: float = 0,
    ):
        """Track usage during the billing cycle"""
        if project_id not in self._usage:
            now = datetime.utcnow()
            self._usage[project_id] = UsageRecord(
                project_id=project_id,
                cycle_start=now.isoformat(),
                cycle_end=(now + timedelta(days=30)).isoformat(),
            )
        
        record = self._usage[project_id]
        record.queries += queries
        record.documents += documents
        record.photos += photos
        record.storage_gb = max(record.storage_gb, storage_gb)  # Peak storage
    
    def get_current_usage(self, project_id: str) -> Dict[str, Any]:
        """Get current cycle usage for a project"""
        record = self._usage.get(project_id)
        if not record:
            return {"queries": 0, "documents": 0, "photos": 0, "storage_gb": 0}
        return record.to_dict()
    
    # =========================================================================
    # USAGE BILLING (charged next cycle)
    # =========================================================================
    
    def calculate_usage_charges(
        self,
        project_id: str,
        queries: int,
        documents: int,
        photos: int,
        storage_gb: float,
    ) -> Dict[str, Any]:
        """
        Calculate usage charges (billed NEXT cycle)
        """
        # Calculate overages
        query_overage = max(0, queries - self.INCLUDED["queries"])
        doc_overage = max(0, documents - self.INCLUDED["documents"])
        photo_overage = max(0, photos - self.INCLUDED["photos"])
        storage_overage = max(0, storage_gb - self.INCLUDED["storage_gb"])
        
        # Calculate charges
        query_charge = query_overage * self.USAGE_PRICES["query"]
        doc_charge = doc_overage * self.USAGE_PRICES["document"]
        photo_charge = photo_overage * self.USAGE_PRICES["photo"]
        storage_charge = storage_overage * self.USAGE_PRICES["storage_gb"]
        
        total_usage = query_charge + doc_charge + photo_charge + storage_charge
        
        # Calculate our costs (for margin verification)
        our_cost = (
            queries * self.COSTS["query"] +
            documents * self.COSTS["document"] +
            photos * self.COSTS["photo"] +
            storage_gb * self.COSTS["storage_gb"]
        )
        
        margin = ((total_usage - our_cost) / total_usage * 100) if total_usage > 0 else 100
        
        return {
            "usage": {
                "queries": {
                    "used": queries,
                    "included": self.INCLUDED["queries"],
                    "overage": query_overage,
                    "rate": self.USAGE_PRICES["query"],
                    "charge_usd": query_charge,
                },
                "documents": {
                    "used": documents,
                    "included": self.INCLUDED["documents"],
                    "overage": doc_overage,
                    "rate": self.USAGE_PRICES["document"],
                    "charge_usd": doc_charge,
                },
                "photos": {
                    "used": photos,
                    "included": self.INCLUDED["photos"],
                    "overage": photo_overage,
                    "rate": self.USAGE_PRICES["photo"],
                    "charge_usd": photo_charge,
                },
                "storage_gb": {
                    "used": storage_gb,
                    "included": self.INCLUDED["storage_gb"],
                    "overage": storage_overage,
                    "rate": self.USAGE_PRICES["storage_gb"],
                    "charge_usd": storage_charge,
                },
            },
            "total_usage_usd": total_usage,
            "total_usage_inr": total_usage * self.USD_TO_INR,
            "our_cost_usd": round(our_cost, 2),
            "margin_percent": round(margin, 1),
            "billing_note": "Usage charges billed in next billing cycle",
        }
    
    # =========================================================================
    # FULL INVOICE
    # =========================================================================
    
    def generate_invoice(
        self,
        company_name: str,
        unique_users: int,
        projects: List[Dict],
        previous_usage: Dict[str, Dict] = None,  # Last cycle's usage per project
        is_founding: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate full invoice
        
        Components:
        1. Flat fee for THIS cycle
        2. Usage charges from PREVIOUS cycle
        """
        # This cycle's flat fee
        flat = self.calculate_flat_fee(unique_users, projects, is_founding=is_founding)
        
        # Previous cycle's usage charges
        usage_charges = []
        total_usage = 0
        
        if previous_usage:
            for project_id, usage in previous_usage.items():
                project_name = next(
                    (p.get("name", project_id) for p in projects if p.get("id") == project_id),
                    project_id
                )
                
                charges = self.calculate_usage_charges(
                    project_id=project_id,
                    queries=usage.get("queries", 0),
                    documents=usage.get("documents", 0),
                    photos=usage.get("photos", 0),
                    storage_gb=usage.get("storage_gb", 0),
                )
                
                if charges["total_usage_usd"] > 0:
                    usage_charges.append({
                        "project": project_name,
                        **charges,
                    })
                    total_usage += charges["total_usage_usd"]
        
        # Total
        total = flat["flat_fee_usd"] + total_usage
        
        return {
            "invoice_id": f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "company": company_name,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "due_date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
            
            "flat_fee": flat,
            "usage_charges": usage_charges,
            "total_usage_usd": total_usage,
            
            "total_usd": total,
            "total_inr": total * self.USD_TO_INR,
            
            "breakdown": {
                "flat_fee": flat["flat_fee_usd"],
                "usage": total_usage,
                "total": total,
            },
        }
    
    # =========================================================================
    # PRICING TABLE
    # =========================================================================
    
    def get_pricing_table(self) -> str:
        """Cursor-style pricing table"""
        return f"""
**SiteMind Pricing**
Flat fee + Usage (like Cursor)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLAT FEE (charged at start of cycle)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Per Seat**
• First {self.INCLUDED_SEATS} users: Included
• Additional: ${self.PER_SEAT_USD}/user/month

**Per Project**
• Active: ${self.PROJECT_FEES[ProjectStage.ACTIVE]}/month
• Planning: ${self.PROJECT_FEES[ProjectStage.PLANNING]}/month
• Handover: ${self.PROJECT_FEES[ProjectStage.HANDOVER]}/month
• Archived: ${self.PROJECT_FEES[ProjectStage.ARCHIVED]}/month

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INCLUDED PER PROJECT (per month)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• {self.INCLUDED['queries']} queries
• {self.INCLUDED['documents']} documents
• {self.INCLUDED['photos']} photos
• {self.INCLUDED['storage_gb']} GB storage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE (billed next cycle)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Additional queries: ${self.USAGE_PRICES['query']}/query
• Additional documents: ${self.USAGE_PRICES['document']}/document
• Additional photos: ${self.USAGE_PRICES['photo']}/photo
• Additional storage: ${self.USAGE_PRICES['storage_gb']}/GB

_All usage prices maintain 80%+ profit margin_

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VOLUME DISCOUNTS (on flat fee)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• $2,000+/month: 5% off
• $5,000+/month: 10% off
• $10,000+/month: 15% off
• $25,000+/month: 20% off

Annual payment: {int(self.ANNUAL_DISCOUNT * 100)}% off
"""
    
    # =========================================================================
    # EXAMPLES
    # =========================================================================
    
    def get_example_invoice(self, size: str = "medium") -> Dict[str, Any]:
        """Generate example invoice"""
        examples = {
            "small": {
                "users": 10,
                "projects": [{"name": "Sunrise Apartments", "stage": "active", "id": "p1"}],
                "usage": {"p1": {"queries": 400, "documents": 15, "photos": 60, "storage_gb": 3}},
            },
            "medium": {
                "users": 25,
                "projects": [
                    {"name": "Green Valley", "stage": "active", "id": "p1"},
                    {"name": "City Heights", "stage": "active", "id": "p2"},
                    {"name": "Lake View", "stage": "planning", "id": "p3"},
                ],
                "usage": {
                    "p1": {"queries": 500, "documents": 25, "photos": 100, "storage_gb": 5},
                    "p2": {"queries": 400, "documents": 15, "photos": 80, "storage_gb": 4},
                    "p3": {"queries": 100, "documents": 5, "photos": 20, "storage_gb": 1},
                },
            },
            "large": {
                "users": 60,
                "projects": [
                    {"name": "Township Phase 1", "stage": "active", "id": "p1"},
                    {"name": "Township Phase 2", "stage": "active", "id": "p2"},
                    {"name": "Commercial Hub", "stage": "active", "id": "p3"},
                    {"name": "Luxury Villas", "stage": "finishing", "id": "p4"},
                    {"name": "Old Project", "stage": "archived", "id": "p5"},
                ],
                "usage": {
                    "p1": {"queries": 1200, "documents": 50, "photos": 200, "storage_gb": 15},
                    "p2": {"queries": 800, "documents": 30, "photos": 150, "storage_gb": 10},
                    "p3": {"queries": 600, "documents": 25, "photos": 100, "storage_gb": 8},
                    "p4": {"queries": 300, "documents": 10, "photos": 50, "storage_gb": 5},
                    "p5": {"queries": 50, "documents": 2, "photos": 10, "storage_gb": 3},
                },
            },
        }
        
        ex = examples.get(size, examples["medium"])
        
        return self.generate_invoice(
            company_name=f"Example {size.title()} Developer",
            unique_users=ex["users"],
            projects=ex["projects"],
            previous_usage=ex["usage"],
        )
    
    # =========================================================================
    # PILOT
    # =========================================================================
    
    def get_pilot_info(self) -> Dict[str, Any]:
        """Pilot program info"""
        return {
            "name": "Founder's Pilot",
            "duration": f"{self.PILOT_MONTHS} months",
            "price": "FREE (flat fee waived)",
            "usage": "Pay only for usage over included limits",
            "after_pilot": f"{int(self.FOUNDING_DISCOUNT * 100)}% discount forever",
        }


# Singleton instance
pricing_service = PricingService()
