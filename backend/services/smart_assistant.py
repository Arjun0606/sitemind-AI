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

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re


class QueryUrgency(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class QueryCategory(str, Enum):
    STRUCTURAL = "structural"
    ARCHITECTURAL = "architectural"
    MEP = "mep"
    MATERIAL = "material"
    SAFETY = "safety"
    GENERAL = "general"


class SmartAssistantService:
    """
    Advanced query processing for construction queries
    """
    
    def __init__(self):
        # Context memory for follow-up questions
        self._context: Dict[str, Dict] = {}  # phone -> {last_query, last_response, timestamp}
        self._context_timeout = timedelta(minutes=10)
        
        # User stats
        self._user_stats: Dict[str, Dict] = {}
        
        # Common Hindi-English mappings
        self.term_mappings = {
            # Structural elements
            "khamba": "column",
            "pillar": "column",
            "beem": "beam",
            "chhat": "slab",
            "neev": "foundation",
            "buniyad": "foundation",
            "deewar": "wall",
            "seedi": "staircase",
            
            # Materials
            "sariya": "rebar",
            "rod": "rebar",
            "cement": "cement",
            "bajri": "aggregate",
            "reta": "sand",
            "eent": "brick",
            
            # Typos
            "colum": "column",
            "colmn": "column",
            "beem": "beam",
            "fondation": "foundation",
            "stiars": "stairs",
            "staircase": "staircase",
        }
        
        # Urgency keywords
        self.urgency_keywords = {
            "critical": ["urgent", "emergency", "immediately", "asap", "jaldi", "abhi", "turant", "critical"],
            "high": ["today", "now", "quick", "fast", "jald"],
            "normal": [],
            "low": ["when you can", "no rush", "later"],
        }
    
    # =========================================================================
    # QUERY PREPROCESSING
    # =========================================================================
    
    def preprocess_query(self, query: str) -> Dict[str, Any]:
        """
        Preprocess query for better understanding
        
        Returns normalized query and extracted information
        """
        original = query
        processed = query.lower().strip()
        
        # Apply term mappings
        for hindi, english in self.term_mappings.items():
            processed = processed.replace(hindi, english)
        
        # Extract location references
        location = self._extract_location(query)
        
        # Check for ambiguity
        needs_clarification = self._needs_clarification(processed, location)
        
        return {
            "original_query": original,
            "normalized_query": processed,
            "location": location,
            "needs_clarification": needs_clarification is not None,
            "clarification_question": needs_clarification,
        }
    
    def _extract_location(self, query: str) -> Dict[str, Any]:
        """Extract location references from query"""
        location = {}
        
        # Grid reference (e.g., B3, C4)
        grid_match = re.search(r'\b([A-Z]\d+)\b', query, re.IGNORECASE)
        if grid_match:
            location["grid"] = grid_match.group(1).upper()
        
        # Floor number
        floor_match = re.search(r'(?:floor|fl|level|lvl|manzil)\s*(\d+)', query, re.IGNORECASE)
        if floor_match:
            location["floor"] = int(floor_match.group(1))
        
        # Element type
        elements = ["beam", "column", "slab", "foundation", "wall", "staircase"]
        for elem in elements:
            if elem in query.lower():
                location["element"] = elem
                break
        
        return location
    
    def _needs_clarification(self, query: str, location: Dict) -> Optional[str]:
        """Check if query needs clarification"""
        
        # Has element but no location
        if location.get("element") and not location.get("grid") and not location.get("floor"):
            element = location["element"]
            return f"Which {element} are you asking about? Please specify the grid reference (e.g., B3) or floor number."
        
        # Generic question without specifics
        generic_patterns = [
            r"^what(\s+is)?(\s+the)?\s*(size|dimension|spec)",
            r"^(kya|kitna)\s",
        ]
        
        for pattern in generic_patterns:
            if re.match(pattern, query) and not location:
                return "Please specify which element you're asking about. For example: 'beam size B3 floor 2' or 'column C4 rebar'"
        
        return None
    
    # =========================================================================
    # CONTEXT MANAGEMENT (Follow-up questions)
    # =========================================================================
    
    def update_context(self, phone: str, query: str, response: str):
        """Store context for follow-up questions"""
        self._context[phone] = {
            "last_query": query,
            "last_response": response,
            "last_location": self._extract_location(query),
            "timestamp": datetime.utcnow(),
        }
    
    def get_context(self, phone: str) -> Optional[Dict]:
        """Get context if still valid"""
        ctx = self._context.get(phone)
        if not ctx:
            return None
        
        # Check if expired
        if datetime.utcnow() - ctx["timestamp"] > self._context_timeout:
            del self._context[phone]
            return None
        
        return ctx
    
    def resolve_follow_up(self, phone: str, query: str) -> str:
        """Resolve follow-up question with context"""
        ctx = self.get_context(phone)
        if not ctx:
            return query
        
        # Check for follow-up patterns
        follow_up_patterns = [
            r"^(and|also)\s+(what about|how about)",
            r"^what about",
            r"^how about",
            r"^(aur|bhi)\s",
            r"^same (for|at)",
        ]
        
        query_lower = query.lower()
        is_follow_up = any(re.match(p, query_lower) for p in follow_up_patterns)
        
        if is_follow_up:
            last_location = ctx.get("last_location", {})
            
            # Inject previous location context
            if last_location.get("grid") and "grid" not in self._extract_location(query):
                query = f"{query} at {last_location['grid']}"
            if last_location.get("floor") and "floor" not in query.lower():
                query = f"{query} floor {last_location['floor']}"
        
        return query
    
    # =========================================================================
    # URGENCY & CATEGORY DETECTION
    # =========================================================================
    
    def detect_urgency(self, query: str) -> QueryUrgency:
        """Detect query urgency level"""
        query_lower = query.lower()
        
        for level, keywords in self.urgency_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return QueryUrgency(level)
        
        return QueryUrgency.NORMAL
    
    def categorize_query(self, query: str) -> QueryCategory:
        """Categorize the query type"""
        query_lower = query.lower()
        
        # Safety related
        safety_keywords = ["safety", "danger", "hazard", "protective", "ppe", "accident", "injury"]
        if any(kw in query_lower for kw in safety_keywords):
            return QueryCategory.SAFETY
        
        # Structural
        structural_keywords = ["beam", "column", "slab", "foundation", "rebar", "concrete", "structural"]
        if any(kw in query_lower for kw in structural_keywords):
            return QueryCategory.STRUCTURAL
        
        # MEP
        mep_keywords = ["electrical", "plumbing", "hvac", "pipe", "wire", "duct", "ac", "drainage"]
        if any(kw in query_lower for kw in mep_keywords):
            return QueryCategory.MEP
        
        # Material
        material_keywords = ["cement", "steel", "sand", "aggregate", "stock", "material", "quantity"]
        if any(kw in query_lower for kw in material_keywords):
            return QueryCategory.MATERIAL
        
        # Architectural
        arch_keywords = ["door", "window", "tile", "paint", "finishing", "facade"]
        if any(kw in query_lower for kw in arch_keywords):
            return QueryCategory.ARCHITECTURAL
        
        return QueryCategory.GENERAL
    
    # =========================================================================
    # CONFLICT DETECTION
    # =========================================================================
    
    def detect_conflicts(self, memory_results: List[Dict]) -> List[str]:
        """Detect conflicts in memory results"""
        conflicts = []
        
        # Check for multiple change orders on same element
        change_orders = [
            m for m in memory_results 
            if m.get("content_type") == "change_order" or 
               m.get("metadata", {}).get("type") == "change_order"
        ]
        
        if len(change_orders) >= 2:
            conflicts.append(
                f"Multiple change orders found ({len(change_orders)}). "
                "Please verify the current specification."
            )
        
        return conflicts
    
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


# Singleton instance
smart_assistant = SmartAssistantService()
