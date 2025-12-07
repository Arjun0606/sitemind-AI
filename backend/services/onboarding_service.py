"""
SiteMind Onboarding Service
Automated customer setup and provisioning

FLOW:
1. Create organization
2. Create admin user
3. Create project(s)
4. Add team members
5. Upload initial drawings
6. Send welcome messages
7. Verify setup complete
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid

from utils.logger import logger
from services.config_service import config_service


class OnboardingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OnboardingStep(str, Enum):
    CREATE_ORGANIZATION = "create_organization"
    CREATE_ADMIN_USER = "create_admin_user"
    CREATE_PROJECTS = "create_projects"
    ADD_TEAM_MEMBERS = "add_team_members"
    UPLOAD_DRAWINGS = "upload_drawings"
    SEND_WELCOME = "send_welcome"
    VERIFY_SETUP = "verify_setup"


class OnboardingService:
    """
    Handles customer onboarding process
    """
    
    def __init__(self):
        # In production, this would be in database
        self._onboarding_sessions: Dict[str, Dict] = {}
        self._organizations: Dict[str, Dict] = {}
        self._users: Dict[str, Dict] = {}
        self._projects: Dict[str, Dict] = {}
        self._project_members: Dict[str, List[Dict]] = {}
    
    # =========================================================================
    # ONBOARDING SESSION MANAGEMENT
    # =========================================================================
    
    def start_onboarding(
        self,
        customer_name: str,
        contact_email: str,
        contact_phone: str,
        plan: str = "pilot",
    ) -> Dict[str, Any]:
        """Start a new onboarding session"""
        session_id = f"onb_{uuid.uuid4().hex[:12]}"
        
        session = {
            "session_id": session_id,
            "customer_name": customer_name,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "plan": plan,
            "status": OnboardingStatus.PENDING,
            "current_step": OnboardingStep.CREATE_ORGANIZATION,
            "steps_completed": [],
            "organization_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }
        
        self._onboarding_sessions[session_id] = session
        
        logger.info(f"📋 Onboarding started: {session_id} for {customer_name}")
        
        return session
    
    def get_onboarding_status(self, session_id: str) -> Optional[Dict]:
        """Get current onboarding status"""
        return self._onboarding_sessions.get(session_id)
    
    # =========================================================================
    # STEP 1: CREATE ORGANIZATION
    # =========================================================================
    
    def create_organization(
        self,
        session_id: str,
        name: str,
        slug: str = None,
        billing_email: str = None,
        settings: Dict = None,
    ) -> Dict[str, Any]:
        """Create a new organization"""
        session = self._onboarding_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        org_id = f"org_{uuid.uuid4().hex[:12]}"
        
        # Generate slug from name if not provided
        if not slug:
            slug = name.lower().replace(" ", "-").replace(".", "")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
        
        organization = {
            "id": org_id,
            "name": name,
            "slug": slug,
            "plan": session["plan"],
            "billing_email": billing_email or session["contact_email"],
            "subscription_status": "active",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._organizations[org_id] = organization
        
        # Set default organization config
        config_service.set_organization_config(org_id, settings or {})
        
        # Update session
        session["organization_id"] = org_id
        session["current_step"] = OnboardingStep.CREATE_ADMIN_USER
        session["steps_completed"].append(OnboardingStep.CREATE_ORGANIZATION)
        session["status"] = OnboardingStatus.IN_PROGRESS
        
        logger.info(f"🏢 Organization created: {name} ({org_id})")
        
        return organization
    
    # =========================================================================
    # STEP 2: CREATE ADMIN USER
    # =========================================================================
    
    def create_admin_user(
        self,
        session_id: str,
        name: str,
        email: str,
        phone: str,
    ) -> Dict[str, Any]:
        """Create the admin/owner user"""
        session = self._onboarding_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        org_id = session.get("organization_id")
        if not org_id:
            raise ValueError("Organization must be created first")
        
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        # Ensure phone has country code
        if not phone.startswith("+"):
            phone = f"+91{phone}"
        
        user = {
            "id": user_id,
            "organization_id": org_id,
            "name": name,
            "email": email,
            "phone": phone,
            "role": "owner",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._users[user_id] = user
        
        # Set default user config for owner
        config_service.set_user_config(user_id, {"role": "owner"})
        
        # Update session
        session["admin_user_id"] = user_id
        session["current_step"] = OnboardingStep.CREATE_PROJECTS
        session["steps_completed"].append(OnboardingStep.CREATE_ADMIN_USER)
        
        logger.info(f"👤 Admin user created: {name} ({user_id})")
        
        return user
    
    # =========================================================================
    # STEP 3: CREATE PROJECTS
    # =========================================================================
    
    def create_project(
        self,
        session_id: str,
        name: str,
        code: str = None,
        address: str = None,
        city: str = None,
        project_type: str = "residential",
        settings: Dict = None,
    ) -> Dict[str, Any]:
        """Create a project/site"""
        session = self._onboarding_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        org_id = session.get("organization_id")
        if not org_id:
            raise ValueError("Organization must be created first")
        
        project_id = f"proj_{uuid.uuid4().hex[:12]}"
        
        # Generate code if not provided
        if not code:
            code = name[:3].upper() + "-001"
        
        project = {
            "id": project_id,
            "organization_id": org_id,
            "name": name,
            "code": code,
            "address": address,
            "city": city,
            "project_type": project_type,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._projects[project_id] = project
        self._project_members[project_id] = []
        
        # Set default project config
        config_service.set_project_config(project_id, settings or {})
        
        # Add admin as project member
        admin_id = session.get("admin_user_id")
        if admin_id:
            self._project_members[project_id].append({
                "user_id": admin_id,
                "project_role": "pm",
            })
        
        # Track in session
        if "project_ids" not in session:
            session["project_ids"] = []
        session["project_ids"].append(project_id)
        
        logger.info(f"🏗️ Project created: {name} ({project_id})")
        
        return project
    
    def complete_projects_step(self, session_id: str):
        """Mark projects step as complete"""
        session = self._onboarding_sessions.get(session_id)
        if session:
            session["current_step"] = OnboardingStep.ADD_TEAM_MEMBERS
            session["steps_completed"].append(OnboardingStep.CREATE_PROJECTS)
    
    # =========================================================================
    # STEP 4: ADD TEAM MEMBERS
    # =========================================================================
    
    def add_team_member(
        self,
        session_id: str,
        project_id: str,
        name: str,
        phone: str,
        role: str = "site_engineer",
        permissions: Dict = None,
    ) -> Dict[str, Any]:
        """Add a team member to a project"""
        session = self._onboarding_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        org_id = session.get("organization_id")
        
        # Check if user already exists (by phone)
        existing_user = None
        for uid, user in self._users.items():
            if user["phone"] == phone or user["phone"] == f"+91{phone}":
                existing_user = user
                break
        
        if existing_user:
            user_id = existing_user["id"]
        else:
            user_id = f"user_{uuid.uuid4().hex[:12]}"
            
            # Ensure phone has country code
            if not phone.startswith("+"):
                phone = f"+91{phone}"
            
            user = {
                "id": user_id,
                "organization_id": org_id,
                "name": name,
                "phone": phone,
                "role": role,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            self._users[user_id] = user
        
        # Add to project
        if project_id not in self._project_members:
            self._project_members[project_id] = []
        
        member = {
            "user_id": user_id,
            "project_role": role,
            "permissions": permissions or {},
        }
        
        self._project_members[project_id].append(member)
        
        # Set user config
        config_service.set_user_config(user_id, {
            "role": role,
            **({"permissions": permissions} if permissions else {})
        })
        
        logger.info(f"👤 Team member added: {name} ({role}) to project {project_id}")
        
        return {
            "user_id": user_id,
            "project_id": project_id,
            "role": role,
        }
    
    def add_team_members_bulk(
        self,
        session_id: str,
        project_id: str,
        members: List[Dict],
    ) -> List[Dict]:
        """Add multiple team members at once"""
        results = []
        for member in members:
            result = self.add_team_member(
                session_id=session_id,
                project_id=project_id,
                name=member["name"],
                phone=member["phone"],
                role=member.get("role", "site_engineer"),
                permissions=member.get("permissions"),
            )
            results.append(result)
        return results
    
    def complete_team_step(self, session_id: str):
        """Mark team members step as complete"""
        session = self._onboarding_sessions.get(session_id)
        if session:
            session["current_step"] = OnboardingStep.UPLOAD_DRAWINGS
            session["steps_completed"].append(OnboardingStep.ADD_TEAM_MEMBERS)
    
    # =========================================================================
    # STEP 5: DRAWINGS
    # =========================================================================
    
    def mark_drawings_uploaded(self, session_id: str, count: int):
        """Mark drawings as uploaded"""
        session = self._onboarding_sessions.get(session_id)
        if session:
            session["drawings_uploaded"] = count
            session["current_step"] = OnboardingStep.SEND_WELCOME
            session["steps_completed"].append(OnboardingStep.UPLOAD_DRAWINGS)
            logger.info(f"📐 {count} drawings uploaded for session {session_id}")
    
    # =========================================================================
    # STEP 6: WELCOME MESSAGES
    # =========================================================================
    
    def generate_welcome_messages(self, session_id: str) -> List[Dict]:
        """Generate welcome messages for all team members"""
        session = self._onboarding_sessions.get(session_id)
        if not session:
            return []
        
        org_id = session.get("organization_id")
        org = self._organizations.get(org_id, {})
        org_name = org.get("name", "your company")
        
        branding = config_service.get_branding(org_id)
        assistant_name = branding.get("assistant_name", "SiteMind")
        
        messages = []
        
        # Get all users in this org
        for user_id, user in self._users.items():
            if user.get("organization_id") == org_id:
                role = user.get("role", "site_engineer")
                
                if role == "owner":
                    message = f"""Welcome to {assistant_name}! 🎉

