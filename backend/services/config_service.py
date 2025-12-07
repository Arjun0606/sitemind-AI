"""
SiteMind Configuration Service
Customer-specific settings and customization

FEATURES:
- Organization-level config
- Project-level config
- User-level config
- Feature toggles
- Branding
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from copy import deepcopy


class ConfigService:
    """
    Manage customer configurations
    """
    
    def __init__(self):
        # Organization configs
        self._org_configs: Dict[str, Dict] = {}
        
        # Project configs (override org)
        self._project_configs: Dict[str, Dict] = {}
        
        # User configs (override project)
        self._user_configs: Dict[str, Dict] = {}
        
        # Default configuration
        self.default_config = {
            # General
            "language": "en",
            "timezone": "Asia/Kolkata",
            
            # Assistant
            "assistant_name": "SiteMind",
            "response_style": "professional",  # professional, friendly, brief
            "include_citations": True,
            "safety_emphasis": "high",  # high, medium, low
            "response_length": "medium",  # brief, medium, detailed
            
            # Features
            "features": {
                "red_flags": True,
                "task_management": True,
                "material_tracking": True,
                "progress_monitoring": True,
                "office_site_sync": True,
                "morning_briefs": True,
                "weekly_reports": True,
                "photo_analysis": True,
                "document_analysis": True,
                "team_management": True,
            },
            
            # Notifications
            "notifications": {
                "morning_brief": True,
                "morning_brief_time": "07:00",
                "red_flag_alerts": True,
                "weekly_report": True,
                "daily_summary": False,
            },
            
            # Enterprise features
            "enterprise": {
                "custom_reports": False,
                "api_access": False,
                "advanced_analytics": False,
                "multi_project": True,
                "audit_export": True,
            },
        }
    
    # =========================================================================
    # ORGANIZATION CONFIG
    # =========================================================================
    
    def set_org_config(
        self,
        org_id: str,
        config: Dict[str, Any],
    ):
        """Set organization configuration"""
        if org_id not in self._org_configs:
            self._org_configs[org_id] = deepcopy(self.default_config)
        
        self._merge_config(self._org_configs[org_id], config)
    
    def get_org_config(self, org_id: str) -> Dict[str, Any]:
        """Get organization configuration"""
        return self._org_configs.get(org_id, deepcopy(self.default_config))
    
    # =========================================================================
    # PROJECT CONFIG
    # =========================================================================
    
    def set_project_config(
        self,
        project_id: str,
        config: Dict[str, Any],
    ):
        """Set project-specific configuration"""
        if project_id not in self._project_configs:
            self._project_configs[project_id] = {}
        
        self._merge_config(self._project_configs[project_id], config)
    
    def get_project_config(
        self,
        project_id: str,
        org_id: str = None,
    ) -> Dict[str, Any]:
        """Get project configuration (merged with org)"""
        # Start with org config or default
        if org_id:
            config = deepcopy(self.get_org_config(org_id))
        else:
            config = deepcopy(self.default_config)
        
        # Merge project overrides
        project_config = self._project_configs.get(project_id, {})
        self._merge_config(config, project_config)
        
        return config
    
    # =========================================================================
    # USER CONFIG
    # =========================================================================
    
    def set_user_config(
        self,
        user_id: str,
        config: Dict[str, Any],
    ):
        """Set user-specific configuration"""
        if user_id not in self._user_configs:
            self._user_configs[user_id] = {}
        
        self._merge_config(self._user_configs[user_id], config)
    
    def get_user_config(
        self,
        user_id: str,
        project_id: str = None,
        org_id: str = None,
    ) -> Dict[str, Any]:
        """Get user configuration (merged with project and org)"""
        # Start with project config
        if project_id:
            config = self.get_project_config(project_id, org_id)
        elif org_id:
            config = self.get_org_config(org_id)
        else:
            config = deepcopy(self.default_config)
        
        # Merge user overrides
        user_config = self._user_configs.get(user_id, {})
        self._merge_config(config, user_config)
        
        return config
    
    # =========================================================================
    # FEATURE TOGGLES
    # =========================================================================
    
    def is_feature_enabled(
        self,
        feature: str,
        org_id: str = None,
        project_id: str = None,
        user_id: str = None,
    ) -> bool:
        """Check if a feature is enabled"""
        if user_id:
            config = self.get_user_config(user_id, project_id, org_id)
        elif project_id:
            config = self.get_project_config(project_id, org_id)
        elif org_id:
            config = self.get_org_config(org_id)
        else:
            config = self.default_config
        
        features = config.get("features", {})
        return features.get(feature, False)
    
    def enable_feature(
        self,
        feature: str,
        org_id: str = None,
        project_id: str = None,
    ):
        """Enable a feature"""
        if project_id:
            self.set_project_config(project_id, {"features": {feature: True}})
        elif org_id:
            self.set_org_config(org_id, {"features": {feature: True}})
    
    def disable_feature(
        self,
        feature: str,
        org_id: str = None,
        project_id: str = None,
    ):
        """Disable a feature"""
        if project_id:
            self.set_project_config(project_id, {"features": {feature: False}})
        elif org_id:
            self.set_org_config(org_id, {"features": {feature: False}})
    
    # =========================================================================
    # BRANDING
    # =========================================================================
    
    def set_branding(
        self,
        org_id: str,
        assistant_name: str = None,
        response_style: str = None,
    ):
        """Set branding options"""
        branding = {}
        if assistant_name:
            branding["assistant_name"] = assistant_name
        if response_style:
            branding["response_style"] = response_style
        
        self.set_org_config(org_id, branding)
    
    def get_branding(self, org_id: str) -> Dict[str, str]:
        """Get branding options"""
        config = self.get_org_config(org_id)
        return {
            "assistant_name": config.get("assistant_name", "SiteMind"),
            "response_style": config.get("response_style", "professional"),
        }
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _merge_config(self, base: Dict, override: Dict):
        """Deep merge override into base"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get_all_features(self) -> List[str]:
        """Get list of all available features"""
        return list(self.default_config["features"].keys())
    
    def export_config(self, org_id: str) -> Dict[str, Any]:
        """Export full configuration for an organization"""
        return {
            "organization": self.get_org_config(org_id),
            "projects": {
                pid: cfg for pid, cfg in self._project_configs.items()
            },
            "users": {
                uid: cfg for uid, cfg in self._user_configs.items()
            },
        }


# Singleton instance
config_service = ConfigService()
