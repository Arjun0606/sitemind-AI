"""
PHASE 3: PROJECT INTELLIGENCE ENGINE
=====================================

Predictive insights using:
- Embeddings
- LLM analysis
- Simple heuristics
- Trend analysis

NO COMPUTER VISION. NO COMPLEX ML.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

from services.memory_service import memory_service
from services.gemini_service import gemini_service
from services.phase1_memory_engine import memory_engine
from services.phase2_awareness_engine import awareness_engine
from utils.logger import logger


@dataclass
class Risk:
    id: str
    description: str
    category: str  # material, labour, approval, contractor, weather
    severity: str  # high, medium, low
    detected_at: datetime
    affected_work: str = None
    mitigation: str = None


@dataclass
class ContractorScore:
    name: str
    score: float  # 0-100
    rfi_response_time_days: float
    issues_logged: int
    on_time_completion_rate: float
    last_updated: datetime


class ProjectIntelligenceEngine:
    """
    Phase 3: Predictive Intelligence
    
    - Material shortage prediction
    - Delay prediction
    - Contractor performance scoring
    - Project health reports
    - BOQ deviation alerts
    - Risk monitoring
    """
    
    def __init__(self):
        self._risks: Dict[str, List[Risk]] = {}
        self._contractor_scores: Dict[str, Dict[str, ContractorScore]] = {}
    
    # =========================================================================
    # 1. MATERIAL SHORTAGE PREDICTION
    # =========================================================================
    
    async def predict_material_shortage(
        self,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Predict material shortages based on:
        - Progress messages (consumption)
        - Delivery messages
        - BOQ data
        - Pattern analysis
        """
        
        # Get material-related messages
        context = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query="material delivery stock arrived shortage running low cement steel tiles",
            limit=20,
        )
        
        if not context:
            return {
                "predictions": [],
                "message": "No material data found. Log material deliveries and usage to enable predictions.",
            }
        
        context_text = "\n".join([
            f"- {item.get('content', str(item))[:200]}"
            for item in context
        ])
        
        prompt = f"""Analyze material status and predict shortages.

MATERIAL DATA:
{context_text}

Based on this data, predict:
1. Which materials might run short soon?
2. What's the estimated timeline?
3. What action should be taken?

Return JSON:
{{
  "predictions": [
    {{
      "material": "material name",
      "current_status": "adequate|low|critical",
      "days_until_shortage": number or null,
      "confidence": "high|medium|low",
      "action": "recommended action"
    }}
  ],
  "summary": "brief summary"
}}"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response)
            return result or {"predictions": [], "message": "Unable to generate predictions."}
        except Exception as e:
            logger.error(f"Material prediction error: {e}")
            return {"predictions": [], "error": str(e)}
    
    # =========================================================================
    # 2. DELAY PREDICTION
    # =========================================================================
    
    async def predict_delays(
        self,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Predict delays based on text patterns:
        - Labour shortage mentions
        - Material delays
        - Approval pending
        - Contractor issues
        - Weather
        """
        
        # Get delay-related messages
        context = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query="delay shortage pending waiting hold stopped labour material weather rain",
            limit=25,
        )
        
        if not context:
            return {
                "risks": [],
                "message": "No delay indicators found.",
            }
        
        context_text = "\n".join([
            f"- {item.get('content', str(item))[:200]}"
            for item in context
        ])
        
        # Also check pending RFIs and open issues
        rfis = memory_engine.get_open_rfis(company_id, project_id)
        issues = awareness_engine.get_open_issues(company_id, project_id)
        
        prompt = f"""Analyze and predict potential delays.

MESSAGES:
{context_text}

OPEN RFIs: {len(rfis)}
OPEN ISSUES: {len(issues)}

Predict delays and return JSON:
{{
  "delay_risks": [
    {{
      "work_type": "what work is affected",
      "cause": "reason for potential delay",
      "estimated_delay_days": number,
      "confidence": "high|medium|low",
      "mitigation": "what can be done"
    }}
  ],
  "overall_risk": "high|medium|low",
  "summary": "brief summary of delay situation"
}}"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response)
            return result or {"delay_risks": [], "message": "Unable to predict delays."}
        except Exception as e:
            logger.error(f"Delay prediction error: {e}")
            return {"delay_risks": [], "error": str(e)}
    
    # =========================================================================
    # 3. CONTRACTOR PERFORMANCE SCORE
    # =========================================================================
    
    async def calculate_contractor_score(
        self,
        contractor_name: str,
        company_id: str,
        project_id: str,
    ) -> ContractorScore:
        """
        Calculate contractor performance based on:
        - RFI response time
        - Issues logged against them
        - On-time completion
        - Communication responsiveness
        """
        
        # Search for contractor-related data
        context = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query=f"{contractor_name} contractor work completed issue delay",
            limit=30,
        )
        
        context_text = "\n".join([
            f"- {item.get('content', str(item))[:200]}"
            for item in context
        ])
        
        prompt = f"""Analyze contractor performance for: {contractor_name}

