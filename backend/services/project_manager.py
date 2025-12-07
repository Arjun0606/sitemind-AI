"""
SiteMind Project Manager
Handle multiple projects per company via WhatsApp

For Urbanrise: 20+ projects, seamless switching.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from utils.logger import logger


@dataclass
class Project:
    """Project data"""
    id: str
    company_id: str
    name: str
    location: str = ""
    project_type: str = "residential"  # residential, commercial, mixed, infrastructure
    stage: str = "active"  # planning, active, finishing, handover, archived
    created_at: str = ""
    
    # Stats
    total_queries: int = 0
    total_photos: int = 0
    total_documents: int = 0
    active_users: int = 0


@dataclass
class UserSession:
    """User's current session state"""
    user_id: str
    company_id: str
    current_project_id: Optional[str] = None
    last_active: str = ""


class ProjectManager:
    """
    Manage projects and user sessions
    
    Key features:
    - Switch between projects via WhatsApp
    - Track activity per project
    - List all company projects
    """
    
    def __init__(self):
        # Projects: company_id -> {project_id: Project}
        self._projects: Dict[str, Dict[str, Project]] = {}
        
        # User sessions: user_id -> UserSession
        self._sessions: Dict[str, UserSession] = {}
        
        # Project aliases for quick switching
        self._aliases: Dict[str, Dict[str, str]] = {}  # company_id -> {alias: project_id}
    
    # =========================================================================
    # PROJECT CRUD
    # =========================================================================
    
    def create_project(
        self,
        company_id: str,
        project_id: str,
        name: str,
        location: str = "",
        project_type: str = "residential",
    ) -> Project:
        """Create a new project"""
        if company_id not in self._projects:
            self._projects[company_id] = {}
        
        project = Project(
            id=project_id,
            company_id=company_id,
            name=name,
            location=location,
            project_type=project_type,
            created_at=datetime.utcnow().isoformat(),
        )
        
        self._projects[company_id][project_id] = project
        
        # Auto-create alias from first word of name
        alias = name.split()[0].lower() if name else project_id[:6]
        self.set_alias(company_id, alias, project_id)
        
        logger.info(f"🏗️ Created project: {name} ({project_id})")
        
        return project
    
    def get_project(self, company_id: str, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self._projects.get(company_id, {}).get(project_id)
    
    def get_company_projects(self, company_id: str) -> List[Project]:
        """Get all projects for a company"""
        return list(self._projects.get(company_id, {}).values())
    
    def get_active_projects(self, company_id: str) -> List[Project]:
        """Get active projects only"""
        return [
            p for p in self.get_company_projects(company_id)
            if p.stage in ["planning", "active", "finishing"]
        ]
    
    # =========================================================================
    # USER SESSIONS
    # =========================================================================
    
    def get_session(self, user_id: str, company_id: str) -> UserSession:
        """Get or create user session"""
        if user_id not in self._sessions:
            self._sessions[user_id] = UserSession(
                user_id=user_id,
                company_id=company_id,
            )
        
        session = self._sessions[user_id]
        session.last_active = datetime.utcnow().isoformat()
        
        return session
    
    def get_current_project(self, user_id: str, company_id: str) -> Optional[Project]:
        """Get user's current active project"""
        session = self.get_session(user_id, company_id)
        
        if session.current_project_id:
            return self.get_project(company_id, session.current_project_id)
        
        # Default to first active project
        projects = self.get_active_projects(company_id)
        if projects:
            session.current_project_id = projects[0].id
            return projects[0]
        
        return None
    
    def switch_project(
        self,
        user_id: str,
        company_id: str,
        project_identifier: str,
    ) -> Optional[Project]:
        """
        Switch user to a different project
        
        project_identifier can be:
        - Project ID
        - Project name (partial match)
        - Project alias
        """
        session = self.get_session(user_id, company_id)
        
        # Try alias first
        aliases = self._aliases.get(company_id, {})
        if project_identifier.lower() in aliases:
            project_id = aliases[project_identifier.lower()]
            project = self.get_project(company_id, project_id)
            if project:
                session.current_project_id = project.id
                logger.info(f"🔄 User {user_id} switched to {project.name}")
                return project
        
        # Try exact ID match
        project = self.get_project(company_id, project_identifier)
        if project:
            session.current_project_id = project.id
            return project
        
        # Try name partial match
        projects = self.get_company_projects(company_id)
        identifier_lower = project_identifier.lower()
        
        for p in projects:
            if identifier_lower in p.name.lower():
                session.current_project_id = p.id
                logger.info(f"🔄 User {user_id} switched to {p.name}")
                return p
        
        return None
    
    # =========================================================================
    # ALIASES
    # =========================================================================
    
    def set_alias(self, company_id: str, alias: str, project_id: str):
        """Set project alias for quick switching"""
        if company_id not in self._aliases:
            self._aliases[company_id] = {}
        
        self._aliases[company_id][alias.lower()] = project_id
    
    def get_aliases(self, company_id: str) -> Dict[str, str]:
        """Get all aliases for company"""
        return self._aliases.get(company_id, {})
    
    # =========================================================================
    # ACTIVITY TRACKING
    # =========================================================================
    
    def track_query(self, company_id: str, project_id: str):
        """Track query for project"""
        project = self.get_project(company_id, project_id)
        if project:
            project.total_queries += 1
    
    def track_photo(self, company_id: str, project_id: str):
        """Track photo for project"""
        project = self.get_project(company_id, project_id)
        if project:
            project.total_photos += 1
    
    def track_document(self, company_id: str, project_id: str):
        """Track document for project"""
        project = self.get_project(company_id, project_id)
        if project:
            project.total_documents += 1
    
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    def format_project_list(self, company_id: str) -> str:
        """Format project list for WhatsApp"""
        projects = self.get_company_projects(company_id)
        
        if not projects:
            return "No projects found. Contact admin to add projects."
        
        active = [p for p in projects if p.stage in ["planning", "active", "finishing"]]
        archived = [p for p in projects if p.stage in ["handover", "archived"]]
        
        msg = """
📋 *Your Projects*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Active Projects*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for p in active:
            stage_icon = {
                "planning": "📝",
                "active": "🏗️",
                "finishing": "🔨",
            }.get(p.stage, "📋")
            
            alias = self._get_alias_for_project(company_id, p.id)
            alias_text = f" ('{alias}')" if alias else ""
            
            msg += f"""
{stage_icon} *{p.name}*{alias_text}
   📍 {p.location or 'No location'}
   📊 {p.total_queries} queries | {p.total_photos} photos
"""
        
        if archived:
            msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Completed/Archived*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for p in archived[:3]:
                msg += f"\n✅ {p.name}"
            
            if len(archived) > 3:
                msg += f"\n_...and {len(archived) - 3} more_"
        
        msg += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 *Switch project:* Type the project name
   Example: "switch to Marina Bay"
"""
        return msg
    
    def format_current_project(self, project: Project) -> str:
        """Format current project info"""
        return f"""
🏗️ *Current Project*

*{project.name}*
📍 {project.location or 'No location set'}
📊 Stage: {project.stage.title()}

Activity:
• {project.total_queries} questions answered
• {project.total_photos} photos analyzed
• {project.total_documents} documents processed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_Type 'projects' to see all projects_
_Type 'switch to [name]' to change_
"""
    
    def format_switch_success(self, project: Project) -> str:
        """Format successful switch message"""
        return f"""
✅ *Switched to {project.name}*

📍 {project.location or 'No location'}
📊 {project.total_queries} queries so far

All your questions will now be about this project.

_Ask anything!_
"""
    
    def _get_alias_for_project(self, company_id: str, project_id: str) -> Optional[str]:
        """Get alias for a project"""
        aliases = self._aliases.get(company_id, {})
        for alias, pid in aliases.items():
            if pid == project_id:
                return alias
        return None


# Singleton
project_manager = ProjectManager()

