"""
SiteMind Material Management Service
Track materials via WhatsApp - inventory, consumption, orders

FEATURES:
1. Inventory Tracking - Current stock levels via WhatsApp
2. Consumption Recording - Log material usage
3. Shortage Alerts - Automatic alerts when stock is low
4. Order Management - Track pending orders
5. Wastage Tracking - Monitor and reduce wastage
6. Cost Analytics - Material cost per sq.ft.

HOW IT WORKS:
- Store keeper updates stock via WhatsApp: "Received 50 bags cement"
- Engineers query: "Cement stock?"
- System alerts PM when stock below threshold
- Automatic consumption calculation based on work progress
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from utils.logger import logger


class MaterialCategory(str, Enum):
    CEMENT = "cement"
    STEEL = "steel"
    AGGREGATE = "aggregate"
    SAND = "sand"
    BRICK = "brick"
    BLOCK = "block"
    CONCRETE = "concrete"
    TILES = "tiles"
    PAINT = "paint"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    OTHER = "other"


class TransactionType(str, Enum):
    RECEIVED = "received"
    CONSUMED = "consumed"
    RETURNED = "returned"
    WASTAGE = "wastage"
    ADJUSTMENT = "adjustment"


class OrderStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Material:
    """A material in inventory"""
    material_id: str
    project_id: str
    name: str
    category: MaterialCategory
    unit: str  # bags, MT, pieces, sqft, etc.
    current_stock: float
    minimum_stock: float  # Alert threshold
    rate: float  # Cost per unit
    location: str  # Storage location
    last_updated: str


@dataclass
class MaterialTransaction:
    """A material transaction (in/out)"""
    transaction_id: str
    project_id: str
    material_id: str
    transaction_type: TransactionType
    quantity: float
    unit: str
    location: str  # Where used/stored
    notes: str
    recorded_by: str
    recorded_at: str
    reference: Optional[str] = None  # PO number, challan, etc.


@dataclass
class MaterialOrder:
    """A material order"""
    order_id: str
    project_id: str
    items: List[Dict]  # [{material_id, quantity, rate}]
    status: OrderStatus
    supplier: str
    ordered_by: str
    ordered_at: str
    expected_delivery: Optional[str] = None
    actual_delivery: Optional[str] = None
    po_number: Optional[str] = None
    total_amount: float = 0


class MaterialManagementService:
    """
    Material inventory and consumption tracking
    """
    
    def __init__(self):
        self._materials: Dict[str, Dict[str, Material]] = {}  # project -> {material_id: Material}
        self._transactions: Dict[str, List[MaterialTransaction]] = {}
        self._orders: Dict[str, List[MaterialOrder]] = {}
    
    # =========================================================================
    # INVENTORY MANAGEMENT
    # =========================================================================
    
    def add_material(
        self,
        project_id: str,
        name: str,
        category: MaterialCategory,
        unit: str,
        initial_stock: float = 0,
        minimum_stock: float = 0,
        rate: float = 0,
        location: str = "Main Store",
    ) -> Material:
        """Add a new material to inventory"""
        material = Material(
            material_id=f"mat_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            name=name,
            category=category,
            unit=unit,
            current_stock=initial_stock,
            minimum_stock=minimum_stock,
            rate=rate,
            location=location,
            last_updated=datetime.utcnow().isoformat(),
        )
        
        if project_id not in self._materials:
            self._materials[project_id] = {}
        
        self._materials[project_id][material.material_id] = material
        
        logger.info(f"📦 Material added: {name} ({initial_stock} {unit})")
        
        return material
    
    def get_material(self, project_id: str, material_id: str) -> Optional[Material]:
        """Get material by ID"""
        return self._materials.get(project_id, {}).get(material_id)
    
    def find_material_by_name(self, project_id: str, name: str) -> Optional[Material]:
        """Find material by name (case-insensitive)"""
        materials = self._materials.get(project_id, {})
        name_lower = name.lower()
        
        for mat in materials.values():
            if mat.name.lower() == name_lower or name_lower in mat.name.lower():
                return mat
        return None
    
    def get_all_materials(self, project_id: str) -> List[Material]:
        """Get all materials for a project"""
        return list(self._materials.get(project_id, {}).values())
    
    # =========================================================================
    # TRANSACTIONS (Via WhatsApp)
    # =========================================================================
    
    def record_receipt(
        self,
        project_id: str,
        material_id: str,
        quantity: float,
        recorded_by: str,
        reference: str = None,
        notes: str = "",
    ) -> Optional[MaterialTransaction]:
        """
        Record material receipt
        
        WhatsApp: "Received 50 bags cement, challan #1234"
        """
        material = self.get_material(project_id, material_id)
        if not material:
            return None
        
        transaction = MaterialTransaction(
            transaction_id=f"txn_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            material_id=material_id,
            transaction_type=TransactionType.RECEIVED,
            quantity=quantity,
            unit=material.unit,
            location=material.location,
            notes=notes,
            recorded_by=recorded_by,
            recorded_at=datetime.utcnow().isoformat(),
            reference=reference,
        )
        
        # Update stock
        material.current_stock += quantity
        material.last_updated = datetime.utcnow().isoformat()
        
        # Store transaction
        if project_id not in self._transactions:
            self._transactions[project_id] = []
        self._transactions[project_id].append(transaction)
        
        logger.info(f"📥 Received: {quantity} {material.unit} {material.name}")
        
        return transaction
    
    def record_consumption(
        self,
        project_id: str,
        material_id: str,
        quantity: float,
        location: str,
        recorded_by: str,
        notes: str = "",
    ) -> Optional[MaterialTransaction]:
        """
        Record material consumption
        
        WhatsApp: "Used 10 bags cement at Floor 3 column"
        """
        material = self.get_material(project_id, material_id)
        if not material:
            return None
        
        if material.current_stock < quantity:
            logger.warning(f"⚠️ Insufficient stock: {material.name}")
            # Still record, but flag negative
        
        transaction = MaterialTransaction(
            transaction_id=f"txn_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            material_id=material_id,
            transaction_type=TransactionType.CONSUMED,
            quantity=quantity,
            unit=material.unit,
            location=location,
            notes=notes,
            recorded_by=recorded_by,
            recorded_at=datetime.utcnow().isoformat(),
        )
        
        # Update stock
        material.current_stock -= quantity
        material.last_updated = datetime.utcnow().isoformat()
        
        if project_id not in self._transactions:
            self._transactions[project_id] = []
        self._transactions[project_id].append(transaction)
        
        logger.info(f"📤 Consumed: {quantity} {material.unit} {material.name} at {location}")
        
        return transaction
    
    def record_wastage(
        self,
        project_id: str,
        material_id: str,
        quantity: float,
        reason: str,
        recorded_by: str,
    ) -> Optional[MaterialTransaction]:
        """Record material wastage"""
        material = self.get_material(project_id, material_id)
        if not material:
            return None
        
        transaction = MaterialTransaction(
            transaction_id=f"txn_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            material_id=material_id,
            transaction_type=TransactionType.WASTAGE,
            quantity=quantity,
            unit=material.unit,
            location="",
            notes=reason,
            recorded_by=recorded_by,
            recorded_at=datetime.utcnow().isoformat(),
        )
        
        material.current_stock -= quantity
        material.last_updated = datetime.utcnow().isoformat()
        
        if project_id not in self._transactions:
            self._transactions[project_id] = []
        self._transactions[project_id].append(transaction)
        
        logger.warning(f"🗑️ Wastage: {quantity} {material.unit} {material.name} - {reason}")
        
        return transaction
    
    # =========================================================================
    # STOCK ALERTS
    # =========================================================================
    
    def check_low_stock(self, project_id: str) -> List[Dict]:
        """Check for materials below minimum stock"""
        materials = self._materials.get(project_id, {})
        low_stock = []
        
        for mat in materials.values():
            if mat.current_stock <= mat.minimum_stock:
                low_stock.append({
                    "material_id": mat.material_id,
                    "name": mat.name,
                    "current_stock": mat.current_stock,
                    "minimum_stock": mat.minimum_stock,
                    "unit": mat.unit,
                    "shortage": mat.minimum_stock - mat.current_stock,
                    "critical": mat.current_stock <= mat.minimum_stock * 0.5,
                })
        
        return low_stock
    
    def generate_low_stock_alert(self, project_id: str) -> Optional[str]:
        """Generate alert message for low stock"""
        low_stock = self.check_low_stock(project_id)
        
        if not low_stock:
            return None
        
        critical = [m for m in low_stock if m["critical"]]
        warning = [m for m in low_stock if not m["critical"]]
        
        alert = "**Material Stock Alert**\n\n"
        
        if critical:
            alert += "🚨 **CRITICAL (Order Immediately):**\n"
            for m in critical:
                alert += f"• {m['name']}: {m['current_stock']} {m['unit']} remaining\n"
            alert += "\n"
        
        if warning:
            alert += "⚠️ **Low Stock:**\n"
            for m in warning:
                alert += f"• {m['name']}: {m['current_stock']} {m['unit']} (min: {m['minimum_stock']})\n"
        
        return alert
    
    # =========================================================================
    # ORDERS
    # =========================================================================
    
    def create_order(
        self,
        project_id: str,
        items: List[Dict],  # [{material_id, quantity, rate}]
        supplier: str,
        ordered_by: str,
        expected_delivery: str = None,
    ) -> MaterialOrder:
        """Create a material order"""
        total = sum(item["quantity"] * item.get("rate", 0) for item in items)
        
        order = MaterialOrder(
            order_id=f"ord_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            items=items,
            status=OrderStatus.PENDING,
            supplier=supplier,
            ordered_by=ordered_by,
            ordered_at=datetime.utcnow().isoformat(),
            expected_delivery=expected_delivery,
            total_amount=total,
        )
        
        if project_id not in self._orders:
            self._orders[project_id] = []
        self._orders[project_id].append(order)
        
        return order
    
    def update_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        notes: str = None,
    ) -> bool:
        """Update order status"""
        for project_orders in self._orders.values():
            for order in project_orders:
                if order.order_id == order_id:
                    order.status = status
                    if status == OrderStatus.DELIVERED:
                        order.actual_delivery = datetime.utcnow().isoformat()
                    return True
        return False
    
    def get_pending_orders(self, project_id: str) -> List[MaterialOrder]:
        """Get pending orders"""
        orders = self._orders.get(project_id, [])
        return [o for o in orders if o.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]]
    
    # =========================================================================
    # WHATSAPP QUERIES
    # =========================================================================
    
    def get_stock_status(self, project_id: str, material_name: str = None) -> str:
        """
        Get stock status for WhatsApp query
        
        Query: "Cement stock?" or "Material status?"
        """
        if material_name:
            material = self.find_material_by_name(project_id, material_name)
            if material:
                status = "⚠️ LOW" if material.current_stock <= material.minimum_stock else "✓ OK"
                return f"""**{material.name}**
