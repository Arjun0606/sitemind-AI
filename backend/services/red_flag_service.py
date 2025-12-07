"""
SiteMind Red Flag Service
Automatic detection of critical issues

TYPES:
1. Safety violations
2. Structural concerns
3. Specification conflicts
4. Quality issues
5. Compliance problems
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class RedFlagSeverity(str, Enum):
    CRITICAL = "critical"  # Stop work
    HIGH = "high"          # Immediate attention
    MEDIUM = "medium"      # Review needed
    LOW = "low"            # Monitor


class RedFlagType(str, Enum):
    SAFETY = "safety"
    STRUCTURAL = "structural"
    CONFLICT = "conflict"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    MATERIAL = "material"


@dataclass
class RedFlag:
    id: str
    project_id: str
    flag_type: RedFlagType
    severity: RedFlagSeverity
    title: str
    description: str
    location: str
    detected_from: str
    detected_at: str
    resolved: bool = False
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None


class RedFlagService:
    """
    Detect and manage red flags
    """
    
    def __init__(self):
        self._flags: Dict[str, List[RedFlag]] = {}  # project_id -> flags
        
        # Detection patterns
        self.safety_keywords = [
            "no harness", "without helmet", "open excavation", "exposed rebar",
            "falling hazard", "electrical hazard", "no barricade", "unsafe",
            "danger", "accident", "injury",
        ]
        
        self.structural_concerns = [
            "crack", "settlement", "deflection", "honeycombing",
            "cold joint", "bulging", "spalling", "corrosion",
            "insufficient cover", "wrong rebar",
        ]
        
        self.conflict_patterns = [
            "different from drawing", "doesn't match", "not as per spec",
            "wrong size", "mismatch", "conflict", "contradiction",
        ]
    
    # =========================================================================
    # DETECTION
    # =========================================================================
    
    def analyze_query(
        self,
        project_id: str,
        query: str,
        response: str,
        user_phone: str,
        memory_results: List[Dict] = None,
    ) -> Optional[RedFlag]:
        """
        Analyze a query for potential red flags
        """
        query_lower = query.lower()
        
        # Check for safety issues
        for keyword in self.safety_keywords:
            if keyword in query_lower:
                return self._create_flag(
                    project_id=project_id,
                    flag_type=RedFlagType.SAFETY,
                    severity=RedFlagSeverity.CRITICAL,
                    title="Safety Concern Reported",
                    description=f"Query contains safety concern: '{query[:100]}'",
                    location="Unknown",
                    detected_from=f"Query from {user_phone}",
                )
        
        # Check for structural concerns
        for keyword in self.structural_concerns:
            if keyword in query_lower:
                return self._create_flag(
                    project_id=project_id,
                    flag_type=RedFlagType.STRUCTURAL,
                    severity=RedFlagSeverity.HIGH,
                    title="Structural Concern Reported",
                    description=f"Query mentions structural issue: '{query[:100]}'",
                    location="Unknown",
                    detected_from=f"Query from {user_phone}",
                )
        
        # Check for conflicts
        for pattern in self.conflict_patterns:
            if pattern in query_lower:
                return self._create_flag(
                    project_id=project_id,
                    flag_type=RedFlagType.CONFLICT,
                    severity=RedFlagSeverity.MEDIUM,
                    title="Specification Conflict Reported",
                    description=f"Query mentions conflict: '{query[:100]}'",
                    location="Unknown",
                    detected_from=f"Query from {user_phone}",
                )
        
        return None
    
    def analyze_photo(
        self,
        project_id: str,
        photo_analysis: str,
        location: str,
        user_phone: str,
    ) -> Optional[RedFlag]:
        """
        Analyze photo analysis results for red flags
        """
        analysis_lower = photo_analysis.lower()
        
        # Safety issues in photo
        for keyword in self.safety_keywords:
            if keyword in analysis_lower:
                return self._create_flag(
                    project_id=project_id,
                    flag_type=RedFlagType.SAFETY,
                    severity=RedFlagSeverity.CRITICAL,
                    title="Safety Issue in Photo",
                    description=f"Photo analysis detected: {keyword}",
                    location=location,
                    detected_from="Photo analysis",
                )
        
        # Quality issues
        quality_keywords = ["poor quality", "defect", "issue", "problem", "concern"]
        for keyword in quality_keywords:
            if keyword in analysis_lower:
                return self._create_flag(
                    project_id=project_id,
                    flag_type=RedFlagType.QUALITY,
                    severity=RedFlagSeverity.MEDIUM,
                    title="Quality Concern in Photo",
                    description=f"Photo analysis detected quality concern",
                    location=location,
                    detected_from="Photo analysis",
                )
        
        return None
    
    def _create_flag(
        self,
        project_id: str,
        flag_type: RedFlagType,
        severity: RedFlagSeverity,
        title: str,
        description: str,
        location: str,
        detected_from: str,
    ) -> RedFlag:
        """Create and store a red flag"""
        flag = RedFlag(
            id=f"flag_{datetime.utcnow().timestamp():.0f}",
            project_id=project_id,
            flag_type=flag_type,
            severity=severity,
            title=title,
            description=description,
            location=location,
            detected_from=detected_from,
            detected_at=datetime.utcnow().isoformat(),
        )
        
        if project_id not in self._flags:
            self._flags[project_id] = []
        self._flags[project_id].append(flag)
        
        return flag
    
    # =========================================================================
    # MANAGEMENT
    # =========================================================================
    
    def get_active_flags(self, project_id: str) -> List[RedFlag]:
        """Get all unresolved flags for a project"""
        flags = self._flags.get(project_id, [])
        return [f for f in flags if not f.resolved]
    
    def get_flags_by_severity(
        self,
        project_id: str,
        severity: RedFlagSeverity,
    ) -> List[RedFlag]:
        """Get flags by severity"""
        flags = self._flags.get(project_id, [])
        return [f for f in flags if f.severity == severity and not f.resolved]
    
    def resolve_flag(
        self,
        project_id: str,
        flag_id: str,
        resolved_by: str,
    ) -> bool:
        """Mark a flag as resolved"""
        flags = self._flags.get(project_id, [])
        for flag in flags:
            if flag.id == flag_id:
                flag.resolved = True
                flag.resolved_at = datetime.utcnow().isoformat()
                flag.resolved_by = resolved_by
                return True
        return False
    
    def format_flag_alert(self, flag: RedFlag) -> str:
        """Format flag for WhatsApp notification"""
        severity_icons = {
            RedFlagSeverity.CRITICAL: "🚨",
            RedFlagSeverity.HIGH: "⚠️",
            RedFlagSeverity.MEDIUM: "⚡",
            RedFlagSeverity.LOW: "ℹ️",
        }
        
        icon = severity_icons[flag.severity]
        
        return f"""{icon} **RED FLAG: {flag.title}**

**Severity:** {flag.severity.value.upper()}
**Type:** {flag.flag_type.value}
**Location:** {flag.location}

{flag.description}

**Detected:** {flag.detected_at[:16]}
**Source:** {flag.detected_from}

_Reply 'resolved' when addressed._"""
    
    def get_summary(self, project_id: str) -> str:
        """Get red flag summary for project"""
        active = self.get_active_flags(project_id)
        
        if not active:
            return "✅ No active red flags."
        
        by_severity = {}
        for flag in active:
            sev = flag.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        summary = f"**Red Flags ({len(active)} active)**\n\n"
        
        for sev in ["critical", "high", "medium", "low"]:
            count = by_severity.get(sev, 0)
            if count > 0:
                summary += f"• {sev.title()}: {count}\n"
        
        return summary


# Singleton instance
red_flag_service = RedFlagService()
