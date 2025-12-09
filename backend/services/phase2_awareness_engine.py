"""
PHASE 2: CONSTRUCTION AWARENESS ENGINE
=======================================

Make SiteMind behave like a senior engineer who knows:
- Drawings and their revisions
- RFIs and dependencies
- Issue timelines
- Approval chains

ALL TEXT-BASED. NO COMPUTER VISION.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from services.memory_service import memory_service
from services.gemini_service import gemini_service
from services.phase1_memory_engine import memory_engine
from utils.logger import logger


@dataclass
class Issue:
    id: str
    description: str
    reported_by: str
    reported_at: datetime
    location: str = None
    severity: str = "medium"  # high, medium, low
    status: str = "open"  # open, in_progress, resolved
    work_type: str = None
    resolution: str = None
    resolved_at: datetime = None


@dataclass
class ProgressUpdate:
    id: str
    work_type: str
    location: str
    description: str
    reported_by: str
    reported_at: datetime
    completion_percentage: float = None


class ConstructionAwarenessEngine:
    """
    Phase 2: Senior Engineer Intelligence
    
    - Drawing Q&A with citations
    - Revision intelligence
    - Issue detection & timelines
    - Approver tracking
    - Text-based progress tracking
    """
    
    def __init__(self):
        self._issues: Dict[str, List[Issue]] = {}
        self._progress: Dict[str, List[ProgressUpdate]] = {}
        self._approvers: Dict[str, Dict[str, str]] = {}  # Who is responsible for what
    
    # =========================================================================
    # 1. PROJECT KNOWLEDGE Q&A (HONEST)
    # =========================================================================
    
    async def answer_drawing_question(
        self,
        question: str,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Answer questions from PROJECT MEMORY (what was discussed/logged)
        
        HONEST: We can only answer from:
        - Decisions that were logged
        - Phone calls that were logged
        - RFI responses
        - Progress updates
        - Issues reported
        - General discussions
        
        We CANNOT read actual drawing content.
        If info isn't in memory, we say so and offer to send relevant files.
        """
        
        # Search stored memories
        context = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query=question,
            limit=10,
        )
        
        if not context:
            return {
                "answer": f"I don't have that information in my records yet.\n\nThis could be because:\n• It hasn't been discussed/logged yet\n• The relevant drawing hasn't been uploaded\n\n💡 If you find the answer, tell me and I'll remember it!",
                "citations": [],
                "found": False,
            }
        
        # Format for LLM
        context_text = "\n".join([
            f"SOURCE {i+1}: {item.get('content', str(item))[:400]}"
            for i, item in enumerate(context[:8])
        ])
        
        prompt = f"""Answer this question using ONLY the provided project records.

QUESTION: {question}

PROJECT RECORDS:
{context_text}

INSTRUCTIONS:
1. Answer using ONLY information from the records above
2. Cite who said it and when (e.g., "According to PM on 15-Dec...")
3. If the exact info isn't in the records, say "I don't have that logged"
4. NEVER make up specifications or dimensions
5. If a drawing was mentioned, note we have it stored but can't read its contents

Be helpful but honest. If unsure, say so."""

        try:
            answer = await gemini_service._generate(prompt)
            
            # Extract any drawing references
            citations = []
            for item in context[:3]:
                meta = item.get("metadata", {})
                if meta.get("file_name"):
                    citations.append({
                        "file": meta.get("file_name"),
                        "uploaded_by": meta.get("uploaded_by", "Unknown"),
                    })
            
            return {
                "answer": answer,
                "citations": citations,
                "found": True,
            }
            
        except Exception as e:
            logger.error(f"Q&A error: {e}")
            return {
                "answer": "I encountered an error. Please try again.",
                "citations": [],
                "found": False,
            }
    
    # =========================================================================
    # 2. REVISION TRACKING (HONEST - Based on filenames/metadata only)
    # =========================================================================
    
    async def check_revision(
        self,
        drawing_name: str,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Check what versions of a drawing we have stored
        
        HONEST: We can only tell you:
        - What files are stored
        - What revision number was in the filename
        - Who uploaded it and when
        
        We CANNOT compare actual drawing content.
        """
        
        # Search for stored drawings
        results = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query=f"drawing {drawing_name}",
            limit=15,
        )
        
        if not results:
            return {
                "drawing": drawing_name,
                "found": False,
                "message": f"No files found matching '{drawing_name}'. Upload the drawing to start tracking.",
            }
        
        # Extract file info from results
        files = []
        for item in results:
            meta = item.get("metadata", {})
            if meta.get("file_name"):
                files.append({
                    "file": meta.get("file_name"),
                    "revision": meta.get("revision"),
                    "uploaded_by": meta.get("uploaded_by"),
                })
        
        if not files:
            return {
                "drawing": drawing_name,
                "found": True,
                "message": f"Found mentions of {drawing_name} but no stored files.",
                "mentions": len(results),
            }
        
        # Sort by revision if available
        files_with_rev = [f for f in files if f.get("revision")]
        latest = files_with_rev[-1] if files_with_rev else files[0]
        
        return {
            "drawing": drawing_name,
            "found": True,
            "latest_file": latest.get("file"),
            "latest_revision": latest.get("revision"),
            "latest_uploaded_by": latest.get("uploaded_by"),
            "all_versions": files,
            "message": f"Found {len(files)} version(s) of {drawing_name}",
        }
    
    async def compare_revisions(
        self,
        drawing_name: str,
        company_id: str,
        project_id: str,
    ) -> str:
        """
        List versions we have stored
        
        HONEST: We CANNOT compare actual drawing content.
        We can only list what files are stored.
        """
        
        result = await self.check_revision(drawing_name, company_id, project_id)
        
        if not result.get("found"):
            return result.get("message", f"No files found for {drawing_name}")
        
        files = result.get("all_versions", [])
        
        if len(files) < 2:
            return f"Only one version of {drawing_name} found:\n• {files[0].get('file')} (uploaded by {files[0].get('uploaded_by', 'Unknown')})"
        
        response = f"📁 Versions of {drawing_name}:\n\n"
        for f in files:
            rev = f.get("revision", "Unknown")
            response += f"• {f.get('file')} - Rev {rev}\n  Uploaded by: {f.get('uploaded_by', 'Unknown')}\n\n"
        
        response += "\n⚠️ Note: I can send you these files, but I cannot compare their actual content."
        
        return response
    
    # =========================================================================
    # 3. ISSUE DETECTION (TEXT-BASED)
    # =========================================================================
    
    async def detect_issue(
        self,
        message: str,
        sender: str,
        company_id: str,
        project_id: str,
    ) -> Optional[Issue]:
        """
        Detect and log issues from text messages
        
        Examples:
        - "Leakage noticed in 1002"
        - "Tiles cracked"
        - "Blockwork delayed"
        - "Plaster not acceptable"
        """
        
        prompt = f"""Analyze if this message reports a construction issue.

MESSAGE: "{message}"

Return JSON:
{{
  "is_issue": true/false,
  "severity": "high|medium|low",
  "work_type": "plumbing|electrical|structural|finishing|etc",
  "location": "location mentioned or null",
  "summary": "brief issue summary"
}}

Examples of issues:
- Leakage, crack, damage, delay
- Quality problems
- Material issues
- Work not acceptable"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response)
            
            if result and result.get("is_issue"):
                key = f"{company_id}_{project_id}"
                if key not in self._issues:
                    self._issues[key] = []
                
                issue = Issue(
                    id=f"ISS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    description=message,
                    reported_by=sender,
                    reported_at=datetime.utcnow(),
                    location=result.get("location"),
                    severity=result.get("severity", "medium"),
                    work_type=result.get("work_type"),
                )
                
                self._issues[key].append(issue)
                
                # Store in memory
                await memory_service.add_memory(
                    company_id=company_id,
                    project_id=project_id,
                    content=f"ISSUE [{issue.severity.upper()}]: {issue.description} (Location: {issue.location or 'Not specified'}, Type: {issue.work_type or 'General'})",
                    memory_type="issue",
                    metadata={
                        "issue_id": issue.id,
                        "severity": issue.severity,
                        "location": issue.location,
                    },
                    user_id=sender,
                )
                
                logger.info(f"⚠️ Issue detected: {issue.id}")
                return issue
            
            return None
            
        except Exception as e:
            logger.error(f"Issue detection error: {e}")
            return None
    
    # =========================================================================
    # 4. ISSUE TIMELINE
    # =========================================================================
    
    async def get_issue_timeline(
        self,
        query: str,
        company_id: str,
        project_id: str,
    ) -> str:
        """
        Get full history of an issue
        
        Example: "Show the full history of the shaft leak issue"
        
        Fetches:
        - All messages
        - All RFIs
        - All decisions
        - All updates
        - Related drawings
        """
        
        # Search for all related content
        results = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query=query,
            limit=25,
        )
        
        if not results:
            return f"No records found related to: {query}"
        
        results_text = "\n".join([
            f"[{item.get('metadata', {}).get('timestamp', 'Unknown date')}] {item.get('content', str(item))[:200]}"
            for item in results
        ])
        
        prompt = f"""Create a timeline for this issue/topic.

QUERY: {query}

ALL RELATED RECORDS:
{results_text}

Create a chronological timeline showing:
1. When it was first reported
2. All related messages
3. Any RFIs raised
4. Any decisions made
5. Current status

Format as a clear timeline."""

        try:
            return await gemini_service._generate(prompt)
        except Exception as e:
            return f"Found {len(results)} related records."
    
    # =========================================================================
    # 5. APPROVER TRACKING
    # =========================================================================
    
    async def detect_approver(
        self,
        message: str,
        sender: str,
        company_id: str,
        project_id: str,
    ) -> Optional[Dict[str, str]]:
        """
        Detect who is responsible from text
        
        Examples:
        - "Consultant will review tomorrow"
        - "Awaiting PMC response"
        - "Approved by structural engineer"
        """
        
        prompt = f"""Analyze if this message mentions someone responsible for an action.

MESSAGE: "{message}"

Return JSON:
{{
  "has_responsibility": true/false,
  "responsible_party": "who is responsible",
  "action": "what they need to do",
  "status": "pending|approved|rejected|in_review"
}}"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response)
            
            if result and result.get("has_responsibility"):
                key = f"{company_id}_{project_id}"
                if key not in self._approvers:
                    self._approvers[key] = {}
                
                # Track who is responsible for what
                action = result.get("action", "Unknown action")
                self._approvers[key][action] = {
                    "responsible": result.get("responsible_party"),
                    "status": result.get("status"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Approver detection error: {e}")
            return None
    
    # =========================================================================
    # 6. PROGRESS TRACKING (TEXT-BASED)
    # =========================================================================
    
    async def detect_progress(
        self,
        message: str,
        sender: str,
        company_id: str,
        project_id: str,
    ) -> Optional[ProgressUpdate]:
        """
        Detect progress updates from text
        
        Examples:
        - "Brickwork completed on Level 10"
        - "Plaster completed in 1204"
        - "Formwork ready for casting tomorrow"
        """
        
        prompt = f"""Analyze if this message is a progress update.