Stock: {material.current_stock} {material.unit}
Minimum: {material.minimum_stock} {material.unit}
Status: {status}
Location: {material.location}"""
            return f"Material '{material_name}' not found in inventory."
        
        # All materials summary
        materials = self.get_all_materials(project_id)
        if not materials:
            return "No materials in inventory."
        
        response = "**Material Stock Summary**\n\n"
        for mat in materials:
            status = "⚠️" if mat.current_stock <= mat.minimum_stock else "✓"
            response += f"{status} {mat.name}: {mat.current_stock} {mat.unit}\n"
        
        low_stock = self.check_low_stock(project_id)
        if low_stock:
            response += f"\n⚠️ {len(low_stock)} materials below minimum stock"
        
        return response
    
    # =========================================================================
    # REPORTS
    # =========================================================================
    
    def generate_consumption_report(
        self,
        project_id: str,
        start_date: str = None,
        end_date: str = None,
    ) -> str:
        """Generate material consumption report"""
        transactions = self._transactions.get(project_id, [])
        
        # Filter by date if provided
        if start_date:
            transactions = [t for t in transactions 
                          if t.recorded_at >= start_date]
        if end_date:
            transactions = [t for t in transactions
                          if t.recorded_at <= end_date]
        
        # Group by material
        consumption = {}
        wastage = {}
        
        for txn in transactions:
            mat = self.get_material(project_id, txn.material_id)
            if not mat:
                continue
            
            if txn.transaction_type == TransactionType.CONSUMED:
                consumption[mat.name] = consumption.get(mat.name, 0) + txn.quantity
            elif txn.transaction_type == TransactionType.WASTAGE:
                wastage[mat.name] = wastage.get(mat.name, 0) + txn.quantity
        
        report = f"""
**Material Consumption Report**
Period: {start_date or 'All time'} to {end_date or 'Now'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONSUMPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for name, qty in consumption.items():
            mat = self.find_material_by_name(project_id, name)
            unit = mat.unit if mat else ""
            report += f"• {name}: {qty} {unit}\n"
        
        if wastage:
            report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WASTAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
            for name, qty in wastage.items():
                mat = self.find_material_by_name(project_id, name)
                unit = mat.unit if mat else ""
                report += f"• {name}: {qty} {unit}\n"
        
        return report


# Singleton instance
material_management = MaterialManagementService()

