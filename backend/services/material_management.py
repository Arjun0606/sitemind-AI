"""
SiteMind Material Management Service
Inventory tracking and consumption monitoring

FEATURES:
- Stock levels
- Receipts and consumption
- Low stock alerts
- Consumption reports
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class MaterialStock:
    material_id: str
    name: str
    unit: str
    current_quantity: float
    minimum_quantity: float
    last_updated: str


@dataclass
class MaterialTransaction:
    id: str
    project_id: str
    material_id: str
    transaction_type: str  # receipt, consumption, adjustment
    quantity: float
    location: Optional[str]
    user_phone: str
    timestamp: str
    notes: Optional[str]


class MaterialManagementService:
    """
    Material inventory management
    """
    
    def __init__(self):
        self._stock: Dict[str, Dict[str, MaterialStock]] = {}  # project_id -> material_id -> stock
        self._transactions: Dict[str, List[MaterialTransaction]] = {}  # project_id -> transactions
        
        # Default materials for construction
        self.default_materials = {
            "cement": {"name": "Cement", "unit": "bags", "min_qty": 50},
            "steel": {"name": "Steel/Rebar", "unit": "MT", "min_qty": 2},
            "sand": {"name": "Sand", "unit": "cu.m", "min_qty": 10},
            "aggregate": {"name": "Aggregate (20mm)", "unit": "cu.m", "min_qty": 10},
            "brick": {"name": "Bricks", "unit": "nos", "min_qty": 5000},
            "block": {"name": "Concrete Blocks", "unit": "nos", "min_qty": 500},
        }
    
    # =========================================================================
    # STOCK MANAGEMENT
    # =========================================================================
    
    def initialize_project(self, project_id: str):
        """Initialize stock tracking for a project"""
        if project_id not in self._stock:
            self._stock[project_id] = {}
            
            for mat_id, mat_info in self.default_materials.items():
                self._stock[project_id][mat_id] = MaterialStock(
                    material_id=mat_id,
                    name=mat_info["name"],
                    unit=mat_info["unit"],
                    current_quantity=0,
                    minimum_quantity=mat_info["min_qty"],
                    last_updated=datetime.utcnow().isoformat(),
                )
    
    def record_receipt(
        self,
        project_id: str,
        material_id: str,
        quantity: float,
        user_phone: str,
        notes: str = None,
    ) -> MaterialStock:
        """Record material receipt"""
        self.initialize_project(project_id)
        
        stock = self._stock[project_id].get(material_id)
        if not stock:
            # Create new material entry
            stock = MaterialStock(
                material_id=material_id,
                name=material_id.title(),
                unit="units",
                current_quantity=0,
                minimum_quantity=10,
                last_updated=datetime.utcnow().isoformat(),
            )
            self._stock[project_id][material_id] = stock
        
        stock.current_quantity += quantity
        stock.last_updated = datetime.utcnow().isoformat()
        
        # Record transaction
        self._record_transaction(
            project_id=project_id,
            material_id=material_id,
            transaction_type="receipt",
            quantity=quantity,
            user_phone=user_phone,
            notes=notes,
        )
        
        return stock
    
    def record_consumption(
        self,
        project_id: str,
        material_id: str,
        quantity: float,
        location: str,
        user_phone: str,
        notes: str = None,
    ) -> MaterialStock:
        """Record material consumption"""
        self.initialize_project(project_id)
        
        stock = self._stock[project_id].get(material_id)
        if stock:
            stock.current_quantity -= quantity
            stock.last_updated = datetime.utcnow().isoformat()
            
            self._record_transaction(
                project_id=project_id,
                material_id=material_id,
                transaction_type="consumption",
                quantity=-quantity,
                location=location,
                user_phone=user_phone,
                notes=notes,
            )
        
        return stock
    
    def _record_transaction(
        self,
        project_id: str,
        material_id: str,
        transaction_type: str,
        quantity: float,
        user_phone: str,
        location: str = None,
        notes: str = None,
    ):
        """Record a transaction"""
        if project_id not in self._transactions:
            self._transactions[project_id] = []
        
        self._transactions[project_id].append(MaterialTransaction(
            id=f"txn_{datetime.utcnow().timestamp():.0f}",
            project_id=project_id,
            material_id=material_id,
            transaction_type=transaction_type,
            quantity=quantity,
            location=location,
            user_phone=user_phone,
            timestamp=datetime.utcnow().isoformat(),
            notes=notes,
        ))
    
    # =========================================================================
    # QUERIES
    # =========================================================================
    
    def get_stock(
        self,
        project_id: str,
        material_id: str = None,
    ) -> Dict[str, MaterialStock]:
        """Get current stock levels"""
        self.initialize_project(project_id)
        
        if material_id:
            stock = self._stock[project_id].get(material_id)
            return {material_id: stock} if stock else {}
        
        return self._stock.get(project_id, {})
    
    def get_low_stock(self, project_id: str) -> List[MaterialStock]:
        """Get materials with low stock"""
        self.initialize_project(project_id)
        
        low = []
        for stock in self._stock[project_id].values():
            if stock.current_quantity <= stock.minimum_quantity:
                low.append(stock)
        
        return low
    
    def get_stock_status(self, project_id: str, material_name: str = None) -> str:
        """Format stock status for WhatsApp"""
        stock = self.get_stock(project_id)
        
        if material_name:
            # Find specific material
            for mat_id, mat_stock in stock.items():
                if material_name.lower() in mat_stock.name.lower():
                    status = "✅ OK" if mat_stock.current_quantity > mat_stock.minimum_quantity else "⚠️ LOW"
                    return f"""**{mat_stock.name} Stock**

Current: {mat_stock.current_quantity} {mat_stock.unit}
Minimum: {mat_stock.minimum_quantity} {mat_stock.unit}
Status: {status}

_Last updated: {mat_stock.last_updated[:10]}_"""
            
            return f"No stock record found for '{material_name}'. Available materials: {', '.join(s.name for s in stock.values())}"
        
        # All materials
        msg = "**Stock Status**\n\n"
        
        for stock in sorted(stock.values(), key=lambda x: x.name):
            if stock.current_quantity <= stock.minimum_quantity:
                icon = "🔴"
            elif stock.current_quantity <= stock.minimum_quantity * 1.5:
                icon = "🟡"
            else:
                icon = "🟢"
            
            msg += f"{icon} {stock.name}: {stock.current_quantity} {stock.unit}\n"
        
        low_stock = self.get_low_stock(project_id)
        if low_stock:
            msg += f"\n⚠️ {len(low_stock)} items need reorder"
        
        return msg
    
    def generate_consumption_report(self, project_id: str, days: int = 7) -> str:
        """Generate consumption report"""
        transactions = self._transactions.get(project_id, [])
        
        # Filter to last N days
        cutoff = datetime.utcnow().isoformat()[:10]
        recent = [t for t in transactions if t.timestamp[:10] >= cutoff]
        
        # Aggregate by material
        consumption = {}
        for t in recent:
            if t.transaction_type == "consumption":
                mat = t.material_id
                consumption[mat] = consumption.get(mat, 0) + abs(t.quantity)
        
        if not consumption:
            return "No consumption recorded in the last week."
        
        report = f"**Material Consumption** (Last {days} days)\n\n"
        
        for mat_id, qty in sorted(consumption.items(), key=lambda x: -x[1]):
            stock = self._stock.get(project_id, {}).get(mat_id)
            unit = stock.unit if stock else "units"
            name = stock.name if stock else mat_id.title()
            report += f"• {name}: {qty} {unit}\n"
        
        return report


# Singleton instance
material_management = MaterialManagementService()
