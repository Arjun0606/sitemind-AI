"""
SiteMind Command Handler
All WhatsApp commands in one place

Commands that make the product feel polished and complete.
"""

from typing import Dict, Any, Optional, Tuple
import re

from utils.logger import logger


class CommandHandler:
    """
    Parse and handle all WhatsApp commands
    
    Commands:
    - help: Show all commands
    - projects: List all projects
    - switch to [name]: Switch project
    - project: Current project info
    - status: Usage status
    - roi: ROI report
    - team: List team members
    - add [phone] [name]: Add team member
    - report: Weekly report
    - brief: Today's brief
    - search [query]: Search memory
    """
    
    def __init__(self):
        # Command patterns
        self.COMMANDS = {
            "help": self._cmd_help,
            "projects": self._cmd_projects,
            "project": self._cmd_current_project,
            "status": self._cmd_status,
            "roi": self._cmd_roi,
            "report": self._cmd_report,
            "week": self._cmd_report,
            "brief": self._cmd_brief,
            "team": self._cmd_team,
            "search": self._cmd_search,
            "hi": self._cmd_hello,
            "hello": self._cmd_hello,
            "hey": self._cmd_hello,
        }
        
        # Pattern commands (with arguments)
        self.PATTERN_COMMANDS = [
            (r"^switch\s+(?:to\s+)?(.+)$", self._cmd_switch),
            (r"^add\s+(\+?\d+)\s+(.+)$", self._cmd_add_member),
            (r"^remove\s+(\+?\d+)$", self._cmd_remove_member),
            (r"^search\s+(.+)$", self._cmd_search),
        ]
    
    def parse(self, message: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Parse message and return command + args if it's a command
        
        Returns:
            (command_name, args) if command found
            (None, None) if not a command (regular query)
        """
        message = message.strip()
        message_lower = message.lower()
        
        # Check simple commands
        if message_lower in self.COMMANDS:
            return message_lower, {}
        
        # Check pattern commands
        for pattern, handler in self.PATTERN_COMMANDS:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                return handler.__name__, {"match": match}
        
        # Not a command
        return None, None
    
    def is_command(self, message: str) -> bool:
        """Check if message is a command"""
        cmd, _ = self.parse(message)
        return cmd is not None
    
    # =========================================================================
    # COMMAND HANDLERS (return response text)
    # =========================================================================
    
    def _cmd_help(self, **kwargs) -> str:
        """Help command"""
        return """
🏗️ *SiteMind Commands*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*BASICS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`help` - Show this message
`project` - Current project info
`projects` - List all projects
`switch to [name]` - Switch project

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*REPORTS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`brief` - Today's brief
`report` - Weekly report
`roi` - ROI summary
`status` - Usage stats

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*TEAM*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`team` - List team members
`add +91xxx Name` - Add member
`remove +91xxx` - Remove member

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*SEARCH*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

`search [query]` - Search project memory

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*ASK ANYTHING*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Just type your question! I know:
• IS codes & standards
• Material specifications
• Construction best practices
• Quality checks
• Safety guidelines

📸 Send photos for AI analysis
📄 Send documents for review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    def _cmd_hello(self, **kwargs) -> str:
        """Greeting response"""
        return """
👋 Hello! I'm SiteMind, your AI construction assistant.

I can help you with:
• 📐 Technical questions (specs, codes, materials)
• 📸 Photo analysis (quality, safety, progress)
• 📄 Document review
• 🔍 Project memory search

Just ask anything or send a photo!

_Type `help` for all commands_
"""
    
    def _cmd_projects(self, **kwargs) -> str:
        """List projects - actual implementation in router"""
        return "__PROJECTS__"  # Placeholder, handled in router
    
    def _cmd_current_project(self, **kwargs) -> str:
        """Current project - actual implementation in router"""
        return "__CURRENT_PROJECT__"
    
    def _cmd_switch(self, **kwargs) -> str:
        """Switch project - actual implementation in router"""
        return "__SWITCH__"
    
    def _cmd_status(self, **kwargs) -> str:
        """Usage status - actual implementation in router"""
        return "__STATUS__"
    
    def _cmd_roi(self, **kwargs) -> str:
        """ROI report - actual implementation in router"""
        return "__ROI__"
    
    def _cmd_report(self, **kwargs) -> str:
        """Weekly report - actual implementation in router"""
        return "__REPORT__"
    
    def _cmd_brief(self, **kwargs) -> str:
        """Daily brief - actual implementation in router"""
        return "__BRIEF__"
    
    def _cmd_team(self, **kwargs) -> str:
        """Team list - actual implementation in router"""
        return "__TEAM__"
    
    def _cmd_add_member(self, **kwargs) -> str:
        """Add team member - actual implementation in router"""
        return "__ADD_MEMBER__"
    
    def _cmd_remove_member(self, **kwargs) -> str:
        """Remove team member - actual implementation in router"""
        return "__REMOVE_MEMBER__"
    
    def _cmd_search(self, **kwargs) -> str:
        """Search memory - actual implementation in router"""
        return "__SEARCH__"
    
    # =========================================================================
    # INTENT DETECTION
    # =========================================================================
    
    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect user intent from message
        
        Returns intent classification for non-command messages
        """
        message_lower = message.lower()
        
        # Safety-related
        safety_keywords = ["safety", "accident", "injury", "fall", "collapse", "danger"]
        if any(kw in message_lower for kw in safety_keywords):
            return {"intent": "safety", "priority": "high"}
        
        # Urgent
        urgent_keywords = ["urgent", "immediately", "asap", "emergency", "stop"]
        if any(kw in message_lower for kw in urgent_keywords):
            return {"intent": "urgent", "priority": "high"}
        
        # Code/specification query
        code_keywords = ["is code", "nbc", "specification", "as per", "standard"]
        if any(kw in message_lower for kw in code_keywords):
            return {"intent": "code_query", "priority": "normal"}
        
        # Material query
        material_keywords = ["concrete", "steel", "cement", "rebar", "brick", "grade"]
        if any(kw in message_lower for kw in material_keywords):
            return {"intent": "material_query", "priority": "normal"}
        
        # Dimension/measurement
        if re.search(r"\d+\s*(mm|cm|m|inch|feet|ft)", message_lower):
            return {"intent": "dimension_query", "priority": "normal"}
        
        # General question
        question_patterns = ["what", "how", "why", "when", "can", "should", "is it", "?"]
        if any(qp in message_lower for qp in question_patterns):
            return {"intent": "question", "priority": "normal"}
        
        # Default
        return {"intent": "general", "priority": "normal"}
    
    # =========================================================================
    # QUICK REPLIES
    # =========================================================================
    
    def get_quick_replies(self, context: str = "default") -> str:
        """Get suggested quick replies based on context"""
        
        replies = {
            "default": [
                "What's the cover for columns?",
                "Check this photo",
                "Show my projects",
            ],
            "after_answer": [
                "Tell me more",
                "What's the IS code?",
                "Any safety concerns?",
            ],
            "after_photo": [
                "Any quality issues?",
                "Is this safe?",
                "What stage is this?",
            ],
            "project_list": [
                "Switch to [project]",
                "Show status",
                "Today's brief",
            ],
        }
        
        suggestions = replies.get(context, replies["default"])
        
        return "\n💬 _Quick replies:_\n" + "\n".join(f"• {s}" for s in suggestions)


# Singleton
command_handler = CommandHandler()

