"""
SiteMind Team Management Service
Self-service team management via WhatsApp

COMMANDS (for Admins/PMs):
- "add team [name] [phone] [role]" → Add new member
- "remove team [phone]" → Remove member
- "list team" → Show all team members
- "change role [phone] [new_role]" → Change someone's role

FLOW:
1. Admin sends: "add team Ramesh 9876543210 engineer"
2. SiteMind validates permissions
3. Creates user, sends welcome message
4. Confirms to admin

NO DASHBOARD NEEDED - all via WhatsApp!
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import re

from utils.logger import logger
from services.config_service import config_service


class TeamManagementService:
    """
    Self-service team management via WhatsApp
    """
    
    def __init__(self):
        # In production, these would be in database
        self._users: Dict[str, Dict] = {}
        self._project_members: Dict[str, List[str]] = {}  # project_id -> [user_ids]
        self._user_projects: Dict[str, List[str]] = {}    # user_id -> [project_ids]
    
    # Role aliases (what users type → actual role)
    ROLE_ALIASES = {
        # Site Engineer
        "engineer": "site_engineer",
        "site engineer": "site_engineer",
        "site_engineer": "site_engineer",
        "se": "site_engineer",
        
        # PM
        "pm": "pm",
        "project manager": "pm",
        "manager": "pm",
        
        # Consultant
        "consultant": "consultant",
        "architect": "consultant",
        "structural": "consultant",
        
        # Viewer
        "viewer": "viewer",
        "view": "viewer",
        "readonly": "viewer",
        
        # Store Keeper (special site_engineer with limited permissions)
        "store": "store_keeper",
        "storekeeper": "store_keeper",
        "store keeper": "store_keeper",
    }
    
    # =========================================================================
    # COMMAND PARSING
    # =========================================================================
    
    def parse_command(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Parse team management commands from WhatsApp messages
        
        Returns None if not a team command
        """
        message = message.strip().lower()
        
        # Add team member
        # Formats: "add team Ramesh 9876543210 engineer"
        #          "add Ramesh 9876543210"
        #          "new member Ramesh 9876543210 pm"
        add_patterns = [
            r"^add\s+team\s+(.+?)\s+(\d{10})\s*(.*)$",
            r"^add\s+member\s+(.+?)\s+(\d{10})\s*(.*)$",
            r"^new\s+member\s+(.+?)\s+(\d{10})\s*(.*)$",
            r"^add\s+(.+?)\s+(\d{10})\s*(.*)$",
        ]
        
        for pattern in add_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                name = match.group(1).strip().title()
                phone = match.group(2)
                role_input = match.group(3).strip() if match.group(3) else "engineer"
                role = self.ROLE_ALIASES.get(role_input.lower(), "site_engineer")
                
                return {
                    "command": "add",
                    "name": name,
                    "phone": self._format_phone(phone),
                    "role": role,
                }
        
        # Remove team member
        # Formats: "remove team 9876543210"
        #          "remove Ramesh"
        #          "delete member 9876543210"
        remove_patterns = [
            r"^remove\s+team\s+(\d{10})$",
            r"^remove\s+member\s+(\d{10})$",
            r"^delete\s+member\s+(\d{10})$",
            r"^remove\s+(\d{10})$",
            r"^remove\s+team\s+(.+)$",
            r"^remove\s+(.+)$",
        ]
        
        for pattern in remove_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                identifier = match.group(1).strip()
                return {
                    "command": "remove",
                    "identifier": identifier,  # Could be phone or name
                }
        
        # List team
        if message in ["list team", "show team", "team list", "team members", "my team"]:
            return {"command": "list"}
        
        # Change role
        # Format: "change role 9876543210 pm"
        role_pattern = r"^change\s+role\s+(\d{10})\s+(.+)$"
        match = re.match(role_pattern, message, re.IGNORECASE)
        if match:
            phone = match.group(1)
            role_input = match.group(2).strip()
            role = self.ROLE_ALIASES.get(role_input.lower())
            
            if role:
                return {
                    "command": "change_role",
                    "phone": self._format_phone(phone),
                    "new_role": role,
                }
        
        return None
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number with country code"""
        phone = phone.replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            if phone.startswith("91"):
                phone = f"+{phone}"
            else:
                phone = f"+91{phone}"
        return phone
    
    # =========================================================================
    # COMMAND EXECUTION
    # =========================================================================
    
    async def execute_command(
        self,
        command: Dict[str, Any],
        requester_phone: str,
        project_id: str,
        organization_id: str,
    ) -> Dict[str, Any]:
        """
        Execute a team management command
        
        Returns response to send back
        """
        # Check permissions
        requester = self._get_user_by_phone(requester_phone)
        if not requester:
            return {
                "success": False,
                "message": "You're not registered in this project.",
            }
        
        requester_role = requester.get("role", "site_engineer")
        
        # Only owner, admin, pm can manage team
        if requester_role not in ["owner", "admin", "pm"]:
            return {
                "success": False,
                "message": "Sorry, only Project Managers and above can manage team members.",
            }
        
        cmd = command["command"]
        
        if cmd == "add":
            return await self._add_member(
                command, requester, project_id, organization_id
            )
        elif cmd == "remove":
            return await self._remove_member(
                command, requester, project_id
            )
        elif cmd == "list":
            return await self._list_members(project_id)
        elif cmd == "change_role":
            return await self._change_role(
                command, requester, project_id
            )
        
        return {"success": False, "message": "Unknown command"}
    
    async def _add_member(
        self,
        command: Dict,
        requester: Dict,
        project_id: str,
        organization_id: str,
    ) -> Dict[str, Any]:
        """Add a new team member"""
        name = command["name"]
        phone = command["phone"]
        role = command["role"]
        
        # Check if user already exists
        existing = self._get_user_by_phone(phone)
        if existing:
            # Check if already in this project
            if project_id in self._user_projects.get(existing["id"], []):
                return {
                    "success": False,
                    "message": f"{name} ({phone}) is already a member of this project.",
                }
            
            # Add to project
            user_id = existing["id"]
        else:
            # Create new user
            user_id = f"user_{datetime.utcnow().timestamp():.0f}"
            
            user = {
                "id": user_id,
                "organization_id": organization_id,
                "name": name,
                "phone": phone,
                "role": role,
                "added_by": requester["phone"],
                "added_at": datetime.utcnow().isoformat(),
            }
            
            self._users[user_id] = user
            
            # Set config based on role
            config_service.set_user_config(user_id, {"role": role})
        
        # Add to project
        if project_id not in self._project_members:
            self._project_members[project_id] = []
        self._project_members[project_id].append(user_id)
        
        if user_id not in self._user_projects:
            self._user_projects[user_id] = []
        self._user_projects[user_id].append(project_id)
        
        logger.info(f"👤 Team member added via WhatsApp: {name} ({role})")
        
        # Generate welcome message
        welcome_message = self._generate_welcome_message(name, role, organization_id)
        
        return {
            "success": True,
            "message": f"✅ **{name}** added as **{self._format_role(role)}**\n\nI'll send them a welcome message now.",
            "welcome_message": {
                "phone": phone,
                "message": welcome_message,
            },
            "user_id": user_id,
        }
    
    async def _remove_member(
        self,
        command: Dict,
        requester: Dict,
        project_id: str,
    ) -> Dict[str, Any]:
        """Remove a team member"""
        identifier = command["identifier"]
        
        # Find user by phone or name
        user = None
        if identifier.isdigit() or identifier.startswith("+"):
            phone = self._format_phone(identifier)
            user = self._get_user_by_phone(phone)
        else:
            # Search by name
            for u in self._users.values():
                if u["name"].lower() == identifier.lower():
                    user = u
                    break
        
        if not user:
            return {
                "success": False,
                "message": f"Couldn't find team member: {identifier}",
            }
        
        # Check if in this project
        if user["id"] not in self._project_members.get(project_id, []):
            return {
                "success": False,
                "message": f"{user['name']} is not a member of this project.",
            }
        
        # Can't remove yourself
        if user["phone"] == requester["phone"]:
            return {
                "success": False,
                "message": "You can't remove yourself from the project.",
            }
        
        # Can't remove someone with higher role
        role_hierarchy = ["viewer", "site_engineer", "consultant", "pm", "admin", "owner"]
        if role_hierarchy.index(user.get("role", "site_engineer")) >= role_hierarchy.index(requester.get("role", "site_engineer")):
            return {
                "success": False,
                "message": f"You can't remove {user['name']} - they have equal or higher access than you.",
            }
        
        # Remove from project
        self._project_members[project_id].remove(user["id"])
        self._user_projects[user["id"]].remove(project_id)
        
        logger.info(f"👤 Team member removed via WhatsApp: {user['name']}")
        
        return {
            "success": True,
            "message": f"✅ **{user['name']}** has been removed from this project.\n\nThey will no longer receive messages or be able to query.",
        }
    
    async def _list_members(self, project_id: str) -> Dict[str, Any]:
        """List all team members"""
        member_ids = self._project_members.get(project_id, [])
        
        if not member_ids:
            return {
                "success": True,
                "message": "No team members in this project yet.\n\nTo add: `add team [name] [phone] [role]`",
            }
        
        # Group by role
        by_role: Dict[str, List[Dict]] = {}
        for uid in member_ids:
            user = self._users.get(uid)
            if user:
                role = user.get("role", "site_engineer")
                if role not in by_role:
                    by_role[role] = []
                by_role[role].append(user)
        
        # Format message
        role_order = ["owner", "admin", "pm", "site_engineer", "consultant", "viewer", "store_keeper"]
        role_emojis = {
            "owner": "👑",
            "admin": "🔑",
            "pm": "📋",
            "site_engineer": "👷",
            "consultant": "🏛️",
            "viewer": "👁️",
            "store_keeper": "📦",
        }
        
        message = "**Team Members**\n\n"
        
        for role in role_order:
            if role in by_role:
                emoji = role_emojis.get(role, "👤")
                message += f"{emoji} **{self._format_role(role)}**\n"
                for user in by_role[role]:
                    phone_display = user["phone"][-4:]  # Last 4 digits
                    message += f"  • {user['name']} (***{phone_display})\n"
                message += "\n"
        
        message += f"_Total: {len(member_ids)} members_"
        
        return {
            "success": True,
            "message": message,
        }
    
    async def _change_role(
        self,
        command: Dict,
        requester: Dict,
        project_id: str,
    ) -> Dict[str, Any]:
        """Change a member's role"""
        phone = command["phone"]
        new_role = command["new_role"]
        
        user = self._get_user_by_phone(phone)
        if not user:
            return {
                "success": False,
                "message": f"Couldn't find team member with phone {phone}",
            }
        
        # Check if in this project
        if user["id"] not in self._project_members.get(project_id, []):
            return {
                "success": False,
                "message": f"{user['name']} is not a member of this project.",
            }
        
        # Can't change your own role
        if user["phone"] == requester["phone"]:
            return {
                "success": False,
                "message": "You can't change your own role.",
            }
        
        old_role = user.get("role", "site_engineer")
        user["role"] = new_role
        config_service.set_user_config(user["id"], {"role": new_role})
        
        logger.info(f"👤 Role changed via WhatsApp: {user['name']} {old_role} → {new_role}")
        
        return {
            "success": True,
            "message": f"✅ **{user['name']}** is now a **{self._format_role(new_role)}**\n\n_Previous: {self._format_role(old_role)}_",
        }
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _get_user_by_phone(self, phone: str) -> Optional[Dict]:
        """Find user by phone number"""
        phone_formatted = self._format_phone(phone)
        for user in self._users.values():
            if user["phone"] == phone_formatted:
                return user
        return None
    
    def _format_role(self, role: str) -> str:
        """Format role for display"""
        return {
            "owner": "Owner",
            "admin": "Admin",
            "pm": "Project Manager",
            "site_engineer": "Site Engineer",
            "consultant": "Consultant",
            "viewer": "Viewer",
            "store_keeper": "Store Keeper",
        }.get(role, role.title())
    
    def _generate_welcome_message(self, name: str, role: str, organization_id: str) -> str:
        """Generate welcome message for new member"""
        branding = config_service.get_branding(organization_id)
        assistant_name = branding.get("assistant_name", "SiteMind")
        
        if role in ["owner", "admin", "pm"]:
            return f"""Welcome to {assistant_name}, {name}! 👋

You've been added as **{self._format_role(role)}**.

You can:
• Ask any question about the project
• Upload drawings and photos
• Create and manage tasks
• View reports and analytics

**Quick commands:**
• `list team` - See team members
• `add team [name] [phone] [role]` - Add someone
• Ask any project question!

Try it now - send any question!"""
        
        else:  # site_engineer, consultant, viewer
            return f"""Welcome to {assistant_name}, {name}! 👋

You've been added to the project team.

I can help you with:
• Blueprint specifications
• Rebar details
• Material information
• And any project questions!

Just send your question - I respond instantly, 24/7.

Example: "beam size B3 floor 2?"

Try it now!"""
    
    # =========================================================================
    # HELP MESSAGE
    # =========================================================================
    
    def get_help_message(self, user_role: str) -> str:
        """Get help message based on user role"""
        if user_role in ["owner", "admin", "pm"]:
            return """**Team Management Commands**

📥 **Add member:**
`add team Ramesh 9876543210 engineer`

Roles: `engineer`, `pm`, `consultant`, `viewer`, `store`

📤 **Remove member:**
`remove team 9876543210`
or `remove Ramesh`

📋 **List team:**
`list team`

🔄 **Change role:**
`change role 9876543210 pm`

_Only Admins and PMs can manage team._"""
        else:
            return "Team management is only available for Project Managers and above."


# Singleton instance
team_management = TeamManagementService()

