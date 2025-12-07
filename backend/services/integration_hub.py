"""
SiteMind Integration Hub
Connect with existing enterprise systems

SUPPORTED INTEGRATIONS:
1. Cloud Storage - Google Drive, OneDrive, Dropbox
2. ERP Systems - SAP, Tally, Zoho
3. Project Management - Primavera, MS Project
4. Communication - Email (IMAP), Slack
5. CAD Systems - AutoCAD (read-only)

ARCHITECTURE:
- Each integration has: connect, sync, webhook
- All data flows TO SiteMind (we're the central brain)
- Changes in external systems trigger SiteMind updates
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

from utils.logger import logger


class IntegrationType(str, Enum):
    GOOGLE_DRIVE = "google_drive"
    ONEDRIVE = "onedrive"
    DROPBOX = "dropbox"
    SAP = "sap"
    TALLY = "tally"
    ZOHO = "zoho"
    PRIMAVERA = "primavera"
    MS_PROJECT = "ms_project"
    EMAIL = "email"
    SLACK = "slack"


class IntegrationStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    PENDING_AUTH = "pending_auth"


class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.status = IntegrationStatus.PENDING_AUTH
        self.last_sync: Optional[datetime] = None
        self.last_error: Optional[str] = None
    
    @abstractmethod
    async def connect(self, credentials: Dict) -> bool:
        """Establish connection to external system"""
        pass
    
    @abstractmethod
    async def sync(self) -> Dict[str, Any]:
        """Sync data from external system"""
        pass
    
    @abstractmethod
    async def handle_webhook(self, payload: Dict) -> Dict[str, Any]:
        """Handle webhook from external system"""
        pass


class GoogleDriveIntegration(BaseIntegration):
    """
    Google Drive Integration
    
    - Auto-sync drawing folders
    - Detect new/modified files
    - Import to SiteMind
    """
    
    async def connect(self, credentials: Dict) -> bool:
        """Connect using OAuth tokens"""
        # Would use Google APIs
        logger.info("🔗 Google Drive: Connecting...")
        self.status = IntegrationStatus.ACTIVE
        return True
    
    async def sync(self) -> Dict[str, Any]:
        """Sync drawings from configured folder"""
        logger.info("🔄 Google Drive: Syncing...")
        
        # Would:
        # 1. List files modified since last sync
        # 2. Download new/modified files
        # 3. Process through SiteMind
        # 4. Update last_sync timestamp
        
        self.last_sync = datetime.utcnow()
        
        return {
            "files_found": 0,
            "files_imported": 0,
            "errors": [],
        }
    
    async def handle_webhook(self, payload: Dict) -> Dict[str, Any]:
        """Handle Google Drive change notification"""
        # Would process file change notifications
        return {"processed": True}
    
    def get_auth_url(self, redirect_uri: str) -> str:
        """Generate OAuth URL for user authorization"""
        # Would generate Google OAuth URL
        return f"https://accounts.google.com/oauth2/auth?redirect_uri={redirect_uri}"


class OneDriveIntegration(BaseIntegration):
    """OneDrive/SharePoint Integration"""
    
    async def connect(self, credentials: Dict) -> bool:
        logger.info("🔗 OneDrive: Connecting...")
        self.status = IntegrationStatus.ACTIVE
        return True
    
    async def sync(self) -> Dict[str, Any]:
        logger.info("🔄 OneDrive: Syncing...")
        self.last_sync = datetime.utcnow()
        return {"files_found": 0, "files_imported": 0}
    
    async def handle_webhook(self, payload: Dict) -> Dict[str, Any]:
        return {"processed": True}


class ERPIntegration(BaseIntegration):
    """
    ERP Integration (SAP, Tally, Zoho)
    
    - Pull BOQ data
    - Sync material master
    - Push consumption data
    - Cost tracking
    """
    
    def __init__(self, config: Dict[str, Any], erp_type: str):
        super().__init__(config)
        self.erp_type = erp_type
    
    async def connect(self, credentials: Dict) -> bool:
        logger.info(f"🔗 {self.erp_type}: Connecting...")
        self.status = IntegrationStatus.ACTIVE
        return True
    
    async def sync(self) -> Dict[str, Any]:
        """Sync data from ERP"""
        logger.info(f"🔄 {self.erp_type}: Syncing...")
        
        # Would:
        # 1. Pull BOQ items
        # 2. Sync material master
        # 3. Get latest rates
        # 4. Update SiteMind inventory
        
        self.last_sync = datetime.utcnow()
        
        return {
            "boq_items_synced": 0,
            "materials_synced": 0,
            "rates_updated": 0,
        }
    
    async def handle_webhook(self, payload: Dict) -> Dict[str, Any]:
        return {"processed": True}
    
    async def push_consumption(self, consumption_data: List[Dict]) -> bool:
        """Push consumption data back to ERP"""
        logger.info(f"📤 {self.erp_type}: Pushing consumption data...")
        # Would send consumption records to ERP
        return True


class ProjectManagementIntegration(BaseIntegration):
    """
    Project Management Integration (Primavera, MS Project)
    
    - Sync milestones
    - Update progress
    - Get baseline schedule
    """
    
    def __init__(self, config: Dict[str, Any], pm_type: str):
        super().__init__(config)
        self.pm_type = pm_type
    
    async def connect(self, credentials: Dict) -> bool:
        logger.info(f"🔗 {self.pm_type}: Connecting...")
        self.status = IntegrationStatus.ACTIVE
        return True
    
    async def sync(self) -> Dict[str, Any]:
        """Sync schedule data"""
        logger.info(f"🔄 {self.pm_type}: Syncing milestones...")
        
        # Would:
        # 1. Pull milestone schedule
        # 2. Update SiteMind milestones
        # 3. Calculate variances
        
        self.last_sync = datetime.utcnow()
        
        return {
            "milestones_synced": 0,
            "schedule_updated": True,
        }
    
    async def handle_webhook(self, payload: Dict) -> Dict[str, Any]:
        return {"processed": True}
    
    async def push_progress(self, progress_data: Dict) -> bool:
        """Push progress updates to PM system"""
        logger.info(f"📤 {self.pm_type}: Pushing progress...")
        return True


class IntegrationHub:
    """
    Central hub for managing all integrations
    """
    
    def __init__(self):
        self._integrations: Dict[str, Dict[str, BaseIntegration]] = {}
    
    def register_integration(
        self,
        organization_id: str,
        integration_type: IntegrationType,
        config: Dict[str, Any],
    ) -> BaseIntegration:
        """Register a new integration"""
        
        integration: BaseIntegration
        
        if integration_type == IntegrationType.GOOGLE_DRIVE:
            integration = GoogleDriveIntegration(config)
        elif integration_type == IntegrationType.ONEDRIVE:
            integration = OneDriveIntegration(config)
        elif integration_type in [IntegrationType.SAP, IntegrationType.TALLY, IntegrationType.ZOHO]:
            integration = ERPIntegration(config, integration_type.value)
        elif integration_type in [IntegrationType.PRIMAVERA, IntegrationType.MS_PROJECT]:
            integration = ProjectManagementIntegration(config, integration_type.value)
        else:
            raise ValueError(f"Unsupported integration type: {integration_type}")
        
        if organization_id not in self._integrations:
            self._integrations[organization_id] = {}
        
        self._integrations[organization_id][integration_type.value] = integration
        
        logger.info(f"✅ Integration registered: {integration_type.value} for org {organization_id}")
        
        return integration
    
    def get_integration(
        self,
        organization_id: str,
        integration_type: IntegrationType,
    ) -> Optional[BaseIntegration]:
        """Get a registered integration"""
        return self._integrations.get(organization_id, {}).get(integration_type.value)
    
    def list_integrations(self, organization_id: str) -> List[Dict]:
        """List all integrations for an organization"""
        integrations = self._integrations.get(organization_id, {})
        
        return [
            {
                "type": int_type,
                "status": integration.status.value,
                "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
                "last_error": integration.last_error,
            }
            for int_type, integration in integrations.items()
        ]
    
    async def sync_all(self, organization_id: str) -> Dict[str, Any]:
        """Sync all active integrations"""
        integrations = self._integrations.get(organization_id, {})
        results = {}
        
        for int_type, integration in integrations.items():
            if integration.status == IntegrationStatus.ACTIVE:
                try:
                    results[int_type] = await integration.sync()
                except Exception as e:
                    integration.status = IntegrationStatus.ERROR
                    integration.last_error = str(e)
                    results[int_type] = {"error": str(e)}
        
        return results
    
    # =========================================================================
    # INTEGRATION GUIDES
    # =========================================================================
    
    def get_setup_instructions(self, integration_type: IntegrationType) -> str:
        """Get setup instructions for an integration"""
        
        instructions = {
            IntegrationType.GOOGLE_DRIVE: """
