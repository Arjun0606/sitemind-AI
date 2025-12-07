"""
SiteMind Intelligence Service
The brain that makes this worth $500/month

THIS IS THE $100K/MONTH ENGINE.

Features:
1. Proactive Alerts - Don't wait, PUSH insights
2. Conflict Detection - Catch issues before they cost money
3. Safety Monitoring - Flag violations instantly
4. Progress Tracking - Visual AI for % completion
5. Expert Knowledge - Not just codes, WISDOM

If this works well, no one will churn.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import re

from utils.logger import logger


@dataclass
class Alert:
    """Proactive alert"""
    level: str  # info, warning, critical
    category: str  # safety, conflict, progress, material, weather
    title: str
    message: str
    action_required: str
    project_id: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


class IntelligenceService:
    """
    Proactive intelligence engine
    
    This is what separates $500/month from free tools.
    """
    
    def __init__(self):
        # Alert queue
        self._alerts: List[Alert] = []
        
        # Pattern database for detection
        self.SAFETY_PATTERNS = [
            r"no\s+safety\s+(helmet|harness|net|equipment)",
            r"working\s+at\s+height",
            r"exposed\s+(rebar|wire|electrical)",
            r"unstable\s+(scaffold|formwork|structure)",
            r"no\s+barricad",
            r"crack\s+in\s+(column|beam|slab|wall)",
            r"water\s+(seepage|leakage|damage)",
            r"rust\s+on\s+(rebar|steel|reinforcement)",
            r"honeycom",  # honeycomb in concrete
            r"cold\s+joint",
            r"segregat",  # concrete segregation
        ]
        
        self.CONFLICT_PATTERNS = [
            r"changed?\s+(from|to)",
            r"(new|revised|updated)\s+drawing",
            r"different\s+(than|from)\s+(original|earlier|previous)",
            r"doesn'?t\s+match",
            r"conflict",
            r"discrepancy",
        ]
        
        self.URGENCY_PATTERNS = [
            r"urgent",
            r"immediately",
            r"asap",
            r"right\s+now",
            r"today",
            r"emergency",
            r"critical",
            r"stop\s+work",
        ]
        
        # Construction expertise database
        self.EXPERT_KNOWLEDGE = {
            "concrete_curing": {
                "minimum_days": 7,
                "ideal_days": 28,
                "tip": "Keep concrete moist for at least 7 days. Use curing compound or wet gunny bags.",
            },
            "rebar_cover": {
                "column": "40mm",
                "beam": "25mm",
                "slab": "15-20mm",
                "foundation": "50mm",
                "ref": "IS 456:2000, Clause 26.4",
            },
            "concrete_grade": {
                "foundation": "M25 minimum",
                "column": "M25-M30",
                "slab": "M20-M25",
                "tip": "Higher grade for seismic zones",
            },
            "formwork_removal": {
                "vertical_surfaces": "16-24 hours",
                "slab_soffit_props": "7 days",
                "beam_soffit": "14 days",
                "tip": "Don't rush formwork removal - it's a common cause of failure",
            },
        }
    
    # =========================================================================
    # SAFETY ANALYSIS
    # =========================================================================
    
    async def analyze_safety(
        self,
        text: str = None,
        image_analysis: str = None,
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Analyze for safety issues
        
        Returns:
            {
                "is_safe": bool,
                "issues": List[str],
                "severity": "ok" | "warning" | "critical",
                "recommendations": List[str]
            }
        """
        issues = []
        recommendations = []
        
        content = f"{text or ''} {image_analysis or ''}".lower()
        
        # Pattern matching
        for pattern in self.SAFETY_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                match = re.search(pattern, content, re.IGNORECASE).group(0)
                issues.append(match)
        
        # Specific checks
        if "height" in content and "harness" not in content:
            issues.append("Working at height without safety harness mentioned")
            recommendations.append("Ensure all workers at height have safety harness")
        
        if "scaffold" in content and "inspect" not in content:
            recommendations.append("Scaffold should be inspected daily before use")
        
        if "concrete" in content and "test" not in content:
            recommendations.append("Ensure concrete cube tests are conducted")
        
        # Severity
        severity = "ok"
        if issues:
            severity = "warning"
            if any(word in content for word in ["crack", "collapse", "fail", "accident"]):
                severity = "critical"
        
        # Generate alert if needed
        if severity in ["warning", "critical"]:
            self._alerts.append(Alert(
                level=severity,
                category="safety",
                title="⚠️ Safety Issue Detected",
                message=f"Potential issues: {', '.join(issues[:3])}",
                action_required="Review immediately and take corrective action",
                project_id=project_id or "unknown",
            ))
        
        return {
            "is_safe": len(issues) == 0,
            "issues": issues,
            "severity": severity,
            "recommendations": recommendations,
        }
    
    # =========================================================================
    # CONFLICT DETECTION
    # =========================================================================
    
    async def detect_conflicts(
        self,
        new_info: str,
        existing_context: List[Dict],
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Detect conflicts between new information and existing decisions
        
        This is GOLD - catches expensive mistakes before they happen.
        """
        conflicts = []
        
        new_lower = new_info.lower()
        
        # Check if this looks like a change
        is_change = any(re.search(p, new_lower) for p in self.CONFLICT_PATTERNS)
        
        if not is_change:
            return {"has_conflicts": False, "conflicts": []}
        
        # Compare with existing context
        for ctx in existing_context:
            ctx_content = ctx.get("content", str(ctx)).lower()
            
            # Look for contradictions
            # This is simplified - in production, use Gemini for semantic comparison
            
            # Dimension conflicts
            dimensions_new = re.findall(r"(\d+)\s*(?:mm|m|cm|inch)", new_lower)
            dimensions_old = re.findall(r"(\d+)\s*(?:mm|m|cm|inch)", ctx_content)
            
            if dimensions_new and dimensions_old:
                for d_new in dimensions_new:
                    for d_old in dimensions_old:
                        if d_new != d_old:
                            conflicts.append({
                                "type": "dimension_mismatch",
                                "new_value": d_new,
                                "old_value": d_old,
                                "context": ctx_content[:100],
                            })
            
            # Material conflicts
            materials = ["steel", "concrete", "cement", "rebar", "brick", "block"]
            for mat in materials:
                if mat in new_lower and mat in ctx_content:
                    # Check if specs changed
                    new_grade = re.search(rf"{mat}.*?(M\d+|Fe\d+|grade\s+\w+)", new_lower)
                    old_grade = re.search(rf"{mat}.*?(M\d+|Fe\d+|grade\s+\w+)", ctx_content)
                    
                    if new_grade and old_grade and new_grade.group(1) != old_grade.group(1):
                        conflicts.append({
                            "type": "material_grade_change",
                            "material": mat,
                            "new_value": new_grade.group(1),
                            "old_value": old_grade.group(1),
                        })
        
        # Generate alert if conflicts found
        if conflicts:
            self._alerts.append(Alert(
                level="warning",
                category="conflict",
                title="🔄 Potential Conflict Detected",
                message=f"New information may conflict with {len(conflicts)} previous decisions",
                action_required="Review changes and confirm with architect/engineer",
                project_id=project_id or "unknown",
            ))
        
        return {
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts,
            "recommendation": "Please verify these changes with the architect" if conflicts else None,
        }
    
    # =========================================================================
    # PROACTIVE ALERTS
    # =========================================================================
    
    def get_pending_alerts(self, project_id: str = None) -> List[Dict]:
        """Get pending alerts for a project"""
        alerts = self._alerts
        
        if project_id:
            alerts = [a for a in alerts if a.project_id == project_id]
        
        return [
            {
                "level": a.level,
                "category": a.category,
                "title": a.title,
                "message": a.message,
                "action": a.action_required,
                "time": a.timestamp.isoformat(),
            }
            for a in alerts
        ]
    
    def add_alert(
        self,
        project_id: str,
        level: str,
        category: str,
        title: str,
        message: str,
        action: str,
    ):
        """Manually add an alert"""
        self._alerts.append(Alert(
            level=level,
            category=category,
            title=title,
            message=message,
            action_required=action,
            project_id=project_id,
        ))
    
    def clear_alerts(self, project_id: str):
        """Clear alerts for a project"""
        self._alerts = [a for a in self._alerts if a.project_id != project_id]
    
    # =========================================================================
    # EXPERT ANSWERS
    # =========================================================================
    
    def get_expert_tip(self, topic: str) -> Optional[str]:
        """Get expert tip for a topic"""
        topic_lower = topic.lower()
        
        for key, knowledge in self.EXPERT_KNOWLEDGE.items():
            if key.replace("_", " ") in topic_lower or any(
                word in topic_lower for word in key.split("_")
            ):
                tip = knowledge.get("tip", "")
                ref = knowledge.get("ref", "")
                
                if tip:
                    result = f"💡 *Expert Tip:* {tip}"
                    if ref:
                        result += f"\n📖 Reference: {ref}"
                    return result
        
        return None
    
    def enhance_answer(self, question: str, answer: str) -> str:
        """Enhance AI answer with expert tips"""
        tip = self.get_expert_tip(question)
        
        if tip:
            return f"{answer}\n\n{tip}"
        
        return answer
    
    # =========================================================================
    # URGENCY DETECTION
    # =========================================================================
    
    def detect_urgency(self, message: str) -> Dict[str, Any]:
        """Detect if message is urgent"""
        message_lower = message.lower()
        
        is_urgent = any(
            re.search(p, message_lower) for p in self.URGENCY_PATTERNS
        )
        
        # Check for safety keywords too
        is_safety_related = any(
            re.search(p, message_lower) for p in self.SAFETY_PATTERNS
        )
        
        return {
            "is_urgent": is_urgent,
            "is_safety_related": is_safety_related,
            "priority": "high" if (is_urgent or is_safety_related) else "normal",
        }
    
    # =========================================================================
    # PROGRESS ESTIMATION
    # =========================================================================
    
    def estimate_progress(
        self,
        photo_analysis: str,
        project_type: str = "residential",
    ) -> Dict[str, Any]:
        """
        Estimate construction progress from photo analysis
        
        This is a simplified version - in production, use Gemini Vision
        with specific prompts for progress estimation.
        """
        analysis_lower = photo_analysis.lower()
        
        # Stage detection
        stages = {
            "excavation": ["excavation", "digging", "pit", "foundation pit"],
            "foundation": ["foundation", "footing", "pile", "raft"],
            "plinth": ["plinth", "basement", "ground level"],
            "structure": ["column", "beam", "slab", "rcc", "concrete"],
            "brickwork": ["brick", "block", "masonry", "wall"],
            "plastering": ["plaster", "rendering", "cement mortar"],
            "finishing": ["paint", "tile", "flooring", "electrical", "plumbing"],
        }
        
        detected_stage = "unknown"
        for stage, keywords in stages.items():
            if any(kw in analysis_lower for kw in keywords):
                detected_stage = stage
        
        # Rough progress mapping
        progress_map = {
            "excavation": 5,
            "foundation": 15,
            "plinth": 25,
            "structure": 50,
            "brickwork": 70,
            "plastering": 85,
            "finishing": 95,
        }
        
        estimated_progress = progress_map.get(detected_stage, 0)
        
        return {
            "detected_stage": detected_stage,
            "estimated_progress_percent": estimated_progress,
            "confidence": "medium",  # Would be higher with proper Gemini analysis
            "note": "Based on visual analysis. Verify with actual progress reports.",
        }
    
    # =========================================================================
    # SMART RESPONSE ENHANCEMENT
    # =========================================================================
    
    async def enhance_response(
        self,
        question: str,
        answer: str,
        context: List[Dict] = None,
        image_analysis: str = None,
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Enhance response with:
        1. Safety checks
        2. Conflict detection
        3. Expert tips
        4. Urgency handling
        
        This is the magic sauce.
        """
        enhanced_answer = answer
        alerts = []
        metadata = {
            "safety_checked": False,
            "conflicts_checked": False,
            "expert_tip_added": False,
            "urgency": "normal",
        }
        
        # 1. Safety check
        safety = await self.analyze_safety(
            text=question + " " + answer,
            image_analysis=image_analysis,
            project_id=project_id,
        )
        
        if not safety["is_safe"]:
            metadata["safety_checked"] = True
            
            safety_warning = "\n\n⚠️ *Safety Note:*\n"
            for issue in safety["issues"][:2]:
                safety_warning += f"• {issue}\n"
            for rec in safety["recommendations"][:2]:
                safety_warning += f"• {rec}\n"
            
            enhanced_answer += safety_warning
            alerts.append({
                "type": "safety",
                "severity": safety["severity"],
            })
        
        # 2. Conflict detection
        if context:
            conflicts = await self.detect_conflicts(
                new_info=question,
                existing_context=context,
                project_id=project_id,
            )
            
            if conflicts["has_conflicts"]:
                metadata["conflicts_checked"] = True
                
                conflict_warning = "\n\n🔄 *Note:* This may differ from previous decisions. Please verify."
                enhanced_answer += conflict_warning
                alerts.append({
                    "type": "conflict",
                    "count": len(conflicts["conflicts"]),
                })
        
        # 3. Expert tip
        tip = self.get_expert_tip(question)
        if tip:
            metadata["expert_tip_added"] = True
            enhanced_answer += f"\n\n{tip}"
        
        # 4. Urgency
        urgency = self.detect_urgency(question)
        metadata["urgency"] = urgency["priority"]
        
        return {
            "answer": enhanced_answer,
            "alerts": alerts,
            "metadata": metadata,
        }


# Singleton
intelligence_service = IntelligenceService()

