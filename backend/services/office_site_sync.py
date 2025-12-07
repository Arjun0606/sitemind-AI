"""
SiteMind Office-Site Sync Service
Real-time communication between office and site

FEATURES:
- Drawing update notifications
- Change order broadcasts
- RFI routing
- Daily status sync
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SyncUpdate:
    id: str
    project_id: str
    update_type: str  # drawing, change_order, rfi, announcement
    title: str
    content: str
    from_user: str
    from_location: str  # office, site
    created_at: str
    acknowledged_by: List[str]


class OfficeSiteSyncService:
    """
    Keep office and site in sync
    """
    
    def __init__(self):
        self._updates: Dict[str, List[SyncUpdate]] = {}  # project_id -> updates
        self._pending_acks: Dict[str, List[str]] = {}  # update_id -> user_phones pending
    
    # =========================================================================
    # UPDATES
    # =========================================================================
    
    def broadcast_update(
        self,
        project_id: str,
        update_type: str,
        title: str,
        content: str,
        from_user: str,
        from_location: str = "office",
        required_acks: List[str] = None,
    ) -> SyncUpdate:
        """Broadcast an update to all team members"""
        update = SyncUpdate(
            id=f"sync_{datetime.utcnow().timestamp():.0f}",
            project_id=project_id,
            update_type=update_type,
            title=title,
            content=content,
            from_user=from_user,
            from_location=from_location,
            created_at=datetime.utcnow().isoformat(),
            acknowledged_by=[],
        )
        
        if project_id not in self._updates:
            self._updates[project_id] = []
        self._updates[project_id].append(update)
        
        if required_acks:
            self._pending_acks[update.id] = required_acks.copy()
        
        return update
    
    def acknowledge_update(
        self,
        update_id: str,
        user_phone: str,
    ) -> bool:
        """Acknowledge receipt of an update"""
        # Find the update
        for updates in self._updates.values():
            for update in updates:
                if update.id == update_id:
                    if user_phone not in update.acknowledged_by:
                        update.acknowledged_by.append(user_phone)
                    
                    # Remove from pending
                    if update_id in self._pending_acks:
                        if user_phone in self._pending_acks[update_id]:
                            self._pending_acks[update_id].remove(user_phone)
                    
                    return True
        
        return False
    
    # =========================================================================
    # SPECIFIC UPDATE TYPES
    # =========================================================================
    
    def track_drawing_upload(
        self,
        project_id: str,
        drawing_name: str,
        uploaded_by: str,
    ) -> SyncUpdate:
        """Track a new drawing upload"""
        return self.broadcast_update(
            project_id=project_id,
            update_type="drawing",
            title=f"New Drawing: {drawing_name}",
            content=f"A new drawing has been uploaded by {uploaded_by}. Please review and acknowledge.",
            from_user=uploaded_by,
            from_location="office",
        )
    
    def track_change_order(
        self,
        project_id: str,
        description: str,
        affected_area: str,
        issued_by: str,
    ) -> SyncUpdate:
        """Track a change order"""
        return self.broadcast_update(
            project_id=project_id,
            update_type="change_order",
            title=f"Change Order: {affected_area}",
            content=f"{description}\n\nIssued by: {issued_by}",
            from_user=issued_by,
            from_location="office",
        )
    
    def track_site_report(
        self,
        project_id: str,
        report_content: str,
        reported_by: str,
    ) -> SyncUpdate:
        """Track a site report"""
        return self.broadcast_update(
            project_id=project_id,
            update_type="site_report",
            title="Daily Site Report",
            content=report_content,
            from_user=reported_by,
            from_location="site",
        )
    
    # =========================================================================
    # QUERIES
    # =========================================================================
    
    def get_pending_updates(
        self,
        project_id: str,
        user_phone: str,
    ) -> List[SyncUpdate]:
        """Get updates not yet acknowledged by user"""
        updates = self._updates.get(project_id, [])
        
        pending = [
            u for u in updates 
            if user_phone not in u.acknowledged_by
        ]
        
        return sorted(pending, key=lambda x: x.created_at, reverse=True)
    
    def get_pending_acknowledgments(
        self,
        update_id: str,
    ) -> List[str]:
        """Get list of users who haven't acknowledged"""
        return self._pending_acks.get(update_id, [])
    
    def format_update_notification(self, update: SyncUpdate) -> str:
        """Format update for WhatsApp notification"""
        icons = {
            "drawing": "📐",
            "change_order": "📝",
            "rfi": "❓",
            "announcement": "📢",
            "site_report": "📋",
        }
        
        icon = icons.get(update.update_type, "ℹ️")
        
        return f"""{icon} **{update.title}**

{update.content}

From: {update.from_user} ({update.from_location})
Time: {update.created_at[:16]}

_Reply 'ack' to acknowledge._"""
    
    def get_sync_status(self, project_id: str) -> str:
        """Get sync status for project"""
        updates = self._updates.get(project_id, [])
        
        # Count unacknowledged
        total_unack = sum(
            len(self._pending_acks.get(u.id, [])) 
            for u in updates[-10:]  # Last 10 updates
        )
        
        recent = updates[-5:] if updates else []
        
        if not updates:
            return "No sync updates yet."
        
        status = f"**Sync Status**\n\n"
        status += f"• Recent updates: {len(recent)}\n"
        status += f"• Pending acknowledgments: {total_unack}\n\n"
        
        if recent:
            status += "**Recent:**\n"
            for u in recent[:3]:
                ack_count = len(u.acknowledged_by)
                status += f"• {u.title[:30]}... ({ack_count} acks)\n"
        
        return status


# Singleton instance
office_site_sync = OfficeSiteSyncService()
