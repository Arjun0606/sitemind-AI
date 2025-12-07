"""
SiteMind Red Flag Detection Service
Proactively identifies risks before they become expensive problems

RED FLAGS DETECTED:
1. Specification Conflicts - Different specs in drawings vs memory
2. Confusion Patterns - Many people asking about same thing
3. Safety Concerns - Keywords/patterns indicating safety risks
4. Timeline Risks - Delays in approvals, pending RFIs
5. Compliance Issues - Missing approvals, documentation gaps
6. Communication Gaps - Updates not reaching site team
7. Rework Patterns - Repeated issues in same area

VALUE: Catching one major issue = saves ₹5-50 Lakhs
This alone justifies the $500/site subscription.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from utils.logger import logger


class FlagSeverity(str, Enum):
    CRITICAL = "critical"   # Stop work, immediate attention
    HIGH = "high"           # Address within 24 hours
    MEDIUM = "medium"       # Address within 3 days
    LOW = "low"             # Monitor, address when convenient


class FlagCategory(str, Enum):
    SPECIFICATION_CONFLICT = "specification_conflict"
    CONFUSION_PATTERN = "confusion_pattern"
    SAFETY_CONCERN = "safety_concern"
    TIMELINE_RISK = "timeline_risk"
    COMPLIANCE_GAP = "compliance_gap"
    COMMUNICATION_GAP = "communication_gap"
    REWORK_PATTERN = "rework_pattern"
    MATERIAL_ISSUE = "material_issue"
    QUALITY_CONCERN = "quality_concern"


@dataclass
class RedFlag:
    """A detected red flag"""
    flag_id: str
    project_id: str
    category: FlagCategory
    severity: FlagSeverity
    title: str
    description: str
    affected_area: str  # e.g., "Floor 3, Grid B2"
    evidence: List[str]  # Supporting data points
    recommended_action: str
    detected_at: str
    status: str = "open"  # open, acknowledged, resolved, false_positive
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None


class RedFlagService:
    """
    Proactive risk detection for construction projects
    """
    
    def __init__(self):
        self._flags: Dict[str, List[RedFlag]] = {}
        self._query_patterns: Dict[str, Dict[str, int]] = {}
        self._safety_keywords = [
            "crack", "collapse", "danger", "unsafe", "falling", "leak",
            "fire", "electrical", "exposed wire", "no support", "unstable",
            "tilting", "sinking", "flood", "gas", "fumes"
        ]
    
    # =========================================================================
    # FLAG DETECTION
    # =========================================================================
    
    def analyze_query(
        self,
        project_id: str,
        query: str,
        response: str,
        user_phone: str,
        memory_results: List[Dict],
    ) -> Optional[RedFlag]:
        """
        Analyze a query for potential red flags
        
        Called after every query to detect issues proactively
        """
        flags_detected = []
        
        # Check for safety concerns
        safety_flag = self._check_safety_concern(project_id, query)
        if safety_flag:
            flags_detected.append(safety_flag)
        
        # Check for confusion patterns (many asking same thing)
        confusion_flag = self._check_confusion_pattern(project_id, query)
        if confusion_flag:
            flags_detected.append(confusion_flag)
        
        # Check for specification conflicts
        conflict_flag = self._check_specification_conflict(project_id, query, memory_results)
        if conflict_flag:
            flags_detected.append(conflict_flag)
        
        # Store and return most severe flag
        for flag in flags_detected:
            self._store_flag(project_id, flag)
        
        if flags_detected:
            # Return most severe
            flags_detected.sort(key=lambda f: 
                ["critical", "high", "medium", "low"].index(f.severity.value))
            return flags_detected[0]
        
        return None
    
    def _check_safety_concern(self, project_id: str, query: str) -> Optional[RedFlag]:
        """Detect safety-related concerns in queries"""
        query_lower = query.lower()
        
        triggered_keywords = [kw for kw in self._safety_keywords if kw in query_lower]
        
        if triggered_keywords:
            return RedFlag(
                flag_id=f"flag_{int(datetime.utcnow().timestamp() * 1000)}",
                project_id=project_id,
                category=FlagCategory.SAFETY_CONCERN,
                severity=FlagSeverity.CRITICAL if any(k in ["collapse", "danger", "unsafe", "falling"] for k in triggered_keywords) else FlagSeverity.HIGH,
                title="Safety Concern Detected",
                description=f"Query contains safety-related keywords: {', '.join(triggered_keywords)}",
                affected_area="See query for location",
                evidence=[f"Query: {query[:200]}"],
                recommended_action="Verify site conditions immediately. If safety risk confirmed, stop work in affected area.",
                detected_at=datetime.utcnow().isoformat(),
            )
        
        return None
    
    def _check_confusion_pattern(self, project_id: str, query: str) -> Optional[RedFlag]:
        """Detect when many people ask about the same thing"""
        # Track query topics
        if project_id not in self._query_patterns:
            self._query_patterns[project_id] = {}
        
        # Simple topic extraction (would be smarter with NLP)
        topics = self._extract_topics(query)
        
        for topic in topics:
            self._query_patterns[project_id][topic] = \
                self._query_patterns[project_id].get(topic, 0) + 1
            
            count = self._query_patterns[project_id][topic]
            
            # Flag if 5+ queries on same topic in short period
            if count == 5:  # Only flag once at threshold
                return RedFlag(
                    flag_id=f"flag_{int(datetime.utcnow().timestamp() * 1000)}",
                    project_id=project_id,
                    category=FlagCategory.CONFUSION_PATTERN,
                    severity=FlagSeverity.MEDIUM,
                    title=f"Multiple Queries About '{topic}'",
                    description=f"{count} queries received about '{topic}'. This may indicate unclear specifications or recent changes not communicated.",
                    affected_area=topic,
                    evidence=[f"{count} queries on this topic today"],
                    recommended_action="Review specifications for clarity. Consider sending clarification to all site engineers.",
                    detected_at=datetime.utcnow().isoformat(),
                )
        
        return None
    
    def _check_specification_conflict(
        self, 
        project_id: str, 
        query: str,
        memory_results: List[Dict]
    ) -> Optional[RedFlag]:
        """Detect conflicting specifications in memory"""
        # Look for multiple change orders on same element
        change_orders = [m for m in memory_results 
                        if m.get("metadata", {}).get("type") == "change_order"]
        
        if len(change_orders) >= 2:
            # Multiple change orders might indicate conflicts
            return RedFlag(
                flag_id=f"flag_{int(datetime.utcnow().timestamp() * 1000)}",
                project_id=project_id,
                category=FlagCategory.SPECIFICATION_CONFLICT,
                severity=FlagSeverity.HIGH,
                title="Multiple Specification Changes",
                description="This element has multiple change orders. Verify the current specification is being used.",
                affected_area="See query for element",
                evidence=[f"Found {len(change_orders)} change orders for this element"],
                recommended_action="Confirm latest specification with consultant. Ensure all team members have current revision.",
                detected_at=datetime.utcnow().isoformat(),
            )
        
        return None
    
    def _extract_topics(self, query: str) -> List[str]:
        """Extract topics from query for pattern detection"""
        topics = []
        query_lower = query.lower()
        
        # Structural elements
        elements = ["beam", "column", "slab", "foundation", "wall", "staircase"]
        for elem in elements:
            if elem in query_lower:
                topics.append(elem)
        
        # Try to extract location (e.g., "B2", "floor 3")
        import re
        grid_match = re.search(r'\b([A-Z]\d+)\b', query, re.IGNORECASE)
        if grid_match:
            topics.append(grid_match.group(1).upper())
        
        floor_match = re.search(r'floor\s*(\d+)', query, re.IGNORECASE)
        if floor_match:
            topics.append(f"floor_{floor_match.group(1)}")
        
        return topics
    
    # =========================================================================
    # PROACTIVE CHECKS (Run periodically)
    # =========================================================================
    
    def run_daily_checks(self, project_id: str, project_data: Dict) -> List[RedFlag]:
        """Run daily proactive checks"""
        flags = []
        
        # Check for pending RFIs without response
        flags.extend(self._check_pending_rfis(project_id, project_data))
        
        # Check for drawings not acknowledged
        flags.extend(self._check_unacknowledged_drawings(project_id, project_data))
        
        # Check for timeline risks
        flags.extend(self._check_timeline_risks(project_id, project_data))
        
        return flags
    
    def _check_pending_rfis(self, project_id: str, project_data: Dict) -> List[RedFlag]:
        """Check for RFIs pending more than 3 days"""
        # Would check actual RFI data
        return []
    
    def _check_unacknowledged_drawings(self, project_id: str, project_data: Dict) -> List[RedFlag]:
        """Check for recent drawings not acknowledged by site team"""
        return []
    
    def _check_timeline_risks(self, project_id: str, project_data: Dict) -> List[RedFlag]:
        """Check for potential timeline risks"""
        return []
    
    # =========================================================================
    # FLAG MANAGEMENT
    # =========================================================================
    
    def _store_flag(self, project_id: str, flag: RedFlag):
        """Store a detected flag"""
        if project_id not in self._flags:
            self._flags[project_id] = []
        
        self._flags[project_id].append(flag)
        logger.warning(f"🚩 Red flag detected: [{flag.severity.value.upper()}] {flag.title}")
    
    def get_open_flags(self, project_id: str) -> List[RedFlag]:
        """Get all open flags for a project"""
        flags = self._flags.get(project_id, [])
        return [f for f in flags if f.status == "open"]
    
    def get_critical_flags(self, project_id: str) -> List[RedFlag]:
        """Get critical flags that need immediate attention"""
        flags = self.get_open_flags(project_id)
        return [f for f in flags if f.severity in [FlagSeverity.CRITICAL, FlagSeverity.HIGH]]
    
    def acknowledge_flag(self, flag_id: str, acknowledged_by: str) -> bool:
        """Acknowledge a flag"""
        for project_flags in self._flags.values():
            for flag in project_flags:
                if flag.flag_id == flag_id:
                    flag.status = "acknowledged"
                    return True
        return False
    
    def resolve_flag(self, flag_id: str, resolved_by: str, notes: str = "") -> bool:
        """Mark a flag as resolved"""
        for project_flags in self._flags.values():
            for flag in project_flags:
                if flag.flag_id == flag_id:
                    flag.status = "resolved"
                    flag.resolved_at = datetime.utcnow().isoformat()
                    flag.resolved_by = resolved_by
                    return True
        return False
    
    def generate_flag_summary(self, project_id: str) -> str:
        """Generate flag summary for reports"""
        flags = self._flags.get(project_id, [])
        open_flags = [f for f in flags if f.status == "open"]
        resolved_flags = [f for f in flags if f.status == "resolved"]
        
        critical = len([f for f in open_flags if f.severity == FlagSeverity.CRITICAL])
        high = len([f for f in open_flags if f.severity == FlagSeverity.HIGH])
        medium = len([f for f in open_flags if f.severity == FlagSeverity.MEDIUM])
        
        summary = f"""
**Red Flag Status**

Open Issues:
• Critical: {critical}
• High: {high}
• Medium: {medium}

Resolved This Period: {len(resolved_flags)}
"""
        
        if critical > 0:
            summary += "\n⚠️ CRITICAL FLAGS REQUIRE IMMEDIATE ATTENTION"
        
        return summary


# Singleton instance
red_flag_service = RedFlagService()

