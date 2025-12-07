"""
SiteMind Office-Site Sync Service
Bridges the communication gap between office and construction site

PROBLEMS SOLVED:
1. Drawings sent but not received → Track acknowledgment
2. Decisions made but not communicated → Auto-notify affected parties
3. Site updates not reaching office → Real-time sync
4. Different versions being used → Version control alerts
5. Verbal instructions lost → Everything documented

FEATURES:
- Drawing distribution tracking
- Decision propagation
- Real-time activity feed
- Version synchronization
- Communication logging
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from utils.logger import logger


class SyncItemType(str, Enum):
    DRAWING = "drawing"
    CHANGE_ORDER = "change_order"
    RFI = "rfi"
    DECISION = "decision"
    INSTRUCTION = "instruction"
    ALERT = "alert"


class AcknowledgmentStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    SEEN = "seen"
    ACKNOWLEDGED = "acknowledged"


@dataclass
class SyncItem:
    """An item to be synced between office and site"""
    item_id: str
    project_id: str
    item_type: SyncItemType
    title: str
    content: str
    source: str  # "office" or "site"
    created_by: str
    created_at: str
    target_recipients: List[str]  # Phone numbers
    acknowledgments: Dict[str, AcknowledgmentStatus] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    priority: str = "normal"  # normal, high, urgent


class OfficeSiteSyncService:
    """
    Keeps office and site in perfect sync
    """
    
    def __init__(self):
        self._sync_items: Dict[str, List[SyncItem]] = {}
        self._user_roles: Dict[str, str] = {}  # phone -> role (office/site/pm)
        self._project_teams: Dict[str, Dict[str, List[str]]] = {}
    
    # =========================================================================
    # TEAM MANAGEMENT
    # =========================================================================
    
    def register_team_member(
        self,
        project_id: str,
        phone: str,
        name: str,
        role: str,  # office, site_engineer, pm, consultant
    ):
        """Register a team member for sync notifications"""
        if project_id not in self._project_teams:
            self._project_teams[project_id] = {
                "office": [],
                "site_engineer": [],
                "pm": [],
                "consultant": [],
            }
        
        if role in self._project_teams[project_id]:
            self._project_teams[project_id][role].append(phone)
        
        self._user_roles[phone] = role
    
    def get_team_by_role(self, project_id: str, role: str) -> List[str]:
        """Get team members by role"""
        return self._project_teams.get(project_id, {}).get(role, [])
    
    # =========================================================================
    # SYNC OPERATIONS
    # =========================================================================
    
    def create_sync_item(
        self,
        project_id: str,
        item_type: SyncItemType,
        title: str,
        content: str,
        created_by: str,
        target_roles: List[str] = None,
        target_phones: List[str] = None,
        priority: str = "normal",
        attachments: List[str] = None,
    ) -> SyncItem:
        """
        Create a new sync item to be distributed
        
        Example: Drawing uploaded by office → notify all site engineers
        """
        # Determine recipients
        recipients = []
        if target_phones:
            recipients.extend(target_phones)
        if target_roles:
            for role in target_roles:
                recipients.extend(self.get_team_by_role(project_id, role))
        
        # Remove duplicates
        recipients = list(set(recipients))
        
        # Determine source
        creator_role = self._user_roles.get(created_by, "unknown")
        source = "office" if creator_role in ["office", "pm"] else "site"
        
        item = SyncItem(
            item_id=f"sync_{int(datetime.utcnow().timestamp() * 1000)}",
            project_id=project_id,
            item_type=item_type,
            title=title,
            content=content,
            source=source,
            created_by=created_by,
            created_at=datetime.utcnow().isoformat(),
            target_recipients=recipients,
            acknowledgments={phone: AcknowledgmentStatus.PENDING for phone in recipients},
            attachments=attachments or [],
            priority=priority,
        )
        
        if project_id not in self._sync_items:
            self._sync_items[project_id] = []
        
        self._sync_items[project_id].append(item)
        
        logger.info(f"📤 Sync item created: {title} → {len(recipients)} recipients")
        
        return item
    
    def sync_drawing_upload(
        self,
        project_id: str,
        drawing_name: str,
        drawing_url: str,
        uploaded_by: str,
        revision: str = None,
        notes: str = None,
    ) -> SyncItem:
        """
        Sync a new drawing upload to all site engineers
        """
        content = f"New drawing uploaded: {drawing_name}"
        if revision:
            content += f" (Revision: {revision})"
        if notes:
            content += f"\n\nNotes: {notes}"
        
        content += "\n\nPlease acknowledge receipt."
        
        return self.create_sync_item(
            project_id=project_id,
            item_type=SyncItemType.DRAWING,
            title=f"📐 New Drawing: {drawing_name}",
            content=content,
            created_by=uploaded_by,
            target_roles=["site_engineer", "pm"],
            priority="high",
            attachments=[drawing_url],
        )
    
    def sync_change_order(
        self,
        project_id: str,
        change_description: str,
        affected_area: str,
        created_by: str,
    ) -> SyncItem:
        """
        Sync a change order to all affected parties
        """
        content = f"""Change Order Issued