DATA:
{context_text}

Evaluate and return JSON:
{{
  "score": 0-100,
  "rfi_response_time_days": average days to respond,
  "issues_count": number of issues logged,
  "on_time_rate": 0.0-1.0,
  "strengths": ["list"],
  "weaknesses": ["list"],
  "trend": "improving|stable|declining"
}}"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response) or {}
            
            score = ContractorScore(
                name=contractor_name,
                score=result.get("score", 70),
                rfi_response_time_days=result.get("rfi_response_time_days", 0),
                issues_logged=result.get("issues_count", 0),
                on_time_completion_rate=result.get("on_time_rate", 0.8),
                last_updated=datetime.utcnow(),
            )
            
            # Store
            key = f"{company_id}_{project_id}"
            if key not in self._contractor_scores:
                self._contractor_scores[key] = {}
            self._contractor_scores[key][contractor_name] = score
            
            return score
            
        except Exception as e:
            logger.error(f"Contractor score error: {e}")
            return ContractorScore(
                name=contractor_name,
                score=70,
                rfi_response_time_days=0,
                issues_logged=0,
                on_time_completion_rate=0.8,
                last_updated=datetime.utcnow(),
            )
    
    async def get_contractor_rankings(
        self,
        company_id: str,
        project_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all contractor rankings"""
        
        # Search for all contractor mentions
        context = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query="contractor vendor supplier electrician plumber mason",
            limit=30,
        )
        
        context_text = "\n".join([
            f"- {item.get('content', str(item))[:150]}"
            for item in context
        ])
        
        prompt = f"""Identify and rank contractors mentioned in this data.

DATA:
{context_text}

Return JSON:
{{
  "contractors": [
    {{
      "name": "contractor name",
      "work_type": "electrical/plumbing/etc",
      "mentions": number of mentions,
      "issues_mentioned": number,
      "positive_mentions": number,
      "estimated_score": 0-100
    }}
  ]
}}"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response)
            return result.get("contractors", []) if result else []
        except Exception as e:
            logger.error(f"Contractor ranking error: {e}")
            return []
    
    # =========================================================================
    # 4. PROJECT HEALTH REPORT
    # =========================================================================
    
    async def generate_health_report(
        self,
        company_id: str,
        project_id: str,
        period: str = "weekly",  # weekly or monthly
    ) -> str:
        """
        Generate comprehensive project health report
        
        Includes:
        - Summary
        - Issues
        - RFIs
        - Delays
        - Drawing changes
        - Risks
        - Next steps
        """
        
        # Gather all data
        stats = memory_engine.get_stats(company_id, project_id)
        awareness_stats = awareness_engine.get_stats(company_id, project_id)
        
        # Get recent activity
        context = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query="progress issue decision rfi update drawing change",
            limit=40,
        )
        
        context_text = "\n".join([
            f"- {item.get('content', str(item))[:200]}"
            for item in context
        ])
        
        # Get delay predictions
        delay_info = await self.predict_delays(company_id, project_id)
        
        prompt = f"""Generate a {period} project health report.

STATS:
- Total RFIs: {stats.get('total_rfis', 0)}
- Open RFIs: {stats.get('open_rfis', 0)}
- Total Decisions: {stats.get('total_decisions', 0)}
- Total Issues: {awareness_stats.get('total_issues', 0)}
- Open Issues: {awareness_stats.get('open_issues', 0)}
- High Severity Issues: {awareness_stats.get('high_severity_issues', 0)}

RECENT ACTIVITY:
{context_text}

DELAY RISKS:
{json.dumps(delay_info, default=str)}

Generate a comprehensive {period.upper()} REPORT with:

📊 *{period.upper()} PROJECT HEALTH REPORT*

*Executive Summary:*
[2-3 sentence overview]

*Progress Highlights:*
• [Key progress items]

*Issues & Concerns:*
• [Open issues and severity]

*RFI Status:*
• [RFI summary and any pending]

*Risks & Mitigation:*
• [Key risks and recommended actions]

*Decisions Made:*
• [Important decisions this period]

*Next Week Focus:*
• [Priority items for next period]

*Health Score: X/100*
[Brief explanation of score]"""

        try:
            return await gemini_service._generate(prompt)
        except Exception as e:
            logger.error(f"Health report error: {e}")
            return f"Unable to generate report. Stats: {stats}"
    
    # =========================================================================
    # 5. BOQ DEVIATION ALERTS
    # =========================================================================
    
    async def check_boq_deviation(
        self,
        company_id: str,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Check for BOQ deviations
        
        Compares:
        - Progress text vs planned quantities
        - Material consumption vs BOQ
        """
        
        # Search for BOQ and progress data
        context = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query="BOQ quantity progress completed consumption material used planned",
            limit=25,
        )
        
        if not context:
            return {
                "deviations": [],
                "message": "No BOQ data found. Upload BOQ to enable deviation tracking.",
            }
        
        context_text = "\n".join([
            f"- {item.get('content', str(item))[:200]}"
            for item in context
        ])
        
        prompt = f"""Analyze for BOQ deviations.

DATA:
{context_text}

Compare progress vs planned quantities and identify deviations.

Return JSON:
{{
  "deviations": [
    {{
      "item": "what item",
      "planned": "planned quantity",
      "actual": "actual/consumed quantity",
      "deviation_percent": number,
      "concern": "overconsumption|underconsumption|none",
      "explanation": "possible reason"
    }}
  ],
  "summary": "overall deviation status"
}}"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response)
            return result or {"deviations": [], "message": "Unable to analyze deviations."}
        except Exception as e:
            logger.error(f"BOQ deviation error: {e}")
            return {"deviations": [], "error": str(e)}
    
    # =========================================================================
    # 6. RISK MONITORING
    # =========================================================================
    
    async def monitor_risks(
        self,
        company_id: str,
        project_id: str,
    ) -> List[Risk]:
        """
        Monitor for risks in project messages
        
        Risk categories:
        - Material delays
        - Labour issues
        - Approval pending
        - Contractor problems
        - Weather/external
        """
        
        # Get risk indicators
        context = await memory_service.search(
            company_id=company_id,
            project_id=project_id,
            query="waiting pending delay risk issue problem shortage unavailable weather rain",
            limit=30,
        )
        
        if not context:
            return []
        
        context_text = "\n".join([
            f"- {item.get('content', str(item))[:200]}"
            for item in context
        ])
        
        prompt = f"""Identify project risks from these messages.

MESSAGES:
{context_text}

Return JSON:
{{
  "risks": [
    {{
      "description": "risk description",
      "category": "material|labour|approval|contractor|weather|other",
      "severity": "high|medium|low",
      "affected_work": "what work is impacted",
      "mitigation": "recommended action"
    }}
  ]
}}"""

        try:
            response = await gemini_service._generate(prompt)
            result = self._extract_json(response)
            
            risks = []
            if result and result.get("risks"):
                key = f"{company_id}_{project_id}"
                if key not in self._risks:
                    self._risks[key] = []
                
                for r in result["risks"]:
                    risk = Risk(
                        id=f"RISK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                        description=r.get("description", ""),
                        category=r.get("category", "other"),
                        severity=r.get("severity", "medium"),
                        detected_at=datetime.utcnow(),
                        affected_work=r.get("affected_work"),
                        mitigation=r.get("mitigation"),
                    )
                    risks.append(risk)
                    self._risks[key].append(risk)
            
            return risks
            
        except Exception as e:
            logger.error(f"Risk monitoring error: {e}")
            return []
    
    async def get_risk_summary(
        self,
        company_id: str,
        project_id: str,
    ) -> str:
        """Get formatted risk summary"""
        
        risks = await self.monitor_risks(company_id, project_id)
        
        if not risks:
            return "✅ *Risk Status: LOW*\n\nNo significant risks detected."
        
        high_risks = [r for r in risks if r.severity == "high"]
        medium_risks = [r for r in risks if r.severity == "medium"]
        
        summary = f"""⚠️ *Risk Summary*

*High Priority ({len(high_risks)}):*
"""
        for r in high_risks[:3]:
            summary += f"• {r.description}\n  → {r.mitigation}\n"
        
        summary += f"""
*Medium Priority ({len(medium_risks)}):*
"""
        for r in medium_risks[:3]:
            summary += f"• {r.description}\n"
        
        return summary
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text"""
        import re
        try:
            # Find JSON in text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return None
        except:
            return None


# Singleton
intelligence_engine = ProjectIntelligenceEngine()

