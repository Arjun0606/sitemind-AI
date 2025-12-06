"""
SiteMind Report Generation Service
Automated reports for management - this justifies the $500/site pricing

Reports Generated:
1. Weekly Summary - Sent every Monday
2. Monthly ROI Report - Sent 1st of month
3. Audit Trail Export - On-demand PDF for legal
4. Conflict Alert Report - When issues detected
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json


class ReportService:
    """
    Automated Report Generation for SiteMind
    
    These reports are sent to:
    - Site Engineers (Weekly summary)
    - Project Managers (Weekly + Monthly)
    - Builder Management (Monthly ROI)
    - Legal Team (Audit exports on demand)
    """
    
    def __init__(self):
        pass
    
    def generate_weekly_summary(
        self,
        project_id: str,
        project_name: str,
        queries: List[Dict],
        roi_data: Dict,
    ) -> Dict[str, Any]:
        """
        Generate weekly summary for project team
        Sent every Monday morning via WhatsApp
        """
        week_start = (datetime.utcnow() - timedelta(days=7)).strftime("%d %b")
        week_end = datetime.utcnow().strftime("%d %b %Y")
        
        # Categorize queries
        dimension_queries = sum(1 for q in queries if q.get("type") == "dimension")
        rfi_queries = sum(1 for q in queries if q.get("type") == "rfi")
        change_queries = sum(1 for q in queries if q.get("type") == "change_order")
        
        report = f"""
📊 *SiteMind Weekly Report*
*{project_name}*
{week_start} - {week_end}

━━━━━━━━━━━━━━━━━━━━━
📈 *This Week's Impact*
━━━━━━━━━━━━━━━━━━━━━
• Queries Answered: {len(queries)}
• Time Saved: {roi_data.get('time_saved_hours', 0):.1f} hours
• Value Delivered: {roi_data.get('total_value_formatted', '₹0')}

━━━━━━━━━━━━━━━━━━━━━
📋 *Query Breakdown*
━━━━━━━━━━━━━━━━━━━━━
• Dimension Queries: {dimension_queries}
• RFI References: {rfi_queries}
• Change Orders: {change_queries}
• Other: {len(queries) - dimension_queries - rfi_queries - change_queries}

━━━━━━━━━━━━━━━━━━━━━
💰 *Value Summary*
━━━━━━━━━━━━━━━━━━━━━
Monthly Cost: ₹41,500 ($500)
Estimated Value: {roi_data.get('estimated_value_formatted', roi_data.get('total_value_formatted', '₹0'))}
Estimated ROI: {roi_data.get('estimated_roi_formatted', roi_data.get('roi_formatted', 'N/A'))}
_Based on industry benchmarks_

━━━━━━━━━━━━━━━━━━━━━
🎯 *Top Queries This Week*
━━━━━━━━━━━━━━━━━━━━━
"""
        # Add top 3 queries
        for i, q in enumerate(queries[:3], 1):
            report += f"{i}. {q.get('query', 'N/A')[:50]}...\n"
        
        report += """
━━━━━━━━━━━━━━━━━━━━━
_Powered by SiteMind AI_
_Your AI Site Engineer_
"""
        
        return {
            "type": "weekly_summary",
            "project_id": project_id,
            "project_name": project_name,
            "period": f"{week_start} - {week_end}",
            "content": report,
            "format": "whatsapp",  # Formatted for WhatsApp
        }
    
    def generate_audit_export(
        self,
        project_id: str,
        project_name: str,
        memories: List[Dict],
        date_range: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        """
        Generate audit trail export for legal/compliance
        This is a PDF-ready format for disputes
        """
        export = {
            "document_type": "AUDIT TRAIL EXPORT",
            "project_name": project_name,
            "project_id": project_id,
            "generated_at": datetime.utcnow().isoformat(),
            "generated_by": "SiteMind AI Platform",
            
            "legal_disclaimer": """