**Affected Area:** {affected_area}

**Change:** {change_description}

Please confirm you have received and understood this change.
Reply 'acknowledged' to confirm."""
        
        return self.create_sync_item(
            project_id=project_id,
            item_type=SyncItemType.CHANGE_ORDER,
            title=f"🔄 Change Order: {affected_area}",
            content=content,
            created_by=created_by,
            target_roles=["site_engineer", "pm"],
            priority="urgent",
        )
    
    def sync_decision(
        self,
        project_id: str,
        decision: str,
        context: str,
        decided_by: str,
        affected_roles: List[str] = None,
    ) -> SyncItem:
        """
        Sync a decision to relevant parties
        """
        content = f"""Decision Recorded

**Decision:** {decision}

**Context:** {context}

**Decided by:** {decided_by}

This decision is now part of the project record."""
        
        return self.create_sync_item(
            project_id=project_id,
            item_type=SyncItemType.DECISION,
            title=f"✅ Decision: {decision[:50]}...",
            content=content,
            created_by=decided_by,
            target_roles=affected_roles or ["site_engineer", "pm", "office"],
            priority="normal",
        )
    
    # =========================================================================
    # ACKNOWLEDGMENT TRACKING
    # =========================================================================
    
    def record_acknowledgment(
        self,
        item_id: str,
        phone: str,
        status: AcknowledgmentStatus = AcknowledgmentStatus.ACKNOWLEDGED,
    ) -> bool:
        """Record that someone has acknowledged a sync item"""
        for project_items in self._sync_items.values():
            for item in project_items:
                if item.item_id == item_id and phone in item.acknowledgments:
                    item.acknowledgments[phone] = status
                    logger.info(f"✅ Acknowledgment recorded: {phone} → {item.title}")
                    return True
        return False
    
    def get_pending_acknowledgments(self, project_id: str) -> List[Dict]:
        """Get items with pending acknowledgments"""
        items = self._sync_items.get(project_id, [])
        pending = []
        
        for item in items:
            pending_phones = [
                phone for phone, status in item.acknowledgments.items()
                if status == AcknowledgmentStatus.PENDING
            ]
            if pending_phones:
                pending.append({
                    "item": item,
                    "pending_from": pending_phones,
                    "pending_count": len(pending_phones),
                })
        
        return pending
    
    def get_user_pending_items(self, phone: str) -> List[SyncItem]:
        """Get items pending acknowledgment from a specific user"""
        pending = []
        
        for project_items in self._sync_items.values():
            for item in project_items:
                if phone in item.acknowledgments:
                    if item.acknowledgments[phone] == AcknowledgmentStatus.PENDING:
                        pending.append(item)
        
        return pending
    
    # =========================================================================
    # ACTIVITY FEED
    # =========================================================================
    
    def get_activity_feed(
        self,
        project_id: str,
        limit: int = 20,
        source_filter: str = None,  # "office", "site", or None for all
    ) -> List[Dict]:
        """
        Get recent activity feed for project
        
        Useful for dashboard showing what's happening
        """
        items = self._sync_items.get(project_id, [])
        
        if source_filter:
            items = [i for i in items if i.source == source_filter]
        
        # Sort by date, most recent first
        items.sort(key=lambda x: x.created_at, reverse=True)
        
        feed = []
        for item in items[:limit]:
            ack_count = sum(1 for s in item.acknowledgments.values() 
                          if s == AcknowledgmentStatus.ACKNOWLEDGED)
            total = len(item.acknowledgments)
            
            feed.append({
                "item_id": item.item_id,
                "type": item.item_type.value,
                "title": item.title,
                "source": item.source,
                "created_by": item.created_by,
                "created_at": item.created_at,
                "priority": item.priority,
                "acknowledgment_status": f"{ack_count}/{total}",
                "fully_acknowledged": ack_count == total,
            })
        
        return feed
    
    # =========================================================================
    # SYNC STATUS REPORTS
    # =========================================================================
    
    def generate_sync_report(self, project_id: str) -> str:
        """Generate sync status report"""
        items = self._sync_items.get(project_id, [])
        
        # Stats
        total_items = len(items)
        office_to_site = len([i for i in items if i.source == "office"])
        site_to_office = len([i for i in items if i.source == "site"])
        
        pending = self.get_pending_acknowledgments(project_id)
        urgent_pending = [p for p in pending if p["item"].priority == "urgent"]
        
        report = f"""
**Office-Site Sync Status**

Total Items Synced: {total_items}
• Office → Site: {office_to_site}
• Site → Office: {site_to_office}

Pending Acknowledgments: {len(pending)}
"""
        
        if urgent_pending:
            report += f"\n⚠️ URGENT items pending acknowledgment: {len(urgent_pending)}"
            for p in urgent_pending[:3]:
                report += f"\n  • {p['item'].title} ({p['pending_count']} pending)"
        
        return report


# Singleton instance
office_site_sync = OfficeSiteSyncService()

