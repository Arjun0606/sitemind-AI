"""
SiteMind Configuration Service
Modular config system - all customization through config, not code

DESIGN PRINCIPLES:
1. Every feature is toggleable per org/project/user
2. All settings have sensible defaults
3. Inheritance: User < Project < Organization < System defaults
4. Config changes don't require restarts
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from copy import deepcopy

from utils.logger import logger


# =============================================================================
# DEFAULT CONFIGURATIONS
# =============================================================================

SYSTEM_DEFAULTS = {
    # Organization defaults
    "organization": {
        "plan": "pilot",
        "max_sites": 3,
        "max_users_per_site": 50,
        "storage_gb": 100,
        
        "language": "hinglish",
        "timezone": "Asia/Kolkata",
        "ai_response_style": "professional",
        
        "morning_brief_enabled": True,
        "morning_brief_time": "07:00",
        
        "features": {
            "red_flags": True,
            "task_management": True,
            "material_tracking": True,
            "progress_photos": True,
            "office_site_sync": True,
            "integrations": True,
            "advanced_analytics": False,
            "custom_reports": False,
            "api_access": False,
        },
        
        "branding": {
            "assistant_name": "SiteMind",
            "logo_url": None,
            "primary_color": "#2563eb",
        },
        
        "notifications": {
            "email_reports": True,
            "whatsapp_alerts": True,
            "dashboard_notifications": True,
        },
    },
    
    # Project defaults
    "project": {
        "disciplines": ["structural", "architectural", "mep"],
        "grid_system": "alphanumeric",
        "floor_naming": "numeric",
        
        "notifications": {
            "morning_brief_recipients": ["pm", "owner"],
            "red_flag_recipients": ["pm", "owner"],
            "daily_summary_recipients": ["pm"],
            "weekly_report_recipients": ["pm", "owner"],
        },
        
        "ai_config": {
            "include_drawing_references": True,
            "include_revision_warnings": True,
            "safety_emphasis": "high",
            "response_length": "medium",
        },
        
        "enable_material_tracking": True,
        "enable_task_management": True,
        "enable_progress_photos": True,
    },
    
    # User defaults by role
    "user_by_role": {
        "owner": {
            "permissions": {
                "can_query": True,
                "can_upload_documents": True,
                "can_upload_photos": True,
                "can_create_tasks": True,
                "can_assign_tasks": True,
                "can_view_reports": True,
                "can_manage_team": True,
                "can_manage_billing": True,
                "can_access_dashboard": True,
                "can_record_materials": True,
                "can_approve_changes": True,
            },
            "notifications": {
                "morning_brief": True,
                "red_flags": True,
                "weekly_reports": True,
                "task_updates": False,
            },
        },
        "admin": {
            "permissions": {
                "can_query": True,
                "can_upload_documents": True,
                "can_upload_photos": True,
                "can_create_tasks": True,
                "can_assign_tasks": True,
                "can_view_reports": True,
                "can_manage_team": True,
                "can_manage_billing": False,
                "can_access_dashboard": True,
                "can_record_materials": True,
                "can_approve_changes": True,
            },
            "notifications": {
                "morning_brief": True,
                "red_flags": True,
                "weekly_reports": True,
                "task_updates": True,
            },
        },
        "pm": {
            "permissions": {
                "can_query": True,
                "can_upload_documents": True,
                "can_upload_photos": True,
                "can_create_tasks": True,
                "can_assign_tasks": True,
                "can_view_reports": True,
                "can_manage_team": False,
                "can_manage_billing": False,
                "can_access_dashboard": True,
                "can_record_materials": True,
                "can_approve_changes": False,
            },
            "notifications": {
                "morning_brief": True,
                "red_flags": True,
                "weekly_reports": True,
                "task_updates": True,
            },
        },
        "site_engineer": {
            "permissions": {
                "can_query": True,
                "can_upload_documents": False,
                "can_upload_photos": True,
                "can_create_tasks": False,
                "can_assign_tasks": False,
                "can_view_reports": False,
                "can_manage_team": False,
                "can_manage_billing": False,
                "can_access_dashboard": False,
                "can_record_materials": True,
                "can_approve_changes": False,
            },
            "notifications": {
                "morning_brief": False,
                "red_flags": False,
                "weekly_reports": False,
                "task_updates": True,
            },
        },
        "consultant": {
            "permissions": {
                "can_query": True,
                "can_upload_documents": True,
                "can_upload_photos": False,
                "can_create_tasks": False,
                "can_assign_tasks": False,
                "can_view_reports": True,
                "can_manage_team": False,
                "can_manage_billing": False,
                "can_access_dashboard": True,
                "can_record_materials": False,
                "can_approve_changes": False,
            },
            "notifications": {
                "morning_brief": False,
                "red_flags": False,
                "weekly_reports": True,
                "task_updates": False,
            },
        },
        "viewer": {
            "permissions": {
                "can_query": True,
                "can_upload_documents": False,
                "can_upload_photos": False,
                "can_create_tasks": False,
                "can_assign_tasks": False,
                "can_view_reports": True,
                "can_manage_team": False,
                "can_manage_billing": False,
                "can_access_dashboard": True,
                "can_record_materials": False,
                "can_approve_changes": False,
            },
            "notifications": {
                "morning_brief": False,
                "red_flags": False,
                "weekly_reports": True,
                "task_updates": False,
            },
        },
    },
}


class ConfigService:
    """
    Manages configuration for organizations, projects, and users
    """
    
    def __init__(self):
        # In production, these would be loaded from database
        self._org_configs: Dict[str, Dict] = {}
        self._project_configs: Dict[str, Dict] = {}
        self._user_configs: Dict[str, Dict] = {}
    
    # =========================================================================
    # CONFIG RESOLUTION (with inheritance)
    # =========================================================================
    
    def get_effective_config(
        self,
        organization_id: str,
        project_id: str = None,
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Get the effective configuration with inheritance applied
        
        Order: System Defaults → Organization → Project → User
        """
        # Start with system defaults
        config = deepcopy(SYSTEM_DEFAULTS["organization"])
        
        # Apply organization overrides
        org_config = self._org_configs.get(organization_id, {})
        config = self._merge_config(config, org_config)
        
        # Apply project overrides
        if project_id:
            project_defaults = deepcopy(SYSTEM_DEFAULTS["project"])
            config["project"] = self._merge_config(
                project_defaults,
                self._project_configs.get(project_id, {})
            )
        
        # Apply user overrides
        if user_id:
            user_config = self._user_configs.get(user_id, {})
            user_role = user_config.get("role", "site_engineer")
            role_defaults = deepcopy(SYSTEM_DEFAULTS["user_by_role"].get(user_role, {}))
            config["user"] = self._merge_config(role_defaults, user_config)
        
        return config
    
    def _merge_config(self, base: Dict, override: Dict) -> Dict:
        """Deep merge override into base"""
        result = deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = deepcopy(value)
        
        return result
    
    # =========================================================================
    # ORGANIZATION CONFIG
    # =========================================================================
    
    def set_organization_config(
        self,
        organization_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Set organization configuration"""
        if organization_id not in self._org_configs:
            self._org_configs[organization_id] = {}
        
        self._org_configs[organization_id] = self._merge_config(
            self._org_configs[organization_id],
            config
        )
        
        logger.info(f"⚙️ Organization config updated: {organization_id}")
        return self._org_configs[organization_id]
    
    def get_organization_config(self, organization_id: str) -> Dict[str, Any]:
        """Get organization configuration"""
        defaults = deepcopy(SYSTEM_DEFAULTS["organization"])
        overrides = self._org_configs.get(organization_id, {})
        return self._merge_config(defaults, overrides)
    
    # =========================================================================
    # PROJECT CONFIG
    # =========================================================================
    
    def set_project_config(
        self,
        project_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Set project configuration"""
        if project_id not in self._project_configs:
            self._project_configs[project_id] = {}
        
        self._project_configs[project_id] = self._merge_config(
            self._project_configs[project_id],
            config
        )
        
        logger.info(f"⚙️ Project config updated: {project_id}")
        return self._project_configs[project_id]
    
    def get_project_config(
        self,
        project_id: str,
        organization_id: str = None,
    ) -> Dict[str, Any]:
        """Get project configuration"""
        defaults = deepcopy(SYSTEM_DEFAULTS["project"])
        overrides = self._project_configs.get(project_id, {})
        return self._merge_config(defaults, overrides)
    
    # =========================================================================
    # USER CONFIG
    # =========================================================================
    
    def set_user_config(
        self,
        user_id: str,
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Set user configuration"""
        if user_id not in self._user_configs:
            self._user_configs[user_id] = {}
        
        self._user_configs[user_id] = self._merge_config(
            self._user_configs[user_id],
            config
        )
        
        logger.info(f"⚙️ User config updated: {user_id}")
        return self._user_configs[user_id]
    
    def get_user_config(self, user_id: str, role: str = "site_engineer") -> Dict[str, Any]:
        """Get user configuration"""
        role_defaults = deepcopy(SYSTEM_DEFAULTS["user_by_role"].get(role, {}))
        overrides = self._user_configs.get(user_id, {})
        return self._merge_config(role_defaults, overrides)
    
    # =========================================================================
    # PERMISSION CHECKS
    # =========================================================================
    
    def has_permission(
        self,
        user_id: str,
        permission: str,
        role: str = "site_engineer",
    ) -> bool:
        """Check if user has a specific permission"""
        config = self.get_user_config(user_id, role)
        permissions = config.get("permissions", {})
        return permissions.get(permission, False)
    
    def get_user_permissions(self, user_id: str, role: str = "site_engineer") -> Dict[str, bool]:
        """Get all permissions for a user"""
        config = self.get_user_config(user_id, role)
        return config.get("permissions", {})
    
    # =========================================================================
    # FEATURE FLAGS
    # =========================================================================
    
    def is_feature_enabled(
        self,
        organization_id: str,
        feature: str,
    ) -> bool:
        """Check if a feature is enabled for an organization"""
        config = self.get_organization_config(organization_id)
        features = config.get("features", {})
        return features.get(feature, False)
    
    def get_enabled_features(self, organization_id: str) -> List[str]:
        """Get list of enabled features"""
        config = self.get_organization_config(organization_id)
        features = config.get("features", {})
        return [f for f, enabled in features.items() if enabled]
    
    # =========================================================================
    # NOTIFICATION SETTINGS
    # =========================================================================
    
    def should_notify(
        self,
        user_id: str,
        notification_type: str,
        role: str = "site_engineer",
    ) -> bool:
        """Check if user should receive a notification type"""
        config = self.get_user_config(user_id, role)
        notifications = config.get("notifications", {})
        return notifications.get(notification_type, False)
    
    def get_notification_recipients(
        self,
        project_id: str,
        notification_type: str,
    ) -> List[str]:
        """Get roles that should receive a notification type"""
        config = self.get_project_config(project_id)
        notifications = config.get("notifications", {})
        
        # Map notification types to recipient keys
        type_mapping = {
            "morning_brief": "morning_brief_recipients",
            "red_flag": "red_flag_recipients",
            "daily_summary": "daily_summary_recipients",
            "weekly_report": "weekly_report_recipients",
        }
        
        key = type_mapping.get(notification_type, f"{notification_type}_recipients")
        return notifications.get(key, [])
    
    # =========================================================================
    # AI CONFIG
    # =========================================================================
    
    def get_ai_config(self, project_id: str) -> Dict[str, Any]:
        """Get AI configuration for a project"""
        config = self.get_project_config(project_id)
        return config.get("ai_config", {
            "include_drawing_references": True,
            "include_revision_warnings": True,
            "safety_emphasis": "high",
            "response_length": "medium",
        })
    
    # =========================================================================
    # BRANDING
    # =========================================================================
    
    def get_branding(self, organization_id: str) -> Dict[str, Any]:
        """Get branding settings for an organization"""
        config = self.get_organization_config(organization_id)
        return config.get("branding", {
            "assistant_name": "SiteMind",
            "logo_url": None,
            "primary_color": "#2563eb",
        })
    
    def get_assistant_name(self, organization_id: str) -> str:
        """Get the assistant name (for personalized responses)"""
        branding = self.get_branding(organization_id)
        return branding.get("assistant_name", "SiteMind")


# Singleton instance
config_service = ConfigService()

