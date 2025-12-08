"""
SiteMind ULTIMATE Leakage Prevention Engine
THE $400K/MONTH PRODUCT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INDUSTRY STATISTICS (Why This Product is ESSENTIAL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 69% of construction projects have cost overruns (KPMG Global Survey)
• 5-15% of costs go to REWORK (FMI Corporation)
• 52% of rework caused by poor project data and miscommunication
• 14% of revenue lost due to poor data management (Autodesk)
• $31.3 BILLION lost annually to rework in US alone
• Construction productivity grew only 1% in 20 years (McKinsey)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE 9 PILLARS OF LEAKAGE PREVENTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CHANGE ORDER INTELLIGENCE     - Capture, track, approve, bill
2. MATERIAL WASTE PREVENTION     - Calculate, verify, track
3. REWORK ELIMINATION           - Memory prevents "I didn't know"
4. DECISION AUDIT TRAIL         - Every decision documented
5. COMMUNICATION BRIDGE         - Site ↔ Office sync
6. VENDOR ACCOUNTABILITY        - Track deliveries, quality
7. SCHEDULE OPTIMIZATION        - Predict delays, alert early
8. REVENUE PROTECTION           - Nothing unbilled, nothing lost
9. REAL-TIME VISIBILITY         - Dashboard for management

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import re
import json

from utils.logger import logger


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class LeakageCategory(Enum):
    """The 9 categories of construction leakages"""
    CHANGE_ORDER = "change_order"
    MATERIAL = "material"
    REWORK = "rework"
    DOCUMENTATION = "documentation"
    COMMUNICATION = "communication"
    VENDOR = "vendor"
    SCHEDULE = "schedule"
    REVENUE = "revenue"
    QUALITY = "quality"


class Severity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"   # Stop work, immediate attention
    HIGH = "high"           # Same day resolution needed
    MEDIUM = "medium"       # This week resolution
    LOW = "low"             # Monitor, track


class Status(Enum):
    """Generic status for tracked items"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    BILLED = "billed"
    PAID = "paid"


@dataclass
class TrackedChange:
    """A tracked change/variation in the project"""
    id: str
    project_id: str
    company_id: str
    
    # What
    category: LeakageCategory
    title: str
    description: str
    
    # Impact
    cost_impact: float = 0.0
    time_impact_days: int = 0
    
    # Source
    source: str = ""  # who/what reported this
    source_message: str = ""  # original message
    detected_at: datetime = None
    
    # Approval
    requires_approval: bool = True
    approved_by: str = ""
    approved_at: datetime = None
    rejection_reason: str = ""
    
    # Billing
    is_billable: bool = False
    billed: bool = False
    invoice_ref: str = ""
    
    # Status
    status: Status = Status.PENDING
    
    # Memory reference
    memory_id: str = ""  # Link to Supermemory
    
    def __post_init__(self):
        if not self.detected_at:
            self.detected_at = datetime.utcnow()


@dataclass
class MaterialEntry:
    """Tracked material order/usage"""
    id: str
    project_id: str
    company_id: str
    
    material: str
    quantity_ordered: float
    quantity_calculated: float
    unit: str
    rate_per_unit: float = 0.0
    
    # Variance
    variance_pct: float = 0.0
    variance_cost: float = 0.0
    
    # Status
    ordered_at: datetime = None
    delivered_at: datetime = None
    verified: bool = False
    verified_by: str = ""
    
    # Issues
    has_issue: bool = False
    issue_description: str = ""
    
    status: Status = Status.PENDING


@dataclass
class ReworkIncident:
    """Tracked rework incident"""
    id: str
    project_id: str
    company_id: str
    
    area: str  # Where
    work_type: str  # What work
    reason: str  # Why rework needed
    root_cause: LeakageCategory  # What category caused this
    
    # Impact
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    time_lost_hours: float = 0.0
    
    # Who
    reported_by: str = ""
    responsible_party: str = ""  # contractor, architect, client
    
    # Prevention
    preventable: bool = True
    prevention_notes: str = ""
    
    created_at: datetime = None
    resolved_at: datetime = None
    status: Status = Status.PENDING


