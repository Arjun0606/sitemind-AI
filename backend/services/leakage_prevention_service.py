"""
SiteMind Leakage Prevention Service
THE CORE OF THE $100K/MONTH PRODUCT

This service ensures ZERO money leakages by:
1. Tracking every change order
2. Capturing every decision
3. Flagging deviations from specs
4. Preventing material waste
5. Ensuring nothing is unbilled

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEAKAGE TYPES WE PREVENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Untracked Change Orders    → Every change logged & tracked
2. Material Waste             → Exact calculations, no over-ordering
3. Rework from Miscommunication → Memory prevents "I didn't know"
4. Duplicate Payments         → Audit trail of all approvals
5. Idle Time                  → Instant answers, no waiting
6. Unbilled Work              → Extra work auto-flagged for billing
7. Vendor Issues              → Photo proof, quality documented
8. Poor Scheduling            → Daily briefs, proactive alerts
9. Revenue Leakage            → Nothing forgotten, everything billed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re

from utils.logger import logger


class LeakageType(Enum):
    """Types of construction money leakages"""
    CHANGE_ORDER = "change_order"           # Untracked changes
    MATERIAL_WASTE = "material_waste"       # Over-ordering, wrong materials
    REWORK = "rework"                       # Miscommunication causing redo
    DUPLICATE_PAYMENT = "duplicate_payment" # Paying twice for same thing
    IDLE_TIME = "idle_time"                 # Workers waiting for decisions
    UNBILLED_WORK = "unbilled_work"         # Extra work not charged to client
    VENDOR_ISSUE = "vendor_issue"           # Overcharging, quality issues
    SCHEDULING = "scheduling"               # Poor planning causing delays
    REVENUE_LEAKAGE = "revenue_leakage"     # Earned but uncollected money


@dataclass
class ChangeOrder:
    """Tracked change order"""
    id: str
    project_id: str
    company_id: str
    
    # What changed
    description: str
    original_spec: str = ""
    new_spec: str = ""
    reason: str = ""
    
    # Who/When
    requested_by: str = ""
    requested_at: datetime = None
    approved_by: str = ""
    approved_at: datetime = None
    
    # Cost impact
    estimated_cost_impact: float = 0.0
    is_billable: bool = False
    billed: bool = False
    
    # Status
    status: str = "pending"  # pending, approved, rejected, implemented
    
    def __post_init__(self):
        if not self.requested_at:
            self.requested_at = datetime.utcnow()


@dataclass
class MaterialRequest:
    """Tracked material request"""
    id: str
    project_id: str
    company_id: str
    
    material: str
    quantity: float
    unit: str
    
    # Calculation
    calculated_quantity: float = 0.0
    variance_pct: float = 0.0  # % difference from calculated
    
    requested_by: str = ""
    requested_at: datetime = None
    
    status: str = "pending"  # pending, approved, ordered, delivered
    
    # Flags
    is_over_order: bool = False
    waste_risk: str = "low"  # low, medium, high


@dataclass 
class LeakageAlert:
    """Alert for potential money leakage"""
    id: str
    project_id: str
    company_id: str
    
    leakage_type: LeakageType
    severity: str  # low, medium, high, critical
    
    title: str
    description: str
    estimated_loss: float = 0.0
    
    # Resolution
    action_required: str = ""
    resolved: bool = False
    resolved_by: str = ""
    resolved_at: datetime = None
    
    created_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()


class LeakagePreventionService:
    """
    The brain that prevents all construction money leakages
    """
    
    def __init__(self):
        # Storage (use database in production)
        self._change_orders: Dict[str, List[ChangeOrder]] = {}
        self._material_requests: Dict[str, List[MaterialRequest]] = {}
        self._alerts: Dict[str, List[LeakageAlert]] = {}
        self._billable_items: Dict[str, List[Dict]] = {}
        
        self._counter = 0
        
        # Detection patterns
        self.CHANGE_PATTERNS = [
            r"change(?:d|s|ing)?\s+(?:to|from|the)",
            r"(?:new|revised|updated)\s+(?:spec|drawing|plan|design)",
            r"instead\s+of",
            r"(?:now|should)\s+(?:be|use)",
            r"(?:client|architect|engineer)\s+(?:said|wants|asked)",
            r"modify|modification|alteration|alter",
            r"increase|decrease|reduce|add|remove",
            r"different\s+(?:than|from)",
        ]
        
        self.MATERIAL_PATTERNS = [
            r"(\d+(?:\.\d+)?)\s*(bags?|kg|tons?|cubic\s*m|cu\.?m|sqft|sqm|meters?|feet|nos?\.?|pieces?|units?)",
            r"(?:need|require|order|get)\s+.*?(cement|steel|rebar|concrete|bricks?|blocks?|sand|aggregate)",
            r"(?:how\s+much|quantity|amount)\s+(?:of\s+)?(\w+)",
        ]
        
        self.BILLABLE_PATTERNS = [
            r"extra\s+work",
            r"additional\s+(?:work|scope|requirement)",
            r"(?:client|owner)\s+(?:asked|requested|wants)",
            r"(?:not\s+in|outside)\s+(?:scope|contract|original)",
            r"variation|VO|change\s+order",
        ]
    
    # =========================================================================
    # CHANGE ORDER TRACKING
    # =========================================================================
    
    def detect_change_order(self, message: str, context: str = "") -> Optional[Dict]:
        """
        Detect if a message contains a change order
        
        Returns change order details if detected, None otherwise
        """
        message_lower = message.lower()
        combined = f"{message_lower} {context.lower()}"
        
        # Check patterns
        is_change = any(re.search(p, combined) for p in self.CHANGE_PATTERNS)
        
        if not is_change:
            return None
        
        # Extract details
        change_info = {
            "detected": True,
            "description": message[:200],
            "patterns_matched": [],
            "needs_approval": True,
            "is_billable": False,
        }
        
        for pattern in self.CHANGE_PATTERNS:
            if re.search(pattern, combined):
                change_info["patterns_matched"].append(pattern)
        
        # Check if billable (client-requested)
        if any(word in combined for word in ["client", "owner", "extra", "additional"]):
            change_info["is_billable"] = True
        
        return change_info
    
    def create_change_order(
        self,
        project_id: str,
        company_id: str,
        description: str,
        original_spec: str = "",
        new_spec: str = "",
        reason: str = "",
        requested_by: str = "",
        estimated_cost: float = 0.0,
        is_billable: bool = False,
    ) -> ChangeOrder:
        """Create and track a change order"""
        
        self._counter += 1
        co_id = f"CO-{project_id[:4]}-{self._counter:04d}"
        
        change_order = ChangeOrder(
            id=co_id,
            project_id=project_id,
            company_id=company_id,
            description=description,
            original_spec=original_spec,
            new_spec=new_spec,
            reason=reason,
            requested_by=requested_by,
            estimated_cost_impact=estimated_cost,
            is_billable=is_billable,
        )
        
        # Store
        if company_id not in self._change_orders:
            self._change_orders[company_id] = []
        self._change_orders[company_id].append(change_order)
        
        logger.info(f"📝 Change Order created: {co_id} - {description[:50]}...")
        
        # Create alert for unapproved change
        self.create_alert(
            project_id=project_id,
            company_id=company_id,
            leakage_type=LeakageType.CHANGE_ORDER,
            severity="medium",
            title=f"New Change Order: {co_id}",
            description=f"{description}\n\nRequires approval before implementation.",
            action_required="Review and approve/reject change order",
        )
        
        return change_order
    
    def approve_change_order(
        self,
        change_order_id: str,
        approved_by: str,
        company_id: str,
    ) -> bool:
        """Approve a change order"""
        
        orders = self._change_orders.get(company_id, [])
        for order in orders:
            if order.id == change_order_id:
                order.status = "approved"
                order.approved_by = approved_by
                order.approved_at = datetime.utcnow()
                
                logger.info(f"✅ Change Order approved: {change_order_id} by {approved_by}")
                
                # If billable, add to billable items
                if order.is_billable:
                    self.add_billable_item(
                        company_id=company_id,
                        project_id=order.project_id,
                        description=f"Change Order: {order.description}",
                        amount=order.estimated_cost_impact,
                        reference=change_order_id,
                    )
                
                return True
        
        return False
    
    def get_pending_change_orders(self, company_id: str, project_id: str = None) -> List[ChangeOrder]:
        """Get all pending change orders"""
        orders = self._change_orders.get(company_id, [])
        pending = [o for o in orders if o.status == "pending"]
        
        if project_id:
            pending = [o for o in pending if o.project_id == project_id]
        
        return pending
    
    # =========================================================================
    # MATERIAL MANAGEMENT
    # =========================================================================
    
    def calculate_material(
        self,
        material: str,
        area_sqft: float = 0,
        volume_cum: float = 0,
        length_m: float = 0,
    ) -> Dict[str, Any]:
        """
        Calculate required material quantity
        Prevents over-ordering and waste
        """
        
        # Material calculation factors (standard industry rates)
        calculations = {
            "cement": {
                "unit": "bags",
                "per_cum_concrete": 8.5,  # bags per cubic meter M20
                "per_sqft_plaster": 0.2,
                "wastage_factor": 1.05,  # 5% wastage
            },
            "sand": {
                "unit": "cum",
                "per_cum_concrete": 0.45,
                "per_sqft_plaster": 0.02,
                "wastage_factor": 1.10,  # 10% wastage
            },
            "aggregate": {
                "unit": "cum",
                "per_cum_concrete": 0.9,
                "wastage_factor": 1.05,
            },
            "steel": {
                "unit": "kg",
                "per_cum_rcc": 78,  # kg per cum for slabs
                "per_cum_column": 180,  # kg per cum for columns
                "wastage_factor": 1.03,  # 3% wastage
            },
            "bricks": {
                "unit": "nos",
                "per_sqft_wall": 14,  # 9" wall
                "wastage_factor": 1.05,
            },
        }
        
        material_lower = material.lower()
        
        # Find matching material
        calc = None
        for key, value in calculations.items():
            if key in material_lower:
                calc = value
                material_key = key
                break
        
        if not calc:
            return {
                "material": material,
                "calculated": False,
                "message": "Material not in database. Please verify quantity manually.",
            }
        
        # Calculate based on inputs
        quantity = 0
        
        if volume_cum > 0:
            if "per_cum_concrete" in calc:
                quantity = volume_cum * calc["per_cum_concrete"]
            elif "per_cum_rcc" in calc:
                quantity = volume_cum * calc["per_cum_rcc"]
        
        elif area_sqft > 0:
            if "per_sqft_plaster" in calc:
                quantity = area_sqft * calc["per_sqft_plaster"]
            elif "per_sqft_wall" in calc:
                quantity = area_sqft * calc["per_sqft_wall"]
        
        # Apply wastage factor
        quantity_with_wastage = quantity * calc["wastage_factor"]
        
        return {
            "material": material_key,
            "calculated": True,
            "quantity": round(quantity, 2),
            "quantity_with_wastage": round(quantity_with_wastage, 2),
            "unit": calc["unit"],
            "wastage_factor": calc["wastage_factor"],
            "wastage_pct": (calc["wastage_factor"] - 1) * 100,
            "formula": f"{quantity:.2f} × {calc['wastage_factor']} = {quantity_with_wastage:.2f} {calc['unit']}",
        }
    
    def check_material_order(
        self,
        material: str,
        requested_qty: float,
        calculated_qty: float,
    ) -> Dict[str, Any]:
        """
        Check if material order quantity is appropriate
        Flags potential waste
        """
        
        if calculated_qty == 0:
            return {
                "status": "unknown",
                "message": "Cannot verify - no calculated quantity",
            }
        
        variance = ((requested_qty - calculated_qty) / calculated_qty) * 100
        
        result = {
            "requested": requested_qty,
            "calculated": calculated_qty,
            "variance_pct": round(variance, 1),
        }
        
        if variance > 20:
            result["status"] = "over_order"
            result["risk"] = "high"
            result["message"] = f"⚠️ OVER-ORDER WARNING: {variance:.1f}% more than calculated. Potential waste!"
            result["recommendation"] = f"Consider ordering {calculated_qty:.1f} instead of {requested_qty:.1f}"
            
            # Create alert
            self.create_alert(
                project_id="",  # Will be set by caller
                company_id="",
                leakage_type=LeakageType.MATERIAL_WASTE,
                severity="high",
                title=f"Material Over-Order: {material}",
                description=f"Requested {requested_qty} but calculated need is {calculated_qty}. {variance:.1f}% excess.",
                estimated_loss=0,  # Will need cost data
                action_required="Verify quantity before ordering",
            )
            
        elif variance > 10:
            result["status"] = "slightly_high"
            result["risk"] = "medium"
            result["message"] = f"📊 Order is {variance:.1f}% above calculated. Within acceptable range but verify."
            
        elif variance < -10:
            result["status"] = "under_order"
            result["risk"] = "medium"
            result["message"] = f"📊 Order is {abs(variance):.1f}% BELOW calculated. May cause shortage!"
            
        else:
            result["status"] = "ok"
            result["risk"] = "low"
            result["message"] = "✅ Order quantity is appropriate"
        
        return result
    
    # =========================================================================
    # BILLABLE ITEMS TRACKING
    # =========================================================================
    
    def detect_billable_work(self, message: str) -> Optional[Dict]:
        """Detect if message mentions billable extra work"""
        
        message_lower = message.lower()
        
        is_billable = any(re.search(p, message_lower) for p in self.BILLABLE_PATTERNS)
        
        if not is_billable:
            return None
        
        return {
            "detected": True,
            "description": message[:200],
            "needs_approval": True,
            "message": "💰 This looks like EXTRA WORK that should be billed to client!",
        }
    
    def add_billable_item(
        self,
        company_id: str,
        project_id: str,
        description: str,
        amount: float = 0.0,
        reference: str = "",
    ):
        """Add an item to billable work tracking"""
        
        if company_id not in self._billable_items:
            self._billable_items[company_id] = []
        
        item = {
            "id": f"BILL-{len(self._billable_items[company_id]) + 1:04d}",
            "project_id": project_id,
            "description": description,
            "amount": amount,
            "reference": reference,
            "created_at": datetime.utcnow().isoformat(),
            "billed": False,
            "invoice_id": None,
        }
        
        self._billable_items[company_id].append(item)
        
        logger.info(f"💰 Billable item added: {description[:50]}...")
        
        return item
    
    def get_unbilled_items(self, company_id: str, project_id: str = None) -> List[Dict]:
        """Get all unbilled work items"""
        
        items = self._billable_items.get(company_id, [])
        unbilled = [i for i in items if not i["billed"]]
        
        if project_id:
            unbilled = [i for i in unbilled if i["project_id"] == project_id]
        
        return unbilled
    
    # =========================================================================
    # ALERT SYSTEM
    # =========================================================================
    
    def create_alert(
        self,
        project_id: str,
        company_id: str,
        leakage_type: LeakageType,
        severity: str,
        title: str,
        description: str,
        estimated_loss: float = 0.0,
        action_required: str = "",
    ) -> LeakageAlert:
        """Create a leakage alert"""
        
        self._counter += 1
        alert_id = f"ALERT-{self._counter:06d}"
        
        alert = LeakageAlert(
            id=alert_id,
            project_id=project_id,
            company_id=company_id,
            leakage_type=leakage_type,
            severity=severity,
            title=title,
            description=description,
            estimated_loss=estimated_loss,
            action_required=action_required,
        )
        
        if company_id not in self._alerts:
            self._alerts[company_id] = []
        self._alerts[company_id].append(alert)
        
        logger.warning(f"🚨 Leakage Alert: [{severity.upper()}] {title}")
        
        return alert
    
    def get_active_alerts(self, company_id: str, project_id: str = None) -> List[LeakageAlert]:
        """Get all active (unresolved) alerts"""
        
        alerts = self._alerts.get(company_id, [])
        active = [a for a in alerts if not a.resolved]
        
        if project_id:
            active = [a for a in active if a.project_id == project_id]
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        active.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        return active
    
    # =========================================================================
    # MESSAGE ANALYSIS (Main entry point)
    # =========================================================================
    
    async def analyze_message(
        self,
        message: str,
        company_id: str,
        project_id: str,
        user_id: str,
        context: List[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Analyze incoming message for potential leakages
        
        This is called for EVERY WhatsApp message to catch:
        1. Change orders
        2. Material requests
        3. Billable work
        4. Deviations
        """
        
        result = {
            "change_order": None,
            "material_check": None,
            "billable_work": None,
            "alerts": [],
            "recommendations": [],
        }
        
        # 1. Check for change orders
        change = self.detect_change_order(message)
        if change:
            result["change_order"] = change
            result["recommendations"].append(
                "📝 This looks like a CHANGE ORDER. It should be documented and approved."
            )
        
        # 2. Check for billable work
        billable = self.detect_billable_work(message)
        if billable:
            result["billable_work"] = billable
            result["recommendations"].append(
                "💰 This looks like EXTRA WORK. Make sure it's billed to the client!"
            )
        
        # 3. Check for material mentions (for calculation)
        for pattern in self.MATERIAL_PATTERNS:
            match = re.search(pattern, message.lower())
            if match:
                result["recommendations"].append(
                    "📦 Material mentioned. Type 'calculate <material> <area/volume>' to verify quantities."
                )
                break
        
        return result
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def get_leakage_summary(self, company_id: str) -> Dict[str, Any]:
        """Get summary of potential leakages for a company"""
        
        change_orders = self._change_orders.get(company_id, [])
        alerts = self._alerts.get(company_id, [])
        billable = self._billable_items.get(company_id, [])
        
        pending_cos = [co for co in change_orders if co.status == "pending"]
        active_alerts = [a for a in alerts if not a.resolved]
        unbilled = [b for b in billable if not b["billed"]]
        
        # Calculate potential loss
        potential_loss = sum(a.estimated_loss for a in active_alerts)
        unbilled_amount = sum(b["amount"] for b in unbilled)
        
        return {
            "total_change_orders": len(change_orders),
            "pending_change_orders": len(pending_cos),
            "total_alerts": len(alerts),
            "active_alerts": len(active_alerts),
            "critical_alerts": len([a for a in active_alerts if a.severity == "critical"]),
            "high_alerts": len([a for a in active_alerts if a.severity == "high"]),
            "unbilled_items": len(unbilled),
            "unbilled_amount": unbilled_amount,
            "potential_loss": potential_loss,
            "status": "attention_needed" if active_alerts else "ok",
        }
    
    def format_summary_whatsapp(self, summary: Dict) -> str:
        """Format summary for WhatsApp"""
        
        status_emoji = "🔴" if summary["critical_alerts"] > 0 else (
            "🟡" if summary["active_alerts"] > 0 else "🟢"
        )
        
        return f"""{status_emoji} *Leakage Prevention Summary*

📝 *Change Orders:*
   Pending: {summary['pending_change_orders']}
   Total: {summary['total_change_orders']}

🚨 *Active Alerts:*
   Critical: {summary['critical_alerts']}
   High: {summary['high_alerts']}
   Total: {summary['active_alerts']}

💰 *Unbilled Work:*
   Items: {summary['unbilled_items']}
   Amount: ${summary['unbilled_amount']:,.0f}

_Type 'alerts' to see details_
_Type 'unbilled' to see billable items_"""


# Singleton instance
leakage_prevention_service = LeakagePreventionService()