**Google Drive Integration Setup**

1. Go to SiteMind Dashboard → Settings → Integrations
2. Click "Connect Google Drive"
3. Sign in with your Google account
4. Select the folder containing project drawings
5. SiteMind will auto-sync any new/modified files

**Folder Structure (Recommended):**
```
Project_Drawings/
├── Structural/
├── Architectural/
├── MEP/
└── Shop_Drawings/
```

Changes in these folders automatically appear in SiteMind.
""",
            IntegrationType.SAP: """
**SAP Integration Setup**

1. Contact your SAP administrator
2. Request API credentials for SiteMind
3. Provide these in Dashboard → Settings → Integrations
4. Configure sync: BOQ, Materials, Rates

**Data Flow:**
- SAP → SiteMind: BOQ, Material Master, Rates
- SiteMind → SAP: Consumption records (optional)
""",
            IntegrationType.PRIMAVERA: """
**Primavera P6 Integration Setup**

1. Export schedule baseline from P6
2. Upload to SiteMind or configure API connection
3. SiteMind will track actual vs planned

**Sync Options:**
- One-time import (upload XML)
- API sync (requires P6 Cloud)
- Manual update via dashboard
""",
        }
        
        return instructions.get(
            integration_type,
            "Contact support@sitemind.ai for integration setup assistance."
        )


# Singleton instance
integration_hub = IntegrationHub()

