"""
SiteMind Onboarding Service
Customer setup and configuration

FEATURES:
- Organization creation
- Project setup
- User creation
- Initial configuration
- Welcome messages
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from services.config_service import config_service
from services.whatsapp_client import WhatsAppClient
from utils.logger import logger


@dataclass
class OnboardingSession:
    id: str
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    admin_user: Optional[Dict] = None
    projects: List[Dict] = field(default_factory=list)
    team_members: List[Dict] = field(default_factory=list)
    config: Dict = field(default_factory=dict)
    status: str = "started"
    created_at: str = ""
    completed_at: Optional[str] = None


class OnboardingService:
    """
    Handle customer onboarding
    """
    
    def __init__(self):
        self._sessions: Dict[str, OnboardingSession] = {}
        self._organizations: Dict[str, Dict] = {}
        self._projects: Dict[str, Dict] = {}
        self._users: Dict[str, Dict] = {}
        
        self.whatsapp = WhatsAppClient()
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    def start_session(self) -> OnboardingSession:
        """Start a new onboarding session"""
        session = OnboardingSession(
            id=f"onb_{datetime.utcnow().timestamp():.0f}",
            created_at=datetime.utcnow().isoformat(),
        )
        self._sessions[session.id] = session
        
        logger.info(f"🚀 Onboarding session started: {session.id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[OnboardingSession]:
        """Get an onboarding session"""
        return self._sessions.get(session_id)
    
    # =========================================================================
    # ORGANIZATION
    # =========================================================================
    
    def create_organization(
        self,
        session_id: str,
        name: str,
        gstin: str = None,
        address: str = None,
        plan: str = "professional",
    ) -> Dict[str, Any]:
        """Create organization in session"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        org_id = f"org_{datetime.utcnow().timestamp():.0f}"
        
        org = {
            "id": org_id,
            "name": name,
            "gstin": gstin,
            "address": address,
            "plan": plan,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        session.organization_id = org_id
        session.organization_name = name
        
        self._organizations[org_id] = org
        
        # Initialize default config
        config_service.set_org_config(org_id, {
            "plan": plan,
            "assistant_name": "SiteMind",
        })
        
        logger.info(f"🏢 Organization created: {name} ({org_id})")
        
        return org
    
    # =========================================================================
    # ADMIN USER
    # =========================================================================
    
    def create_admin_user(
        self,
        session_id: str,
        name: str,
        email: str,
        phone: str,
    ) -> Dict[str, Any]:
        """Create admin user for organization"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        user_id = f"user_{datetime.utcnow().timestamp():.0f}"
        
        user = {
            "id": user_id,
            "organization_id": session.organization_id,
            "name": name,
            "email": email,
            "phone": self._format_phone(phone),
            "role": "admin",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        session.admin_user = user
        self._users[user_id] = user
        
        logger.info(f"👤 Admin user created: {name} ({user_id})")
        
        return user
    
    # =========================================================================
    # PROJECTS
    # =========================================================================
    
    def add_project(
        self,
        session_id: str,
        name: str,
        location: str = None,
        project_type: str = "residential",
    ) -> Dict[str, Any]:
        """Add a project to the session"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        project_id = f"proj_{datetime.utcnow().timestamp():.0f}"
        
        project = {
            "id": project_id,
            "organization_id": session.organization_id,
            "name": name,
            "location": location,
            "project_type": project_type,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        session.projects.append(project)
        self._projects[project_id] = project
        
        logger.info(f"📁 Project added: {name} ({project_id})")
        
        return project
    
    # =========================================================================
    # TEAM MEMBERS
    # =========================================================================
    
    def add_team_member(
        self,
        session_id: str,
        project_id: str,
        name: str,
        phone: str,
        role: str = "site_engineer",
    ) -> Dict[str, Any]:
        """Add a team member"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        user_id = f"user_{datetime.utcnow().timestamp():.0f}"
        
        user = {
            "id": user_id,
            "organization_id": session.organization_id,
            "project_id": project_id,
            "name": name,
            "phone": self._format_phone(phone),
            "role": role,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        session.team_members.append(user)
        self._users[user_id] = user
        
        logger.info(f"👤 Team member added: {name} as {role}")
        
        return user
    
    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    
    def set_config(
        self,
        session_id: str,
        config: Dict[str, Any],
    ):
        """Set configuration for the session"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        session.config = config
        
        if session.organization_id:
            config_service.set_org_config(session.organization_id, config)
    
    # =========================================================================
    # COMPLETE ONBOARDING
    # =========================================================================
    
    async def complete_onboarding(
        self,
        session_id: str,
        send_welcome: bool = True,
    ) -> Dict[str, Any]:
        """Complete the onboarding process"""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        session.status = "completed"
        session.completed_at = datetime.utcnow().isoformat()
        
        result = {
            "organization_id": session.organization_id,
            "organization_name": session.organization_name,
            "admin_user_id": session.admin_user["id"] if session.admin_user else None,
            "project_count": len(session.projects),
            "team_member_count": len(session.team_members),
            "welcome_messages_sent": 0,
        }
        
        # Send welcome messages
        if send_welcome:
            # Welcome admin
            if session.admin_user:
                await self._send_welcome(
                    session.admin_user["phone"],
                    session.admin_user["name"],
                    "admin",
                    session.organization_name,
                )
                result["welcome_messages_sent"] += 1
            
            # Welcome team members
            for member in session.team_members:
                await self._send_welcome(
                    member["phone"],
                    member["name"],
                    member["role"],
                    session.organization_name,
                )
                result["welcome_messages_sent"] += 1
        
        logger.info(f"✅ Onboarding completed: {session.organization_name}")
        
        return result
    
    # =========================================================================
    # QUICK SETUP
    # =========================================================================
    
    async def quick_setup(
        self,
        organization_name: str,
        admin_name: str,
        admin_email: str,
        admin_phone: str,
        projects: List[Dict] = None,
        team_members: List[Dict] = None,
        config: Dict = None,
        send_welcome: bool = True,
    ) -> Dict[str, Any]:
        """Quick setup - do everything in one call"""
        
        # Start session
        session = self.start_session()
        
        # Create organization
        self.create_organization(session.id, organization_name)
        
        # Create admin
        self.create_admin_user(session.id, admin_name, admin_email, admin_phone)
        
        # Add projects
        if projects:
            for proj in projects:
                self.add_project(
                    session.id,
                    proj.get("name", "Main Project"),
                    proj.get("location"),
                    proj.get("type", "residential"),
                )
        
        # Add team members
        if team_members:
            project_id = session.projects[0]["id"] if session.projects else None
            for member in team_members:
                self.add_team_member(
                    session.id,
                    member.get("project_id", project_id),
                    member.get("name"),
                    member.get("phone"),
                    member.get("role", "site_engineer"),
                )
        
        # Set config
        if config:
            self.set_config(session.id, config)
        
        # Complete
        return await self.complete_onboarding(session.id, send_welcome)
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number"""
        phone = phone.replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            if phone.startswith("91"):
                phone = f"+{phone}"
            else:
                phone = f"+91{phone}"
        return phone
    
    async def _send_welcome(
        self,
        phone: str,
        name: str,
        role: str,
        org_name: str,
    ):
        """Send welcome message"""
        await self.whatsapp.send_welcome(phone, name, role, org_name)
    
    # =========================================================================
    # LOOKUPS
    # =========================================================================
    
    def get_organization(self, org_id: str) -> Optional[Dict]:
        """Get organization by ID"""
        return self._organizations.get(org_id)
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        return self._projects.get(project_id)
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self._users.get(user_id)
    
    def get_user_by_phone(self, phone: str) -> Optional[Dict]:
        """Get user by phone number"""
        phone_formatted = self._format_phone(phone)
        for user in self._users.values():
            if user.get("phone") == phone_formatted:
                return user
        return None
    
    def list_organizations(self) -> List[Dict]:
        """List all organizations"""
        return list(self._organizations.values())
    
    def list_projects(self, org_id: str = None) -> List[Dict]:
        """List projects, optionally filtered by org"""
        projects = list(self._projects.values())
        if org_id:
            projects = [p for p in projects if p.get("organization_id") == org_id]
        return projects
    
    def list_users(self, org_id: str = None, project_id: str = None) -> List[Dict]:
        """List users, optionally filtered"""
        users = list(self._users.values())
        if org_id:
            users = [u for u in users if u.get("organization_id") == org_id]
        if project_id:
            users = [u for u in users if u.get("project_id") == project_id]
        return users


# Singleton instance
onboarding_service = OnboardingService()