You're now set up as admin for {org_name}.

Your team can send any construction query via WhatsApp and get instant, accurate answers.

To get started:
1. Forward any drawing to this number
2. Ask any question about your project
3. Check the dashboard for analytics

Questions? Just reply here!"""
                
                elif role == "pm":
                    message = f"""Welcome to {assistant_name}!

You've been added as Project Manager for {org_name}.

You can:
• Ask any question about project drawings & specs
• Upload documents and photos
• Create and assign tasks
• View progress reports

Try asking: "What's the status of Floor 3?"

The more your team uses {assistant_name}, the smarter it gets!"""
                
                else:  # site_engineer
                    message = f"""Welcome to {assistant_name}!

You've been added to {org_name}'s project team.

I can help you with:
• Blueprint specifications ("beam size B3?")
• Rebar details ("sariya at C4?")
• Material info ("steel grade for columns?")
• And more!

Just send your question - I respond instantly, 24/7.

Try it now: Send any question about the project!"""
                
                messages.append({
                    "user_id": user_id,
                    "phone": user["phone"],
                    "name": user["name"],
                    "message": message,
                })
        
        # Update session
        session["current_step"] = OnboardingStep.VERIFY_SETUP
        session["steps_completed"].append(OnboardingStep.SEND_WELCOME)
        
        return messages
    
    # =========================================================================
    # STEP 7: VERIFY & COMPLETE
    # =========================================================================
    
    def complete_onboarding(self, session_id: str) -> Dict[str, Any]:
        """Mark onboarding as complete"""
        session = self._onboarding_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        session["status"] = OnboardingStatus.COMPLETED
        session["current_step"] = None
        session["steps_completed"].append(OnboardingStep.VERIFY_SETUP)
        session["completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Onboarding completed: {session_id}")
        
        return self.get_onboarding_summary(session_id)
    
    def get_onboarding_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of completed onboarding"""
        session = self._onboarding_sessions.get(session_id)
        if not session:
            return {}
        
        org_id = session.get("organization_id")
        org = self._organizations.get(org_id, {})
        
        # Count users and projects
        user_count = len([u for u in self._users.values() 
                         if u.get("organization_id") == org_id])
        project_ids = session.get("project_ids", [])
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "organization": {
                "id": org_id,
                "name": org.get("name"),
                "slug": org.get("slug"),
            },
            "projects_created": len(project_ids),
            "users_added": user_count,
            "drawings_uploaded": session.get("drawings_uploaded", 0),
            "started_at": session["created_at"],
            "completed_at": session.get("completed_at"),
        }
    
    # =========================================================================
    # QUICK SETUP (All-in-one)
    # =========================================================================
    
    def quick_setup(
        self,
        company_name: str,
        admin_name: str,
        admin_email: str,
        admin_phone: str,
        sites: List[Dict],  # [{name, address, city, team: [{name, phone, role}]}]
        plan: str = "pilot",
    ) -> Dict[str, Any]:
        """
        One-call setup for simple onboarding
        
        Example:
        quick_setup(
            company_name="ABC Builders",
            admin_name="Rajesh Sharma",
            admin_email="rajesh@abc.com",
            admin_phone="+919876543210",
            sites=[{
                "name": "Skyline Towers",
                "address": "Sector 62, Noida",
                "city": "Noida",
                "team": [
                    {"name": "Ramesh", "phone": "+919876543211", "role": "site_engineer"},
                    {"name": "Priya", "phone": "+919876543212", "role": "pm"}
                ]
            }],
            plan="pilot"
        )
        """
        # Start session
        session = self.start_onboarding(
            customer_name=company_name,
            contact_email=admin_email,
            contact_phone=admin_phone,
            plan=plan,
        )
        session_id = session["session_id"]
        
        # Create org
        self.create_organization(
            session_id=session_id,
            name=company_name,
        )
        
        # Create admin
        self.create_admin_user(
            session_id=session_id,
            name=admin_name,
            email=admin_email,
            phone=admin_phone,
        )
        
        # Create each site
        for site in sites:
            project = self.create_project(
                session_id=session_id,
                name=site["name"],
                address=site.get("address"),
                city=site.get("city"),
            )
            
            # Add team members
            if site.get("team"):
                self.add_team_members_bulk(
                    session_id=session_id,
                    project_id=project["id"],
                    members=site["team"],
                )
        
        self.complete_projects_step(session_id)
        self.complete_team_step(session_id)
        
        # Generate welcome messages
        messages = self.generate_welcome_messages(session_id)
        
        # Complete
        summary = self.complete_onboarding(session_id)
        summary["welcome_messages"] = messages
        
        return summary


# Singleton instance
onboarding_service = OnboardingService()

