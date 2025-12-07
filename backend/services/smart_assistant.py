"""
SiteMind Smart Assistant
Enterprise-grade query processing with edge case handling

FEATURES:
1. Multi-language support (Hindi-English code switching)
2. Typo tolerance ("beem" → "beam")
3. Context memory (follow-up questions)
4. Ambiguity resolution (clarifying questions)
5. Conflict detection (flags contradictions)
6. Urgency detection (prioritizes critical queries)
7. Professional response formatting
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum


class QueryUrgency(str, Enum):
    CRITICAL = "critical"      # Safety, structural, active pour
    HIGH = "high"              # Needs answer within minutes
    NORMAL = "normal"          # Regular query
    LOW = "low"                # Can wait


class QueryCategory(str, Enum):
    STRUCTURAL = "structural"
    ARCHITECTURAL = "architectural"
    MEP = "mep"
    MATERIAL = "material"
    SAFETY = "safety"
    SCHEDULE = "schedule"
    COST = "cost"
    GENERAL = "general"
    OUT_OF_SCOPE = "out_of_scope"


# =============================================================================
# LANGUAGE HANDLING - Hindi/English/Regional Code Switching
# =============================================================================

# Common Hindi construction terms → English
HINDI_TO_ENGLISH = {
    # Structural
    "khamba": "column",
    "pillar": "column", 
    "sthambh": "column",
    "beam": "beam",
    "beem": "beam",
    "girder": "beam",
    "slab": "slab",
    "chhat": "slab",
    "ceiling": "slab",
    "neev": "foundation",
    "buniyad": "foundation",
    "foundation": "foundation",
    "deewar": "wall",
    "wall": "wall",
    "seedi": "staircase",
    "stairs": "staircase",
    
    # Materials
    "sariya": "rebar",
    "rod": "rebar",
    "rebar": "rebar",
    "steel": "steel",
    "loha": "steel",
    "cement": "cement",
    "concrete": "concrete",
    "eet": "brick",
    "brick": "brick",
    
    # Actions
    "dalna": "pour",
    "pour": "pour",
    "casting": "pour",
    "dhalna": "pour",
    "check": "verify",
    "dekho": "verify",
    "batao": "tell",
    "bolo": "tell",
    "kya": "what",
    "kahan": "where",
    "kitna": "how much",
    "kaisa": "how",
    "kab": "when",
    
    # Measurements
    "lambai": "length",
    "chaudai": "width",
    "unchai": "height",
    "gadhai": "depth",
    "mota": "thick",
    "patla": "thin",
    
    # Common phrases
    "sahi hai": "is correct",
    "galat hai": "is wrong",
    "theek hai": "okay",
    "samajh nahi aaya": "didn't understand",
    "dobara batao": "tell again",
    "jaldi": "urgent",
    "abhi": "now",
    "turant": "immediately",
}

# Common typos → corrections
TYPO_CORRECTIONS = {
    "beem": "beam",
    "bem": "beam",
    "colum": "column",
    "coloumn": "column",
    "columm": "column",
    "slb": "slab",
    "slaab": "slab",
    "rber": "rebar",
    "rebr": "rebar",
    "founation": "foundation",
    "foundatin": "foundation",
    "spacin": "spacing",
    "spacng": "spacing",
    "dimeter": "diameter",
    "diamter": "diameter",
    "reinfrcement": "reinforcement",
    "reinforcment": "reinforcement",
    "drwing": "drawing",
    "drawng": "drawing",
    "flor": "floor",
    "florr": "floor",
    "grd": "grid",
    "gridd": "grid",
}

# Urgency keywords
URGENCY_CRITICAL = [
    "safety", "emergency", "danger", "collapse", "crack", "urgent", 
    "khatarnak", "danger", "immediately", "abhi", "turant", "jaldi",
    "active pour", "casting chal raha", "pouring now", "wet concrete"
]

URGENCY_HIGH = [
    "asap", "quickly", "fast", "jaldi", "fatafat",
    "waiting", "ruk gaya", "work stopped", "kaam ruka"
]


class SmartAssistant:
    """
    Handles all the edge cases to make SiteMind addictive
    """
    
    def __init__(self):
        # Conversation context (per user)
        self._context: Dict[str, Dict] = {}
        
        # User stats (for gamification)
        self._user_stats: Dict[str, Dict] = {}
        
        # Daily summaries
        self._daily_queries: Dict[str, List] = {}
    
    # =========================================================================
    # LANGUAGE PROCESSING
    # =========================================================================
    
    def normalize_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Normalize query - handle Hindi, typos, informal language
        
        Returns: (normalized_query, metadata)
        """
        original = query
        normalized = query.lower().strip()
        
        # Track what we changed
        changes = []
        
        # Fix typos
        for typo, correct in TYPO_CORRECTIONS.items():
            if typo in normalized:
                normalized = normalized.replace(typo, correct)
                changes.append(f"typo:{typo}→{correct}")
        
        # Translate Hindi terms (keep both for context)
        hindi_terms_found = []
        for hindi, english in HINDI_TO_ENGLISH.items():
            if hindi in normalized and hindi != english:
                hindi_terms_found.append(f"{hindi}={english}")
        
        # Detect urgency
        urgency = self._detect_urgency(normalized)
        
        # Detect category
        category = self._detect_category(normalized)
        
        # Check for ambiguity
        ambiguities = self._detect_ambiguity(normalized)
        
        return normalized, {
            "original": original,
            "changes": changes,
            "hindi_terms": hindi_terms_found,
            "urgency": urgency,
            "category": category,
            "ambiguities": ambiguities,
            "needs_clarification": len(ambiguities) > 0,
        }
    
    def _detect_urgency(self, query: str) -> QueryUrgency:
        """Detect how urgent the query is"""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in URGENCY_CRITICAL):
            return QueryUrgency.CRITICAL
        if any(kw in query_lower for kw in URGENCY_HIGH):
            return QueryUrgency.HIGH
        
        return QueryUrgency.NORMAL
    
    def _detect_category(self, query: str) -> QueryCategory:
        """Categorize the query"""
        query_lower = query.lower()
        
        structural_kw = ["beam", "column", "slab", "foundation", "rebar", "reinforcement", "structural"]
        architectural_kw = ["floor plan", "layout", "elevation", "section", "architectural", "room"]
        mep_kw = ["electrical", "plumbing", "hvac", "duct", "pipe", "wire", "mep", "ac"]
        material_kw = ["cement", "concrete", "steel", "brick", "sand", "aggregate", "material"]
        safety_kw = ["safety", "danger", "ppe", "harness", "helmet", "fall"]
        cost_kw = ["cost", "price", "rate", "budget", "kitna paisa", "kharcha"]
        
        if any(kw in query_lower for kw in safety_kw):
            return QueryCategory.SAFETY
        if any(kw in query_lower for kw in structural_kw):
            return QueryCategory.STRUCTURAL
        if any(kw in query_lower for kw in mep_kw):
            return QueryCategory.MEP
        if any(kw in query_lower for kw in architectural_kw):
            return QueryCategory.ARCHITECTURAL
        if any(kw in query_lower for kw in material_kw):
            return QueryCategory.MATERIAL
        if any(kw in query_lower for kw in cost_kw):
            return QueryCategory.COST
        
        # Check for out of scope
        out_of_scope_kw = ["weather", "mausam", "cricket", "movie", "film", "news"]
        if any(kw in query_lower for kw in out_of_scope_kw):
            return QueryCategory.OUT_OF_SCOPE
        
        return QueryCategory.GENERAL
    
    def _detect_ambiguity(self, query: str) -> List[str]:
        """Detect ambiguous queries that need clarification"""
        ambiguities = []
        
        # Check for missing location
        location_needed = ["beam", "column", "slab", "wall"]
        has_location = any(loc in query for loc in ["at", "pe", "par", "grid", "floor", "level", "axis"])
        
        if any(item in query for item in location_needed) and not has_location:
            ambiguities.append("missing_location")
        
        # Check for missing floor
        if any(f"floor" not in query and f"level" not in query and "manzil" not in query 
               for _ in [1]) and any(item in query for item in location_needed):
            if not any(char.isdigit() for char in query):
                ambiguities.append("missing_floor")
        
        # Generic "size" without specifying what
        if "size" in query or "dimension" in query:
            specific_items = ["beam", "column", "slab", "footing", "pile"]
            if not any(item in query for item in specific_items):
                ambiguities.append("missing_element_type")
        
        return ambiguities
    
    # =========================================================================
    # CONTEXT MANAGEMENT (Follow-up questions)
    # =========================================================================
    
    def get_context(self, user_phone: str) -> Dict[str, Any]:
        """Get conversation context for a user"""
        if user_phone not in self._context:
            self._context[user_phone] = {
                "last_query": None,
                "last_topic": None,
                "last_location": None,
                "last_element": None,
                "last_response": None,
                "timestamp": None,
                "query_count_today": 0,
            }
        return self._context[user_phone]
    
    def update_context(
        self, 
        user_phone: str, 
        query: str, 
        response: str,
        topic: Optional[str] = None,
        location: Optional[str] = None,
        element: Optional[str] = None,
    ):
        """Update conversation context after a query"""
        ctx = self.get_context(user_phone)
        ctx["last_query"] = query
        ctx["last_response"] = response
        ctx["last_topic"] = topic or ctx["last_topic"]
        ctx["last_location"] = location or ctx["last_location"]
        ctx["last_element"] = element or ctx["last_element"]
        ctx["timestamp"] = datetime.utcnow().isoformat()
        ctx["query_count_today"] = ctx.get("query_count_today", 0) + 1
    
    def is_followup_query(self, user_phone: str, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if this is a follow-up to previous query
        
        Examples:
        - Previous: "Beam size at B2?"
        - Follow-up: "And the reinforcement?" → Should understand it's about B2
        """
        ctx = self.get_context(user_phone)
        
        if not ctx["last_query"]:
            return False, None
        
        # Check if recent (within 10 minutes)
        if ctx["timestamp"]:
            last_time = datetime.fromisoformat(ctx["timestamp"])
            if datetime.utcnow() - last_time > timedelta(minutes=10):
                return False, None
        
        # Follow-up indicators
        followup_phrases = [
            "and ", "aur ", "also", "bhi", "what about", "kya", 
            "same", "wahi", "usme", "iska", "uska",
            "reinforcement", "spacing", "size", "detail"
        ]
        
        query_lower = query.lower()
        
        # Short query that references previous context
        if len(query.split()) <= 5 and any(fp in query_lower for fp in followup_phrases):
            # Build context string
            context = f"Following up on: {ctx['last_query']}"
            if ctx["last_location"]:
                context += f" at {ctx['last_location']}"
            if ctx["last_element"]:
                context += f" ({ctx['last_element']})"
            
            return True, context
        
        return False, None
    
    # =========================================================================
    # CLARIFICATION REQUESTS
    # =========================================================================
    
    def generate_clarification(self, query: str, ambiguities: List[str]) -> str:
        """Generate a helpful clarification request"""
        
        clarifications = []
        
        if "missing_location" in ambiguities:
            clarifications.append("📍 Which grid/axis? (e.g., 'B2' or 'grid A-C')")
        
        if "missing_floor" in ambiguities:
            clarifications.append("🏢 Which floor/level? (e.g., '3rd floor' or 'basement')")
        
        if "missing_element_type" in ambiguities:
            clarifications.append("🔧 Size of what? (beam, column, slab, footing?)")
        
        if not clarifications:
            return ""
        
        response = "I want to give you the exact answer. Can you clarify:\n\n"
        response += "\n".join(clarifications)
        response += "\n\nExample: 'Beam size at B2, 3rd floor'"
        
        return response
    
    # =========================================================================
    # CONFLICT DETECTION
    # =========================================================================
    
    def check_for_conflicts(
        self, 
        query: str, 
        memory_results: List[Dict],
        blueprint_info: Optional[str] = None
    ) -> Optional[str]:
        """
        Check if there are conflicting pieces of information
        
        Example: Memory says "beam changed to 600mm" but blueprint shows 450mm
        """
        # This would be enhanced with actual comparison logic
        # For now, flag if there are multiple change orders for same element
        
        change_orders = [m for m in memory_results if m.get("metadata", {}).get("type") == "change_order"]
        
        if len(change_orders) > 1:
            # Multiple change orders - check if they're for same element
            # Simplified: just warn
            return "⚠️ Note: There have been multiple changes to this element. Showing the latest."
        
        return None
    
    # =========================================================================
    # PROACTIVE FEATURES
    # =========================================================================
    
    def get_proactive_alerts(self, project_id: str, user_phone: str) -> List[str]:
        """
        Generate proactive alerts for the user
        
        Examples:
        - "Drawing SK-003 was updated 2 hours ago"
        - "3 engineers asked about Beam B2 today - there might be confusion"
        - "You haven't confirmed the stirrup fix from yesterday"
        """
        alerts = []
        
        # Would check:
        # - Recent drawing uploads
        # - Unresolved issues
        # - Trending questions (many people asking same thing)
        # - Follow-up reminders
        
        return alerts
    
    def generate_daily_summary(self, project_id: str, user_phone: str) -> str:
        """
        Generate daily summary for a user
        
        "Today you asked 23 questions and saved ~4 hours.
        SiteMind caught 2 potential issues before they became problems."
        """
        # Would pull from actual stats
        return ""
    
    # =========================================================================
    # USER METRICS (Professional, no gamification)
    # =========================================================================
    
    def get_user_stats(self, user_phone: str) -> Dict[str, Any]:
        """Get usage stats for a user"""
        if user_phone not in self._user_stats:
            self._user_stats[user_phone] = {
                "total_queries": 0,
                "issues_flagged": 0,
                "first_query_date": None,
            }
        return self._user_stats[user_phone]
    
    def record_query(self, user_phone: str):
        """Record a query"""
        stats = self.get_user_stats(user_phone)
        stats["total_queries"] += 1
        
        if not stats["first_query_date"]:
            stats["first_query_date"] = datetime.utcnow().isoformat()
    
    # =========================================================================
    # OUT OF SCOPE HANDLING
    # =========================================================================
    
    def handle_out_of_scope(self, query: str) -> str:
        """Handle queries that are out of scope professionally"""
        
        out_of_scope_responses = {
            "weather": "I'm configured to assist with construction project queries. For weather information, please use a weather service.\n\nHow can I help with the project?",
            "cricket": "I'm configured to assist with construction project queries only.\n\nHow can I help with blueprints, specifications, or project details?",
            "hello": "Hello. I'm SiteMind, your AI construction assistant. I can answer questions about blueprints, specifications, change orders, and project history.\n\nWhat do you need to know?",
            "thanks": "You're welcome. Feel free to ask if you have more questions about the project.",
            "who are you": "I'm SiteMind, an AI assistant for construction projects. I have access to your project's blueprints, specifications, RFIs, change orders, and decision history.\n\nExample query: 'Beam size at B2, floor 3'",
            "help": "I can help with:\n• Blueprint specifications\n• Rebar and structural details\n• Change order history\n• RFI lookups\n• Site photo verification\n\nWhat do you need?",
        }
        
        query_lower = query.lower()
        
        for keyword, response in out_of_scope_responses.items():
            if keyword in query_lower:
                return response
        
        return "I'm configured to assist with construction project queries - blueprints, specifications, materials, and project documentation. How can I help?"
    
    # =========================================================================
    # PROACTIVE SUGGESTIONS
    # =========================================================================
    
    def get_suggestions(self, project_id: str, recent_queries: List[str]) -> List[str]:
        """
        Generate relevant suggestions based on query patterns
        """
        suggestions = []
        # Would analyze patterns and suggest relevant actions
        return suggestions
    
    # =========================================================================
    # RESPONSE ENHANCEMENT
    # =========================================================================
    
    def enhance_response(
        self, 
        response: str, 
        urgency: QueryUrgency,
        category: QueryCategory,
        user_stats: Dict,
    ) -> str:
        """
        Enhance response based on context
        
        - Add warnings for safety queries
        - Adjust formatting based on urgency
        - Keep professional tone
        """
        enhanced = response
        
        # Safety queries get clear warning
        if category == QueryCategory.SAFETY:
            enhanced = "**⚠️ SAFETY-RELATED QUERY**\n\n" + enhanced
            enhanced += "\n\n_Note: For safety-critical work, always verify with site supervisor and follow established protocols._"
        
        # Urgent queries get priority indicator
        if urgency == QueryUrgency.CRITICAL:
            enhanced = "**PRIORITY RESPONSE**\n\n" + enhanced
        
        return enhanced


# Singleton instance
smart_assistant = SmartAssistant()