This document contains a complete audit trail of all decisions, 
change orders, and RFIs recorded in the SiteMind system. 
Each entry includes timestamp, approver, and source reference.
This document may be used as evidence in dispute resolution.
            """,
            
            "entries": [],
        }
        
        for mem in memories:
            metadata = mem.get("metadata", {})
            entry = {
                "timestamp": mem.get("created_at", "N/A"),
                "type": metadata.get("type", "general").upper(),
                "content": mem.get("content", ""),
                "drawing_reference": metadata.get("drawing", "N/A"),
                "approved_by": metadata.get("approved_by", "N/A"),
                "requested_by": metadata.get("requested_by", "N/A"),
                "reason": metadata.get("reason", "N/A"),
                "previous_value": metadata.get("previous_value", "N/A"),
                "new_value": metadata.get("new_value", "N/A"),
                "reference_number": metadata.get("change_order_number") or metadata.get("rfi_number") or "N/A",
            }
            export["entries"].append(entry)
        
        export["total_entries"] = len(export["entries"])
        export["entry_types"] = {}
        for entry in export["entries"]:
            t = entry["type"]
            export["entry_types"][t] = export["entry_types"].get(t, 0) + 1
        
        return export
    
    def generate_conflict_alert(
        self,
        project_id: str,
        project_name: str,
        conflict_type: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate conflict alert when AI detects potential issues
        This is PROACTIVE value - finding problems before they cost money
        """
        alert = f"""
🚨 *CONFLICT ALERT*
*{project_name}*

━━━━━━━━━━━━━━━━━━━━━
⚠️ *Issue Detected*
━━━━━━━━━━━━━━━━━━━━━
Type: {conflict_type}
Location: {details.get('location', 'N/A')}
Drawing: {details.get('drawing', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━
📋 *Details*
━━━━━━━━━━━━━━━━━━━━━
{details.get('description', 'No details available')}

━━━━━━━━━━━━━━━━━━━━━
💡 *Recommendation*
━━━━━━━━━━━━━━━━━━━━━
{details.get('recommendation', 'Please verify with structural engineer')}

━━━━━━━━━━━━━━━━━━━━━
💰 *Potential Cost if Ignored*
━━━━━━━━━━━━━━━━━━━━━
Estimated: {details.get('potential_cost', '₹2-5 Lakhs')}

━━━━━━━━━━━━━━━━━━━━━
_SiteMind detected this issue proactively_
_Action required within 24 hours_
"""
        
        return {
            "type": "conflict_alert",
            "priority": "HIGH",
            "project_id": project_id,
            "project_name": project_name,
            "conflict_type": conflict_type,
            "content": alert,
            "details": details,
            "requires_action": True,
        }
    
    def generate_management_dashboard(
        self,
        builder_id: str,
        builder_name: str,
        projects_data: List[Dict],
    ) -> Dict[str, Any]:
        """
        Generate dashboard data for builder management
        Shows all projects and total ROI across portfolio
        """
        total_queries = sum(p.get("queries", 0) for p in projects_data)
        total_value = sum(p.get("value_inr", 0) for p in projects_data)
        total_sites = len(projects_data)
        monthly_cost = total_sites * 500 * 83  # $500 per site in INR
        
        dashboard = {
            "builder_id": builder_id,
            "builder_name": builder_name,
            "generated_at": datetime.utcnow().isoformat(),
            
            "portfolio_summary": {
                "total_active_sites": total_sites,
                "total_queries_answered": total_queries,
                "total_value_delivered_inr": total_value,
                "total_value_formatted": f"₹{total_value:,.0f}",
                "monthly_subscription_inr": monthly_cost,
                "monthly_subscription_formatted": f"₹{monthly_cost:,.0f}",
                "portfolio_roi": f"{total_value / monthly_cost:.1f}x" if monthly_cost > 0 else "N/A",
            },
            
            "projects": [
                {
                    "name": p.get("name", "Unknown"),
                    "queries": p.get("queries", 0),
                    "value_inr": p.get("value_inr", 0),
                    "value_formatted": f"₹{p.get('value_inr', 0):,.0f}",
                    "status": p.get("status", "active"),
                }
                for p in projects_data
            ],
            
            "insights": {
                "most_active_site": max(projects_data, key=lambda x: x.get("queries", 0)).get("name", "N/A") if projects_data else "N/A",
                "highest_value_site": max(projects_data, key=lambda x: x.get("value_inr", 0)).get("name", "N/A") if projects_data else "N/A",
                "avg_queries_per_site": total_queries / total_sites if total_sites > 0 else 0,
            },
        }
        
        return dashboard


# Singleton instance
report_service = ReportService()