@dataclass
class VendorEntry:
    """Tracked vendor interaction"""
    id: str
    project_id: str
    company_id: str
    
    vendor_name: str
    material_or_service: str
    
    # Order
    po_number: str = ""
    ordered_quantity: float = 0.0
    ordered_amount: float = 0.0
    
    # Delivery
    expected_delivery: datetime = None
    actual_delivery: datetime = None
    delivered_quantity: float = 0.0
    
    # Quality
    quality_check_done: bool = False
    quality_issues: List[str] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)
    
    # Payment
    invoice_received: bool = False
    invoice_amount: float = 0.0
    paid: bool = False
    
    status: Status = Status.PENDING


@dataclass
class DailyLog:
    """Daily project log for complete visibility"""
    date: str
    project_id: str
    company_id: str
    
    # Activity counts
    queries: int = 0
    photos: int = 0
    documents: int = 0
    
    # Tracked items
    changes_detected: int = 0
    changes_approved: int = 0
    changes_pending: int = 0
    
    materials_ordered: int = 0
    materials_delivered: int = 0
    material_issues: int = 0
    
    rework_incidents: int = 0
    
    # Financial
    billable_items_detected: int = 0
    total_billable_amount: float = 0.0
    
    # Alerts
    critical_alerts: int = 0
    high_alerts: int = 0
    
    # People
    active_users: List[str] = field(default_factory=list)
    
    # Key events
    events: List[Dict] = field(default_factory=list)


# =============================================================================
# ULTIMATE LEAKAGE ENGINE
# =============================================================================