MESSAGE: "{message}"

Return JSON:
{{
  "is_progress": true/false,
  "work_type": "brickwork|plaster|formwork|electrical|plumbing|etc",
  "location": "where the work was done",
  "status": "completed|in_progress|planned",
  "completion_percentage": number or null
}}"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response)
            
            if result and result.get("is_progress"):
                key = f"{company_id}_{project_id}"
                if key not in self._progress:
                    self._progress[key] = []
                
                update = ProgressUpdate(
                    id=f"PRG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    work_type=result.get("work_type", "General"),
                    location=result.get("location", "Not specified"),
                    description=message,
                    reported_by=sender,
                    reported_at=datetime.utcnow(),
                    completion_percentage=result.get("completion_percentage"),
                )
                
                self._progress[key].append(update)
                
                # Store in memory
                await memory_service.add_memory(
                    company_id=company_id,
                    project_id=project_id,
                    content=f"PROGRESS: {update.work_type} at {update.location} - {message}",
                    memory_type="progress",
                    metadata={
                        "work_type": update.work_type,
                        "location": update.location,
                        "completion": update.completion_percentage,
                    },
                    user_id=sender,
                )
                
                return update
            
            return None
            
        except Exception as e:
            logger.error(f"Progress detection error: {e}")
            return None
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text"""
        import re
        try:
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return None
        except:
            return None
    
    def get_open_issues(self, company_id: str, project_id: str) -> List[Issue]:
        """Get all open issues"""
        key = f"{company_id}_{project_id}"
        if key not in self._issues:
            return []
        return [i for i in self._issues[key] if i.status == "open"]
    
    def get_stats(self, company_id: str, project_id: str) -> Dict[str, Any]:
        """Get awareness stats"""
        key = f"{company_id}_{project_id}"
        
        issues = self._issues.get(key, [])
        progress = self._progress.get(key, [])
        
        return {
            "total_issues": len(issues),
            "open_issues": len([i for i in issues if i.status == "open"]),
            "high_severity_issues": len([i for i in issues if i.severity == "high" and i.status == "open"]),
            "progress_updates": len(progress),
        }


# Singleton
awareness_engine = ConstructionAwarenessEngine()

