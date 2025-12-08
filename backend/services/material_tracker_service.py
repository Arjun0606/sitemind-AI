"""
SiteMind Material Tracker Service
Customer-specific material rates and tracking

KEY INSIGHT: 
Costs are INPUT by customer because:
- Special vendor relationships
- Bulk/mass discounts  
- Regional variations
- Time-based fluctuations

We track:
1. Company-specific material rates
2. Vendor-specific pricing
3. Purchase history
4. Consumption tracking
5. Variance analysis (ordered vs used)

This catches leakages by comparing:
- What was ordered vs what was needed
- What was delivered vs what was ordered
- What was used vs what was delivered
- Vendor A price vs Vendor B price
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from utils.logger import logger


class MaterialCategory(Enum):
    """Material categories"""
    CEMENT = "cement"
    STEEL = "steel"
    SAND = "sand"
    AGGREGATE = "aggregate"
    BRICKS = "bricks"
    BLOCKS = "blocks"
    TILES = "tiles"
    PAINT = "paint"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HARDWARE = "hardware"
    OTHER = "other"


@dataclass
class MaterialRate:
    """Company-specific material rate"""
    material: str
    category: MaterialCategory
    unit: str
    rate: float  # Customer's rate
    vendor: str = ""
    last_updated: datetime = None
    notes: str = ""
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.utcnow()


@dataclass
class MaterialOrder:
    """Tracked material order"""
    id: str
    company_id: str
    project_id: str
    
    # What
    material: str
    category: MaterialCategory
    quantity: float
    unit: str
    
    # Vendor
    vendor: str
    po_number: str = ""
    
    # Pricing (from customer's rates)
    rate_per_unit: float = 0.0
    total_amount: float = 0.0
    
    # Calculation check
    calculated_need: float = 0.0  # What we calculated they need
    variance_pct: float = 0.0     # % difference from calculated
    variance_flag: str = ""       # ok, over_order, under_order
    
    # Status
    ordered_at: datetime = None
    expected_delivery: datetime = None
    delivered_at: datetime = None
    delivered_quantity: float = 0.0
    
    # Issues
    short_delivery: float = 0.0
    quality_issues: List[str] = field(default_factory=list)
    
    # Payment
    invoice_amount: float = 0.0
    paid: bool = False
    
    status: str = "pending"  # pending, ordered, in_transit, delivered, verified


@dataclass
class MaterialConsumption:
    """Track actual material consumption"""
    id: str
    company_id: str
    project_id: str
    
    material: str
    date: str
    
    # Quantities
    opening_stock: float = 0.0
    received: float = 0.0
    consumed: float = 0.0
    closing_stock: float = 0.0
    wastage: float = 0.0
    
    # Work done (for consumption rate calculation)
    work_description: str = ""
    work_quantity: float = 0.0
    work_unit: str = ""
    
    # Consumption rate
    consumption_rate: float = 0.0  # material per work unit
    standard_rate: float = 0.0     # what it should be
    variance_pct: float = 0.0


class MaterialTrackerService:
    """
    Track materials with CUSTOMER-SPECIFIC rates
    
    This is how we catch leakages:
    1. Customer inputs their rates (from their vendors)
    2. We calculate what they SHOULD need
    3. We track what they ORDER
    4. We track what they RECEIVE
    5. We track what they USE
    6. We flag any variances
    """
    
    def __init__(self):
        # Company-specific rates: company_id -> {material: MaterialRate}
        self._rates: Dict[str, Dict[str, MaterialRate]] = {}
        
        # Orders: company_id -> List[MaterialOrder]
        self._orders: Dict[str, List[MaterialOrder]] = {}
        
        # Consumption: company_id -> List[MaterialConsumption]
        self._consumption: Dict[str, List[MaterialConsumption]] = {}
        
        self._counter = 0
        
        # CALCULATION RATES (these are FIXED - physics doesn't change!)
        # Only the PRICES are customer-specific
        self.CALCULATION_RATES = {
            "cement": {
                "unit": "bags",  # 50 kg
                "rates": {
                    "per_cum_concrete_m20": 8.5,
                    "per_cum_concrete_m25": 9.5,
                    "per_cum_concrete_m30": 10.5,
                    "per_cum_concrete_m35": 11.5,
                    "per_cum_concrete_m40": 12.5,
                    "per_sqft_plaster_12mm": 0.22,
                    "per_sqft_plaster_20mm": 0.35,
                    "per_sqm_flooring": 0.5,
                    "per_cum_brickwork": 1.25,
                },
                "wastage": 0.05,
            },
            "steel": {
                "unit": "kg",
                "rates": {
                    "per_cum_slab": 78,
                    "per_cum_beam": 120,
                    "per_cum_column": 180,
                    "per_cum_foundation": 90,
                    "per_cum_staircase": 150,
                    "per_cum_retaining_wall": 100,
                },
                "wastage": 0.03,
            },
            "sand": {
                "unit": "cum",
                "rates": {
                    "per_cum_concrete": 0.45,
                    "per_sqft_plaster_12mm": 0.018,
                    "per_sqft_plaster_20mm": 0.025,
                    "per_sqm_flooring": 0.04,
                    "per_cum_brickwork": 0.3,
                },
                "wastage": 0.10,
            },
            "aggregate": {
                "unit": "cum",
                "rates": {
                    "per_cum_concrete_20mm": 0.9,
                    "per_cum_concrete_12mm": 0.45,
                },
                "wastage": 0.05,
            },
            "bricks": {
                "unit": "nos",
                "rates": {
                    "per_sqft_wall_9inch": 14,
                    "per_sqft_wall_4inch": 7,
                    "per_cum_brickwork": 500,
                },
                "wastage": 0.05,
            },
            "blocks": {
                "unit": "nos",
                "rates": {
                    "per_sqft_wall_200mm": 1.3,
                    "per_sqft_wall_150mm": 1.3,
                    "per_sqft_wall_100mm": 1.3,
                    "per_cum_blockwork": 15,
                },
                "wastage": 0.03,
            },
            "tiles": {
                "unit": "sqft",
                "rates": {
                    "per_sqft_floor": 1.1,
                    "per_sqft_wall": 1.15,
                },
                "wastage": 0.10,
            },
            "paint": {
                "unit": "liters",
                "rates": {
                    "per_sqft_wall_2coat": 0.018,
                    "per_sqft_ceiling_2coat": 0.015,
                    "per_sqft_exterior_2coat": 0.022,
                },
                "wastage": 0.05,
            },
        }
    
    # =========================================================================
    # RATE MANAGEMENT (Customer inputs their rates)
    # =========================================================================
    
    def set_material_rate(
        self,
        company_id: str,
        material: str,
        rate: float,
        unit: str,
        vendor: str = "",
        notes: str = "",
    ) -> MaterialRate:
        """
        Set company-specific material rate
        
        Example:
        set_material_rate("comp1", "cement", 350, "bag", "UltraTech")
        set_material_rate("comp1", "steel", 62, "kg", "TATA Steel", "Bulk rate")
        """
        
        if company_id not in self._rates:
            self._rates[company_id] = {}
        
        # Determine category
        category = MaterialCategory.OTHER
        for cat in MaterialCategory:
            if cat.value in material.lower():
                category = cat
                break
        
        rate_obj = MaterialRate(
            material=material.lower(),
            category=category,
            unit=unit,
            rate=rate,
            vendor=vendor,
            notes=notes,
        )
        
        self._rates[company_id][material.lower()] = rate_obj
        
        logger.info(f"💰 Rate set: {material} = ₹{rate}/{unit} for {company_id}")
        
        return rate_obj
    
    def get_material_rate(self, company_id: str, material: str) -> Optional[MaterialRate]:
        """Get company's rate for a material"""
        return self._rates.get(company_id, {}).get(material.lower())
    
    def get_all_rates(self, company_id: str) -> Dict[str, MaterialRate]:
        """Get all rates for a company"""
        return self._rates.get(company_id, {})
    
    def import_rates_bulk(
        self,
        company_id: str,
        rates: List[Dict],
    ) -> int:
        """
        Bulk import rates from customer
        
        rates = [
            {"material": "cement", "rate": 350, "unit": "bag", "vendor": "UltraTech"},
            {"material": "steel", "rate": 62, "unit": "kg", "vendor": "TATA"},
            ...
        ]
        """
        count = 0
        for r in rates:
            self.set_material_rate(
                company_id=company_id,
                material=r["material"],
                rate=r["rate"],
                unit=r.get("unit", ""),
                vendor=r.get("vendor", ""),
                notes=r.get("notes", ""),
            )
            count += 1
        
        logger.info(f"📦 Imported {count} rates for {company_id}")
        return count
    
    # =========================================================================
    # MATERIAL CALCULATION (Quantities - physics based)
    # =========================================================================
    
    def calculate_material(
        self,
        material: str,
        work_type: str,
        quantity: float,
        unit: str = "",
        company_id: str = None,
    ) -> Dict[str, Any]:
        """
        Calculate required material
        
        - Quantity calculation is FIXED (based on physics/standards)
        - Cost estimate uses CUSTOMER'S rate if available
        
        Example:
        calculate_material("cement", "concrete_m25", 10, "cum", "comp1")
        """
        
        material_lower = material.lower()
        
        # Find material in calculation database
        calc_data = None
        for key, data in self.CALCULATION_RATES.items():
            if key in material_lower:
                calc_data = data
                material_lower = key
                break
        
        if not calc_data:
            return {
                "success": False,
                "error": f"Material '{material}' not in calculation database",
                "available": list(self.CALCULATION_RATES.keys()),
            }
        
        # Find appropriate rate for work type
        rate_key = None
        work_type_lower = work_type.lower().replace(" ", "_")
        
        for key in calc_data["rates"]:
            if work_type_lower in key:
                rate_key = key
                break
        
        if not rate_key:
            # Try partial match
            for key in calc_data["rates"]:
                if any(word in key for word in work_type_lower.split("_")):
                    rate_key = key
                    break
        
        if not rate_key:
            rate_key = list(calc_data["rates"].keys())[0]
        
        rate = calc_data["rates"][rate_key]
        wastage = calc_data["wastage"]
        material_unit = calc_data["unit"]
        
        # Calculate quantity
        base_qty = quantity * rate
        wastage_qty = base_qty * wastage
        total_qty = base_qty + wastage_qty
        
        result = {
            "success": True,
            "material": material_lower,
            "work_type": work_type,
            "input": {
                "quantity": quantity,
                "unit": unit or "units",
            },
            "calculation": {
                "rate_used": rate_key,
                "rate": rate,
                "base_quantity": round(base_qty, 2),
                "wastage_pct": wastage * 100,
                "wastage_quantity": round(wastage_qty, 2),
                "total_quantity": round(total_qty, 2),
                "unit": material_unit,
            },
            "formula": f"{quantity} × {rate} = {base_qty:.2f} + {wastage*100}% wastage = {total_qty:.2f} {material_unit}",
        }
        
        # Add cost estimate if company has rate
        if company_id:
            company_rate = self.get_material_rate(company_id, material_lower)
            if company_rate:
                estimated_cost = total_qty * company_rate.rate
                result["cost_estimate"] = {
                    "rate": company_rate.rate,
                    "unit": company_rate.unit,
                    "vendor": company_rate.vendor,
                    "total": round(estimated_cost, 2),
                    "last_updated": company_rate.last_updated.isoformat() if company_rate.last_updated else None,
                }
            else:
                result["cost_estimate"] = {
                    "message": "No rate set for this material. Use 'set rate' command to add your vendor prices.",
                }
        
        return result
    
    # =========================================================================
    # ORDER TRACKING
    # =========================================================================
    
    def create_order(
        self,
        company_id: str,
        project_id: str,
        material: str,
        quantity: float,
        unit: str,
        vendor: str,
        po_number: str = "",
        expected_delivery: datetime = None,
        calculated_need: float = 0,
    ) -> MaterialOrder:
        """Create a material order"""
        
        self._counter += 1
        order_id = f"MO-{datetime.utcnow().strftime('%y%m%d')}-{self._counter:04d}"
        
        # Get rate if available
        rate = 0.0
        company_rate = self.get_material_rate(company_id, material)
        if company_rate:
            rate = company_rate.rate
        
        # Calculate variance if we know what they need
        variance_pct = 0.0
        variance_flag = "ok"
        if calculated_need > 0:
            variance_pct = ((quantity - calculated_need) / calculated_need) * 100
            if variance_pct > 20:
                variance_flag = "over_order"
            elif variance_pct < -10:
                variance_flag = "under_order"
        
        order = MaterialOrder(
            id=order_id,
            company_id=company_id,
            project_id=project_id,
            material=material.lower(),
            category=self._get_category(material),
            quantity=quantity,
            unit=unit,
            vendor=vendor,
            po_number=po_number,
            rate_per_unit=rate,
            total_amount=quantity * rate,
            calculated_need=calculated_need,
            variance_pct=variance_pct,
            variance_flag=variance_flag,
            ordered_at=datetime.utcnow(),
            expected_delivery=expected_delivery,
        )
        
        if company_id not in self._orders:
            self._orders[company_id] = []
        self._orders[company_id].append(order)
        
        logger.info(f"📦 Order created: {order_id} - {quantity} {unit} {material}")
        
        # Alert if over-ordering
        if variance_flag == "over_order":
            logger.warning(f"⚠️ OVER-ORDER: {material} ordered {variance_pct:.1f}% more than calculated need")
        
        return order
    
    def record_delivery(
        self,
        order_id: str,
        company_id: str,
        delivered_quantity: float,
        quality_issues: List[str] = None,
    ) -> Optional[MaterialOrder]:
        """Record material delivery"""
        
        orders = self._orders.get(company_id, [])
        for order in orders:
            if order.id == order_id:
                order.delivered_at = datetime.utcnow()
                order.delivered_quantity = delivered_quantity
                order.short_delivery = order.quantity - delivered_quantity
                order.quality_issues = quality_issues or []
                order.status = "delivered"
                
                if order.short_delivery > 0:
                    logger.warning(f"⚠️ SHORT DELIVERY: {order.material} - {order.short_delivery} {order.unit} less than ordered")
                
                if quality_issues:
                    logger.warning(f"⚠️ QUALITY ISSUES: {order.material} - {quality_issues}")
                
                return order
        
        return None
    
    def _get_category(self, material: str) -> MaterialCategory:
        """Get category for material"""
        material_lower = material.lower()
        for cat in MaterialCategory:
            if cat.value in material_lower:
                return cat
        return MaterialCategory.OTHER
    
    # =========================================================================
    # CONSUMPTION TRACKING
    # =========================================================================
    
    def record_consumption(
        self,
        company_id: str,
        project_id: str,
        material: str,
        consumed: float,
        work_description: str,
        work_quantity: float,
        work_unit: str,
        opening_stock: float = 0,
        received: float = 0,
        wastage: float = 0,
    ) -> MaterialConsumption:
        """
        Record daily/periodic material consumption
        
        This helps track:
        - Actual consumption vs standard rates
        - Wastage
        - Stock levels
        """
        
        self._counter += 1
        cons_id = f"MC-{datetime.utcnow().strftime('%y%m%d')}-{self._counter:04d}"
        
        closing_stock = opening_stock + received - consumed - wastage
        
        # Calculate consumption rate
        consumption_rate = 0
        if work_quantity > 0:
            consumption_rate = consumed / work_quantity
        
        # Get standard rate for comparison
        standard_rate = self._get_standard_rate(material, work_description)
        
        # Calculate variance
        variance_pct = 0
        if standard_rate > 0:
            variance_pct = ((consumption_rate - standard_rate) / standard_rate) * 100
        
        record = MaterialConsumption(
            id=cons_id,
            company_id=company_id,
            project_id=project_id,
            material=material.lower(),
            date=datetime.utcnow().strftime("%Y-%m-%d"),
            opening_stock=opening_stock,
            received=received,
            consumed=consumed,
            closing_stock=closing_stock,
            wastage=wastage,
            work_description=work_description,
            work_quantity=work_quantity,
            work_unit=work_unit,
            consumption_rate=consumption_rate,
            standard_rate=standard_rate,
            variance_pct=variance_pct,
        )
        
        if company_id not in self._consumption:
            self._consumption[company_id] = []
        self._consumption[company_id].append(record)
        
        # Alert if high variance
        if variance_pct > 15:
            logger.warning(f"⚠️ HIGH CONSUMPTION: {material} - {variance_pct:.1f}% above standard rate")
        
        return record
    
    def _get_standard_rate(self, material: str, work_type: str) -> float:
        """Get standard consumption rate"""
        material_lower = material.lower()
        work_lower = work_type.lower().replace(" ", "_")
        
        for mat_key, data in self.CALCULATION_RATES.items():
            if mat_key in material_lower:
                for rate_key, rate in data["rates"].items():
                    if any(word in rate_key for word in work_lower.split("_")):
                        return rate
        return 0
    
    # =========================================================================
    # ANALYTICS & REPORTING
    # =========================================================================
    
    def get_material_summary(
        self,
        company_id: str,
        project_id: str = None,
    ) -> Dict[str, Any]:
        """Get material summary with leakage indicators"""
        
        orders = self._orders.get(company_id, [])
        if project_id:
            orders = [o for o in orders if o.project_id == project_id]
        
        summary = {
            "total_orders": len(orders),
            "total_value": sum(o.total_amount for o in orders),
            "pending_delivery": len([o for o in orders if o.status == "pending"]),
            "delivered": len([o for o in orders if o.status == "delivered"]),
            
            # Leakage indicators
            "over_orders": len([o for o in orders if o.variance_flag == "over_order"]),
            "over_order_value": sum(
                (o.quantity - o.calculated_need) * o.rate_per_unit 
                for o in orders if o.variance_flag == "over_order" and o.calculated_need > 0
            ),
            "short_deliveries": len([o for o in orders if o.short_delivery > 0]),
            "quality_issues": len([o for o in orders if o.quality_issues]),
            
            # By material
            "by_material": {},
        }
        
        for order in orders:
            mat = order.material
            if mat not in summary["by_material"]:
                summary["by_material"][mat] = {
                    "orders": 0,
                    "quantity": 0,
                    "value": 0,
                    "over_orders": 0,
                }
            summary["by_material"][mat]["orders"] += 1
            summary["by_material"][mat]["quantity"] += order.quantity
            summary["by_material"][mat]["value"] += order.total_amount
            if order.variance_flag == "over_order":
                summary["by_material"][mat]["over_orders"] += 1
        
        return summary
    
    def format_summary_whatsapp(self, summary: Dict) -> str:
        """Format summary for WhatsApp"""
        
        return f"""📦 *Material Summary*

*Orders:*
• Total: {summary['total_orders']}
• Total Value: ₹{summary['total_value']:,.0f}
• Pending: {summary['pending_delivery']}
• Delivered: {summary['delivered']}

⚠️ *Leakage Alerts:*
• Over-orders: {summary['over_orders']} (₹{summary['over_order_value']:,.0f} excess)
• Short Deliveries: {summary['short_deliveries']}
• Quality Issues: {summary['quality_issues']}

_Use 'set rate <material> <price>' to update your rates_
_Use 'calculate <material> <work> <qty>' to verify orders_"""


# Singleton instance
material_tracker_service = MaterialTrackerService()