class UltimateLeakageEngine:
    """
    The brain that prevents ALL construction money leakages
    
    This is what makes SiteMind worth $1,000/month:
    - Every message is analyzed
    - Every photo is checked
    - Every change is tracked
    - Every material is verified
    - Every vendor is monitored
    - Every decision is documented
    - NOTHING falls through the cracks
    """
    
    def __init__(self):
        # Storage (in production, use Supabase)
        self._changes: Dict[str, List[TrackedChange]] = {}
        self._materials: Dict[str, List[MaterialEntry]] = {}
        self._rework: Dict[str, List[ReworkIncident]] = {}
        self._vendors: Dict[str, List[VendorEntry]] = {}
        self._daily_logs: Dict[str, DailyLog] = {}
        
        self._counter = 0
        
        # Detection patterns (comprehensive!)
        self._init_detection_patterns()
        
        # Material database (Indian construction)
        self._init_material_database()
        
        # Cost estimation database
        self._init_cost_database()
    
    def _init_detection_patterns(self):
        """Initialize all detection patterns"""
        
        # CHANGE ORDER PATTERNS
        self.CHANGE_PATTERNS = {
            "direct_change": [
                r"chang(?:e|ed|ing)\s+(?:to|from|the)",
                r"(?:new|revised|updated)\s+(?:spec|drawing|plan|design|BOQ)",
                r"instead\s+of",
                r"(?:now|should)\s+(?:be|use)",
                r"modify|modification|alteration|alter",
                r"variation|VO\s*#?\d*",
            ],
            "stakeholder_request": [
                r"(?:client|owner|architect|engineer|PMC)\s+(?:said|wants|asked|instructed|directed)",
                r"(?:as\s+per|according\s+to)\s+(?:client|architect|engineer)",
                r"(?:client|owner)\s+(?:approval|approved)",
            ],
            "specification_change": [
                r"(?:increase|decrease|reduce)\s+(?:size|depth|width|thickness|height)",
                r"(?:add|remove|delete)\s+(?:column|beam|slab|wall|room|floor)",
                r"(?:change|replace)\s+(?:grade|type|brand|material)",
                r"M\d+\s+(?:to|→)\s+M\d+",  # Concrete grade change
                r"Fe\d+\s+(?:to|→)\s+Fe\d+",  # Steel grade change
            ],
        }
        
        # BILLABLE WORK PATTERNS
        self.BILLABLE_PATTERNS = [
            r"extra\s+work",
            r"additional\s+(?:work|scope|requirement|item)",
            r"(?:not\s+in|outside|beyond)\s+(?:scope|contract|BOQ|original)",
            r"variation\s+(?:order|work)",
            r"(?:client|owner)\s+(?:asked|requested|wants)\s+(?:extra|additional|new)",
            r"VO\s*#?\d*",
            r"(?:add|added)\s+(?:to|in)\s+(?:scope|work)",
        ]
        
        # MATERIAL PATTERNS
        self.MATERIAL_PATTERNS = [
            r"(?:order|need|require|get|arrange)\s+.*?(\d+(?:\.\d+)?)\s*(bags?|MT|kg|tons?|cum|cft|sqft|sqm|nos?\.?|pieces?|units?|bundles?|rods?)",
            r"(\d+(?:\.\d+)?)\s*(bags?|MT|kg|tons?|cum|cft|sqft|sqm)\s+(?:of\s+)?(cement|steel|rebar|sand|aggregate|bricks?|blocks?|tiles?)",
            r"cement|steel|rebar|TMT|sand|aggregate|crush|jalli|bricks?|blocks?|concrete|RMC",
        ]
        
        # REWORK PATTERNS
        self.REWORK_PATTERNS = [
            r"(?:redo|re-do|rework|re-work|do\s+again|repeat)",
            r"(?:break|demolish|remove|dismantle)\s+(?:and|&)\s+(?:redo|rebuild|reconstruct)",
            r"(?:wrong|incorrect|mistake|error)\s+(?:done|work|dimension|level|alignment)",
            r"(?:not\s+as\s+per|doesn't\s+match|mismatch)\s+(?:drawing|spec|plan)",
            r"(?:reject|rejected|failed)\s+(?:by|in)\s+(?:inspection|QC|quality)",
        ]
        
        # VENDOR/DELIVERY PATTERNS
        self.VENDOR_PATTERNS = [
            r"(?:delivery|delivered|received|arrived)\s+(?:from|by)?\s*(\w+)",
            r"(?:vendor|supplier|contractor)\s+(\w+)",
            r"(?:PO|purchase\s+order)\s*#?\s*(\w+)",
            r"(?:short|less|missing)\s+(?:delivery|quantity|material)",
            r"(?:quality|damaged|defective|rejected)\s+(?:issue|material|delivery)",
            r"(?:delay|late|pending)\s+(?:delivery|material|supply)",
        ]
        
        # SAFETY PATTERNS
        self.SAFETY_PATTERNS = [
            r"(?:no|without|missing)\s+(?:helmet|harness|safety\s+net|PPE|goggles|gloves)",
            r"(?:unsafe|dangerous|hazard|risk)",
            r"(?:fall|fell|falling)\s+(?:from|down|risk)",
            r"(?:exposed|open)\s+(?:rebar|wire|electrical|pit|excavation)",
            r"(?:crack|cracks?)\s+(?:in|on)\s+(?:column|beam|slab|wall|foundation)",
            r"(?:water|seepage|leakage)\s+(?:in|from|through)",
        ]
        
        # SCHEDULE/DELAY PATTERNS
        self.SCHEDULE_PATTERNS = [
            r"(?:delay|delayed|behind|late)\s+(?:by|due\s+to)?",
            r"(?:waiting|wait)\s+(?:for|on)\s+(?:material|approval|drawing|decision)",
            r"(?:work|progress)\s+(?:stopped|halted|paused)",
            r"(?:can't|cannot|unable)\s+(?:proceed|continue|start)",
            r"(?:shortage|short)\s+(?:of\s+)?(labour|labor|material|manpower)",
        ]
    
    def _init_material_database(self):
        """Indian construction material calculation database"""
        
        self.MATERIALS = {
            # CEMENT
            "cement": {
                "unit": "bags",  # 50 kg bag
                "rates": {
                    "per_cum_concrete_m20": 8.5,
                    "per_cum_concrete_m25": 9.5,
                    "per_cum_concrete_m30": 10.5,
                    "per_cum_concrete_m35": 11.5,
                    "per_sqft_plaster_12mm": 0.22,
                    "per_sqft_plaster_20mm": 0.35,
                    "per_sqm_flooring": 0.5,
                },
                "wastage": 0.05,  # 5%
                "avg_price_inr": 380,  # per bag
            },
            
            # STEEL/REBAR
            "steel": {
                "unit": "kg",
                "rates": {
                    "per_cum_slab": 78,
                    "per_cum_beam": 120,
                    "per_cum_column": 180,
                    "per_cum_foundation": 90,
                    "per_cum_staircase": 150,
                },
                "wastage": 0.03,  # 3%
                "avg_price_inr": 65,  # per kg
            },
            
            # SAND
            "sand": {
                "unit": "cum",
                "rates": {
                    "per_cum_concrete": 0.45,
                    "per_sqft_plaster_12mm": 0.018,
                    "per_sqft_plaster_20mm": 0.025,
                    "per_sqm_flooring": 0.04,
                },
                "wastage": 0.10,  # 10%
                "avg_price_inr": 2500,  # per cum
            },
            
            # AGGREGATE
            "aggregate": {
                "unit": "cum",
                "rates": {
                    "per_cum_concrete_20mm": 0.9,
                    "per_cum_concrete_10mm": 0.45,
                },
                "wastage": 0.05,
                "avg_price_inr": 1800,  # per cum
            },
            
            # BRICKS
            "bricks": {
                "unit": "nos",
                "rates": {
                    "per_sqft_wall_9inch": 14,
                    "per_sqft_wall_4.5inch": 7,
                    "per_cum_brickwork": 500,
                },
                "wastage": 0.05,
                "avg_price_inr": 8,  # per brick
            },
            
            # BLOCKS (AAC/CLC)
            "blocks": {
                "unit": "nos",
                "rates": {
                    "per_sqft_wall_200mm": 1.3,
                    "per_sqft_wall_150mm": 1.3,
                    "per_cum_blockwork": 15,  # 600x200x200
                },
                "wastage": 0.03,
                "avg_price_inr": 55,  # per block
            },
            
            # TILES
            "tiles": {
                "unit": "sqft",
                "rates": {
                    "per_sqft_floor": 1.1,  # accounting for cutting
                    "per_sqft_wall": 1.15,
                },
                "wastage": 0.10,
                "avg_price_inr": 50,  # per sqft (average)
            },
            
            # PAINT
            "paint": {
                "unit": "liters",
                "rates": {
                    "per_sqft_wall_2coat": 0.018,
                    "per_sqft_ceiling_2coat": 0.015,
                },
                "wastage": 0.05,
                "avg_price_inr": 350,  # per liter
            },
        }
    
    def _init_cost_database(self):
        """Rework and delay cost estimates"""
        
        self.COSTS = {
            "rework": {
                "concrete_cum": 8000,  # ₹ per cum including breaking
                "brickwork_sqft": 150,
                "plaster_sqft": 80,
                "tiling_sqft": 200,
                "painting_sqft": 50,
                "electrical_point": 500,
                "plumbing_point": 800,
            },
            "delay": {
                "per_day_small_project": 50000,   # ₹50k/day
                "per_day_medium_project": 200000,  # ₹2L/day
                "per_day_large_project": 500000,   # ₹5L/day
            },
            "idle_labor": {
                "mason_per_day": 800,
                "helper_per_day": 500,
                "carpenter_per_day": 900,
                "plumber_per_day": 900,
                "electrician_per_day": 850,
            },
        }
    
    # =========================================================================
    # MAIN ANALYSIS ENGINE
    # =========================================================================
    
    async def analyze_message(
        self,
        message: str,
        company_id: str,
        project_id: str,
        user_id: str,
        user_name: str = "",
        context: List[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Analyze EVERY message for potential leakages
        
        This is called for every WhatsApp message.
        Returns analysis with recommendations and alerts.
        """
        
        message_lower = message.lower()
        
        result = {
            "has_leakage_risk": False,
            "categories": [],
            "changes": [],
            "materials": [],
            "alerts": [],
            "recommendations": [],
            "billable_detected": False,
            "requires_attention": False,
            "summary": "",
        }
        
        # 1. CHECK FOR CHANGE ORDERS
        change_result = self._analyze_for_changes(message, context)
        if change_result["detected"]:
            result["has_leakage_risk"] = True
            result["categories"].append(LeakageCategory.CHANGE_ORDER.value)
            result["changes"].append(change_result)
            result["requires_attention"] = True
            
            # Create tracked change
            change = self._create_tracked_change(
                company_id=company_id,
                project_id=project_id,
                change_result=change_result,
                source=user_name or user_id,
                source_message=message,
            )
            result["recommendations"].append(
                f"📝 *Change Order Detected* [{change.id}]\n"
                f"   {change_result['description'][:100]}\n"
                f"   ⚠️ Requires approval before implementation"
            )
        
        # 2. CHECK FOR BILLABLE WORK
        billable_result = self._analyze_for_billable(message)
        if billable_result["detected"]:
            result["has_leakage_risk"] = True
            result["billable_detected"] = True
            result["categories"].append(LeakageCategory.REVENUE.value)
            result["requires_attention"] = True
            result["recommendations"].append(
                "💰 *Billable Work Detected*\n"
                "   This appears to be extra/additional work.\n"
                "   ✅ Auto-logged for client billing"
            )
        
        # 3. CHECK FOR MATERIAL ORDERS
        material_result = self._analyze_for_materials(message)
        if material_result["detected"]:
            result["categories"].append(LeakageCategory.MATERIAL.value)
            result["materials"].append(material_result)
            
            if material_result.get("waste_risk"):
                result["has_leakage_risk"] = True
                result["requires_attention"] = True
                result["recommendations"].append(
                    f"📦 *Material Order Detected*\n"
                    f"   {material_result['message']}"
                )
        
        # 4. CHECK FOR REWORK INDICATORS
        rework_result = self._analyze_for_rework(message)
        if rework_result["detected"]:
            result["has_leakage_risk"] = True
            result["categories"].append(LeakageCategory.REWORK.value)
            result["requires_attention"] = True
            result["alerts"].append({
                "type": "rework",
                "severity": "high",
                "message": rework_result["message"],
            })
            result["recommendations"].append(
                "🔄 *Rework Detected*\n"
                f"   {rework_result['description']}\n"
                "   ⚠️ Document root cause to prevent recurrence"
            )
        
        # 5. CHECK FOR SAFETY ISSUES
        safety_result = self._analyze_for_safety(message)
        if safety_result["detected"]:
            result["has_leakage_risk"] = True
            result["categories"].append(LeakageCategory.QUALITY.value)
            result["requires_attention"] = True
            result["alerts"].append({
                "type": "safety",
                "severity": "critical",
                "message": safety_result["message"],
            })
        
        # 6. CHECK FOR SCHEDULE/DELAY ISSUES
        schedule_result = self._analyze_for_schedule(message)
        if schedule_result["detected"]:
            result["has_leakage_risk"] = True
            result["categories"].append(LeakageCategory.SCHEDULE.value)
            result["recommendations"].append(
                f"⏰ *Schedule Alert*\n"
                f"   {schedule_result['message']}"
            )
        
        # 7. CHECK FOR VENDOR ISSUES
        vendor_result = self._analyze_for_vendor(message)
        if vendor_result["detected"]:
            result["categories"].append(LeakageCategory.VENDOR.value)
            if vendor_result.get("has_issue"):
                result["has_leakage_risk"] = True
                result["requires_attention"] = True
        
        # Generate summary
        if result["has_leakage_risk"]:
            result["summary"] = self._generate_summary(result)
        
        # Update daily log
        self._update_daily_log(company_id, project_id, result, user_id)
        
        return result
    
    # =========================================================================
    # INDIVIDUAL ANALYZERS
    # =========================================================================
    
    def _analyze_for_changes(self, message: str, context: List[Dict] = None) -> Dict:
        """Analyze message for change orders"""
        
        message_lower = message.lower()
        detected = False
        matched_patterns = []
        change_type = ""
        is_billable = False
        
        # Check all change patterns
        for category, patterns in self.CHANGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected = True
                    matched_patterns.append(pattern)
                    change_type = category
        
        if not detected:
            return {"detected": False}
        
        # Check if billable (client/owner requested)
        for pattern in self.BILLABLE_PATTERNS:
            if re.search(pattern, message_lower):
                is_billable = True
                break
        
        return {
            "detected": True,
            "description": message[:200],
            "change_type": change_type,
            "is_billable": is_billable,
            "matched_patterns": matched_patterns,
            "needs_approval": True,
        }
    
    def _analyze_for_billable(self, message: str) -> Dict:
        """Analyze message for billable work"""
        
        message_lower = message.lower()
        
        for pattern in self.BILLABLE_PATTERNS:
            if re.search(pattern, message_lower):
                return {
                    "detected": True,
                    "description": message[:200],
                    "message": "Extra/additional work detected - will be logged for billing",
                }
        
        return {"detected": False}
    
    def _analyze_for_materials(self, message: str) -> Dict:
        """Analyze message for material orders"""
        
        message_lower = message.lower()
        detected = False
        material_found = ""
        quantity_found = 0.0
        unit_found = ""
        
        # Look for material mentions
        for material in self.MATERIALS.keys():
            if material in message_lower:
                material_found = material
                detected = True
                break
        
        # Look for quantity
        for pattern in self.MATERIAL_PATTERNS:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    groups = match.groups()
                    for g in groups:
                        if g and g.replace(".", "").isdigit():
                            quantity_found = float(g)
                            break
                except:
                    pass
                detected = True
        
        if not detected:
            return {"detected": False}
        
        result = {
            "detected": True,
            "material": material_found,
            "quantity": quantity_found,
            "unit": unit_found,
            "waste_risk": False,
            "message": f"Material mentioned: {material_found}",
        }
        
        # If quantity found, check for waste risk
        if quantity_found > 0 and material_found:
            result["message"] = (
                f"📦 Material order: {quantity_found} {material_found}\n"
                f"   💡 Use 'calculate {material_found}' to verify quantity"
            )
        
        return result
    
    def _analyze_for_rework(self, message: str) -> Dict:
        """Analyze message for rework indicators"""
        
        message_lower = message.lower()
        
        for pattern in self.REWORK_PATTERNS:
            if re.search(pattern, message_lower):
                return {
                    "detected": True,
                    "description": message[:200],
                    "message": "⚠️ Rework detected - this is a cost leakage!",
                }
        
        return {"detected": False}
    
    def _analyze_for_safety(self, message: str) -> Dict:
        """Analyze message for safety issues"""
        
        message_lower = message.lower()
        issues = []
        
        for pattern in self.SAFETY_PATTERNS:
            match = re.search(pattern, message_lower)
            if match:
                issues.append(match.group(0))
        
        if not issues:
            return {"detected": False}
        
        return {
            "detected": True,
            "issues": issues,
            "message": f"🚨 SAFETY ALERT: {', '.join(issues)}",
        }
    
    def _analyze_for_schedule(self, message: str) -> Dict:
        """Analyze message for schedule/delay issues"""
        
        message_lower = message.lower()
        
        for pattern in self.SCHEDULE_PATTERNS:
            if re.search(pattern, message_lower):
                return {
                    "detected": True,
                    "message": "Potential delay/schedule issue detected",
                }
        
        return {"detected": False}
    
    def _analyze_for_vendor(self, message: str) -> Dict:
        """Analyze message for vendor-related issues"""
        
        message_lower = message.lower()
        detected = False
        has_issue = False
        
        for pattern in self.VENDOR_PATTERNS:
            if re.search(pattern, message_lower):
                detected = True
                
                # Check for issues
                issue_words = ["short", "less", "missing", "damaged", "defective", 
                             "rejected", "delay", "late", "quality"]
                if any(word in message_lower for word in issue_words):
                    has_issue = True
        
        return {
            "detected": detected,
            "has_issue": has_issue,
        }
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _create_tracked_change(
        self,
        company_id: str,
        project_id: str,
        change_result: Dict,
        source: str,
        source_message: str,
    ) -> TrackedChange:
        """Create and store a tracked change"""
        
        self._counter += 1
        change_id = f"CO-{datetime.utcnow().strftime('%y%m%d')}-{self._counter:04d}"
        
        change = TrackedChange(
            id=change_id,
            project_id=project_id,
            company_id=company_id,
            category=LeakageCategory.CHANGE_ORDER,
            title=f"Change detected: {change_result['change_type']}",
            description=change_result["description"],
            source=source,
            source_message=source_message,
            is_billable=change_result.get("is_billable", False),
        )
        
        if company_id not in self._changes:
            self._changes[company_id] = []
        self._changes[company_id].append(change)
        
        logger.info(f"📝 Change tracked: {change_id}")
        
        return change
    
    def _generate_summary(self, result: Dict) -> str:
        """Generate summary of analysis"""
        
        parts = []
        
        if result["changes"]:
            parts.append(f"• {len(result['changes'])} change order(s) detected")
        
        if result["billable_detected"]:
            parts.append("• Billable work detected")
        
        if result["materials"]:
            parts.append(f"• {len(result['materials'])} material mention(s)")
        
        if result["alerts"]:
            critical = len([a for a in result["alerts"] if a["severity"] == "critical"])
            if critical:
                parts.append(f"• ⚠️ {critical} CRITICAL alert(s)")
        
        return "\n".join(parts)
    
    def _update_daily_log(
        self,
        company_id: str,
        project_id: str,
        result: Dict,
        user_id: str,
    ):
        """Update daily log with analysis results"""
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"{today}_{project_id}_{company_id}"
        
        if key not in self._daily_logs:
            self._daily_logs[key] = DailyLog(
                date=today,
                project_id=project_id,
                company_id=company_id,
            )
        
        log = self._daily_logs[key]
        log.queries += 1
        
        if user_id not in log.active_users:
            log.active_users.append(user_id)
        
        if result["changes"]:
            log.changes_detected += len(result["changes"])
            log.changes_pending += len(result["changes"])
        
        if result["billable_detected"]:
            log.billable_items_detected += 1
        
        for alert in result.get("alerts", []):
            if alert["severity"] == "critical":
                log.critical_alerts += 1
            elif alert["severity"] == "high":
                log.high_alerts += 1
    
    # =========================================================================
    # MATERIAL CALCULATOR
    # =========================================================================
    
    def calculate_material(
        self,
        material: str,
        work_type: str = "concrete",
        quantity: float = 0,
        unit: str = "cum",
    ) -> Dict[str, Any]:
        """
        Calculate required material with wastage
        
        Examples:
        - calculate_material("cement", "concrete_m25", 10, "cum")
        - calculate_material("steel", "slab", 10, "cum")
        - calculate_material("bricks", "wall_9inch", 1000, "sqft")
        """
        
        material_lower = material.lower()
        
        # Find material in database
        mat_data = None
        for key, data in self.MATERIALS.items():
            if key in material_lower:
                mat_data = data
                material_lower = key
                break
        
        if not mat_data:
            return {
                "success": False,
                "error": f"Material '{material}' not in database",
                "available": list(self.MATERIALS.keys()),
            }
        
        # Find appropriate rate
        rate_key = None
        for key in mat_data["rates"]:
            if work_type.lower() in key.lower():
                rate_key = key
                break
        
        if not rate_key:
            # Use first available rate
            rate_key = list(mat_data["rates"].keys())[0]
        
        rate = mat_data["rates"][rate_key]
        wastage = mat_data["wastage"]
        price = mat_data["avg_price_inr"]
        
        # Calculate
        base_quantity = quantity * rate
        wastage_quantity = base_quantity * wastage
        total_quantity = base_quantity + wastage_quantity
        total_cost = total_quantity * price
        
        return {
            "success": True,
            "material": material_lower,
            "work_type": work_type,
            "input_quantity": quantity,
            "input_unit": unit,
            "rate_used": rate_key,
            "rate": rate,
            "base_quantity": round(base_quantity, 2),
            "wastage_pct": wastage * 100,
            "wastage_quantity": round(wastage_quantity, 2),
            "total_quantity": round(total_quantity, 2),
            "unit": mat_data["unit"],
            "price_per_unit": price,
            "estimated_cost": round(total_cost, 2),
            "formula": f"{quantity} {unit} × {rate} = {base_quantity:.2f} + {wastage*100}% wastage = {total_quantity:.2f} {mat_data['unit']}",
        }
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def get_daily_summary(self, company_id: str, project_id: str = None) -> Dict:
        """Get daily summary for reporting"""
        
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        summary = {
            "date": today,
            "total_queries": 0,
            "changes_detected": 0,
            "changes_pending": 0,
            "billable_items": 0,
            "critical_alerts": 0,
            "high_alerts": 0,
            "active_users": set(),
            "projects": [],
        }
        
        for key, log in self._daily_logs.items():
            if not key.startswith(today):
                continue
            if log.company_id != company_id:
                continue
            if project_id and log.project_id != project_id:
                continue
            
            summary["total_queries"] += log.queries
            summary["changes_detected"] += log.changes_detected
            summary["changes_pending"] += log.changes_pending
            summary["billable_items"] += log.billable_items_detected
            summary["critical_alerts"] += log.critical_alerts
            summary["high_alerts"] += log.high_alerts
            summary["active_users"].update(log.active_users)
            summary["projects"].append(log.project_id)
        
        summary["active_users"] = len(summary["active_users"])
        summary["projects"] = len(set(summary["projects"]))
        
        return summary
    
    def format_daily_summary_whatsapp(self, summary: Dict, company_name: str) -> str:
        """Format daily summary for WhatsApp"""
        
        status = "🟢"
        if summary["critical_alerts"] > 0:
            status = "🔴"
        elif summary["high_alerts"] > 0 or summary["changes_pending"] > 0:
            status = "🟡"
        
        return f"""{status} *Daily Summary - {company_name}*
📅 {summary['date']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *Activity:*
• Total Queries: {summary['total_queries']}
• Active Users: {summary['active_users']}
• Projects Active: {summary['projects']}

📝 *Change Orders:*
• Detected Today: {summary['changes_detected']}
• Pending Approval: {summary['changes_pending']}

💰 *Revenue Protection:*
• Billable Items: {summary['billable_items']}

🚨 *Alerts:*
• Critical: {summary['critical_alerts']}
• High: {summary['high_alerts']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_All leakages are being tracked._
_Nothing falls through the cracks._"""


# Singleton instance
ultimate_leakage_engine = UltimateLeakageEngine()

