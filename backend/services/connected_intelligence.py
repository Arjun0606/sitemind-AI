"""
Connected Intelligence - SIMPLIFIED
====================================

WHAT THIS DOES (reliably):
1. Tracks drawing revisions
2. Logs decisions with full audit trail
3. Manages RFIs
4. Provides stats for dashboard

WHAT THIS DOESN'T DO (removed):
- "AI detects rebar from photos" ❌
- "AI catches mismatches automatically" ❌
- Any risky computer vision claims ❌

This is the boring, reliable version that actually ships.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from services.memory_service import memory_service
from utils.logger import logger


@dataclass
class DrawingRevision:
    """Track drawing revisions"""
    drawing_name: str
    revision: str
    uploaded_by: str
    uploaded_at: datetime
    changes: str = None
    file_path: str = None


@dataclass
class Decision:
    """Track decisions"""
    id: str
    description: str
    approved_by: str
    approved_at: datetime
    project_id: str
    context: str = None


@dataclass
class RFI:
    """Track RFIs"""
    id: str
    description: str
    raised_by: str
    assigned_to: str
    raised_at: datetime
    status: str = "open"  # open, responded, closed
    response: str = None
    responded_at: datetime = None


class ConnectedIntelligence:
    """
    Simplified Connected Intelligence
    
    Focus on:
    - Drawing revision tracking
    - Decision logging
    - RFI management
    - Stats for dashboard
    """
    
    def __init__(self):
        # In-memory stores (will be backed by Supabase in production)
        self._drawings: Dict[str, List[DrawingRevision]] = {}  # key: company_project
        self._decisions: Dict[str, List[Decision]] = {}
        self._rfis: Dict[str, List[RFI]] = {}
    
    # =========================================================================
    # DRAWING REVISIONS
    # =========================================================================
    
    async def log_drawing_revision(
        self,
        company_id: str,
        project_id: str,
        drawing_name: str,
        revision: str,
        uploaded_by: str,
        changes: str = None,
        file_path: str = None,
    ) -> Dict[str, Any]:
        """
        Log a drawing revision
        Returns previous revisions if any
        """
        key = f"{company_id}_{project_id}"
        
        if key not in self._drawings:
            self._drawings[key] = []
        
        # Check for previous revisions
        previous = [d for d in self._drawings[key] if d.drawing_name.lower() == drawing_name.lower()]
        
        # Add new revision
        new_revision = DrawingRevision(
            drawing_name=drawing_name,
            revision=revision,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.utcnow(),
            changes=changes,
            file_path=file_path,
        )
        self._drawings[key].append(new_revision)
        
        # Store in memory
        await memory_service.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=f"Drawing: {drawing_name}, Revision: {revision}, Changes: {changes or 'Not specified'}, Uploaded by: {uploaded_by}",
            memory_type="drawing",
            metadata={
                "drawing_name": drawing_name,
                "revision": revision,
                "uploaded_by": uploaded_by,
            },
            user_id=uploaded_by,
        )
        
        logger.info(f"📐 Drawing logged: {drawing_name} {revision}")
        
        return {
            "drawing_name": drawing_name,
            "revision": revision,
            "previous_count": len(previous),
            "previous_revisions": [{"revision": p.revision, "date": p.uploaded_at.isoformat()} for p in previous[-3:]],
        }
    
    def get_latest_revision(
        self,
        company_id: str,
        project_id: str,
        drawing_name: str,
    ) -> Optional[DrawingRevision]:
        """Get latest revision of a drawing"""
        key = f"{company_id}_{project_id}"
        
        if key not in self._drawings:
            return None
        
        matches = [d for d in self._drawings[key] if d.drawing_name.lower() == drawing_name.lower()]
        
        if not matches:
            return None
        
        # Sort by upload date, return latest
        matches.sort(key=lambda x: x.uploaded_at, reverse=True)
        return matches[0]
    
    def get_drawing_history(
        self,
        company_id: str,
        project_id: str,
        drawing_name: str,
    ) -> List[DrawingRevision]:
        """Get full revision history of a drawing"""
        key = f"{company_id}_{project_id}"
        
        if key not in self._drawings:
            return []
        
        matches = [d for d in self._drawings[key] if d.drawing_name.lower() == drawing_name.lower()]
        matches.sort(key=lambda x: x.uploaded_at, reverse=True)
        return matches
    
    # =========================================================================
    # DECISIONS
    # =========================================================================
    
    async def log_decision(
        self,
        company_id: str,
        project_id: str,
        decision_text: str,
        approved_by: str,
        context: str = None,
    ) -> Decision:
        """Log a decision"""
        key = f"{company_id}_{project_id}"
        
        if key not in self._decisions:
            self._decisions[key] = []
        
        decision = Decision(
            id=f"DEC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=decision_text,
            approved_by=approved_by,
            approved_at=datetime.utcnow(),
            project_id=project_id,
            context=context,
        )
        
        self._decisions[key].append(decision)
        
        # Store in memory
        await memory_service.add_decision(
            company_id=company_id,
            project_id=project_id,
            decision=decision_text,
            approved_by=approved_by,
            user_id=approved_by,
        )
        
        logger.info(f"✅ Decision logged: {decision.id}")
        
        return decision
    
    def get_decisions(
        self,
        company_id: str,
        project_id: str,
        limit: int = 50,
    ) -> List[Decision]:
        """Get recent decisions"""
        key = f"{company_id}_{project_id}"
        
        if key not in self._decisions:
            return []
        
        decisions = self._decisions[key]
        decisions.sort(key=lambda x: x.approved_at, reverse=True)
        return decisions[:limit]
    
    # =========================================================================
    # RFIs
    # =========================================================================
    
    async def log_rfi(
        self,
        company_id: str,
        project_id: str,
        description: str,
        raised_by: str,
        assigned_to: str,
    ) -> RFI:
        """Log an RFI"""
        key = f"{company_id}_{project_id}"
        
        if key not in self._rfis:
            self._rfis[key] = []
        
        rfi = RFI(
            id=f"RFI-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            description=description,
            raised_by=raised_by,
            assigned_to=assigned_to,
            raised_at=datetime.utcnow(),
        )
        
        self._rfis[key].append(rfi)
        
        # Store in memory
        await memory_service.add_memory(
            company_id=company_id,
            project_id=project_id,
            content=f"RFI: {description}, Raised by: {raised_by}, Assigned to: {assigned_to}",
            memory_type="rfi",
            metadata={
                "rfi_id": rfi.id,
                "status": "open",
                "assigned_to": assigned_to,
            },
            user_id=raised_by,
        )
        
        logger.info(f"📋 RFI logged: {rfi.id}")
        
        return rfi
    
    def get_open_rfis(
        self,
        company_id: str,
        project_id: str,
    ) -> List[RFI]:
        """Get open RFIs"""
        key = f"{company_id}_{project_id}"
        
        if key not in self._rfis:
            return []
        
        return [r for r in self._rfis[key] if r.status == "open"]
    
    def get_overdue_rfis(
        self,
        company_id: str,
        project_id: str,
        days_threshold: int = 3,
    ) -> List[RFI]:
        """Get RFIs that are overdue"""
        key = f"{company_id}_{project_id}"
        
        if key not in self._rfis:
            return []
        
        now = datetime.utcnow()
        overdue = []
        
        for rfi in self._rfis[key]:
            if rfi.status == "open":
                days_open = (now - rfi.raised_at).days
                if days_open >= days_threshold:
                    overdue.append(rfi)
        
        return overdue
    
    async def respond_to_rfi(
        self,
        company_id: str,
        project_id: str,
        rfi_id: str,
        response: str,
    ) -> Optional[RFI]:
        """Mark an RFI as responded"""
        key = f"{company_id}_{project_id}"
        
        if key not in self._rfis:
            return None
        
        for rfi in self._rfis[key]:
            if rfi.id == rfi_id:
                rfi.response = response
                rfi.responded_at = datetime.utcnow()
                rfi.status = "responded"
                return rfi
        
        return None
    
    # =========================================================================
    # STATS FOR DASHBOARD
    # =========================================================================
    
    def get_project_stats(
        self,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """Get stats for a project"""
        key = f"{company_id}_{project_id}"
        
        drawings = self._drawings.get(key, [])
        decisions = self._decisions.get(key, [])
        rfis = self._rfis.get(key, [])
        
        open_rfis = [r for r in rfis if r.status == "open"]
        overdue_rfis = self.get_overdue_rfis(company_id, project_id)
        
        return {
            "drawings_count": len(drawings),
            "decisions_count": len(decisions),
            "total_rfis": len(rfis),
            "open_rfis": len(open_rfis),
            "overdue_rfis": len(overdue_rfis),
        }
    
    def get_company_stats(
        self,
        company_id: str,
    ) -> Dict[str, Any]:
        """Get aggregate stats for a company"""
        total_drawings = 0
        total_decisions = 0
        total_rfis = 0
        open_rfis = 0
        
        for key in self._drawings:
            if key.startswith(company_id):
                total_drawings += len(self._drawings[key])
        
        for key in self._decisions:
            if key.startswith(company_id):
                total_decisions += len(self._decisions[key])
        
        for key in self._rfis:
            if key.startswith(company_id):
                total_rfis += len(self._rfis[key])
                open_rfis += len([r for r in self._rfis[key] if r.status == "open"])
        
        return {
            "total_drawings": total_drawings,
            "total_decisions": total_decisions,
            "total_rfis": total_rfis,
            "open_rfis": open_rfis,
        }
    
    # =========================================================================
    # LEGACY COMPATIBILITY (for dashboard)
    # =========================================================================
    
    def get_value_protected(
        self,
        company_id: str,
        project_id: str = None,
    ) -> Dict[str, Any]:
        """
        Calculate estimated value protected
        
        This is a SOFT estimate based on:
        - Drawings tracked (prevent wrong revision)
        - Decisions logged (prevent disputes)
        - RFIs resolved (prevent delays)
        
        NOT based on risky "AI detection" claims
        """
        stats = self.get_company_stats(company_id) if not project_id else self.get_project_stats(company_id, project_id)
        
        # Conservative estimates
        value_per_drawing_tracked = 10000  # ₹10K potential save per drawing tracked
        value_per_decision_logged = 25000  # ₹25K potential save per decision logged
        value_per_rfi_tracked = 50000  # ₹50K potential save per RFI tracked
        
        estimated_value = (
            stats.get("total_drawings", stats.get("drawings_count", 0)) * value_per_drawing_tracked +
            stats.get("total_decisions", stats.get("decisions_count", 0)) * value_per_decision_logged +
            stats.get("total_rfis", 0) * value_per_rfi_tracked
        )
        
        return {
            "total_value_protected_lakh": estimated_value / 100000,
            "drawings_tracked": stats.get("total_drawings", stats.get("drawings_count", 0)),
            "decisions_logged": stats.get("total_decisions", stats.get("decisions_count", 0)),
            "rfis_tracked": stats.get("total_rfis", 0),
            "calculation_note": "Estimated based on industry-average cost of revision errors, decision disputes, and RFI delays",
        }


# Singleton
connected_intelligence = ConnectedIntelligence()
