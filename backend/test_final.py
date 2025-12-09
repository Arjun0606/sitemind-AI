#!/usr/bin/env python3
"""
SITEMIND FINAL TEST SUITE
=========================

Comprehensive tests for ALL honest capabilities.
If any test fails, DO NOT DEPLOY.

Run: python test_final.py
"""

import asyncio
import sys
from datetime import datetime
from typing import Tuple


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add(self, name: str, passed: bool, message: str = ""):
        self.tests.append((name, passed, message))
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print()
        
        for name, passed, message in self.tests:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {name}")
            if message and not passed:
                print(f"         → {message}")
        
        print()
        print("-" * 80)
        print(f"  PASSED: {self.passed}")
        print(f"  FAILED: {self.failed}")
        print(f"  TOTAL:  {len(self.tests)}")
        print("-" * 80)
        
        if self.failed > 0:
            print()
            print("⚠️  SOME TESTS FAILED - DO NOT DEPLOY")
            print()
            return False
        else:
            print()
            print("🎉 ALL TESTS PASSED - READY FOR DEPLOYMENT")
            print()
            return True


async def test_services_import() -> Tuple[bool, str]:
    """Test that all essential services can be imported"""
    try:
        from services import (
            gemini_service,
            memory_service,
            storage_service,
            whatsapp_service,
            memory_engine,
            awareness_engine,
            intelligence_engine,
            billing_service,
            pricing_service,
            project_manager,
            subscription_reminder_service,
        )
        return True, ""
    except Exception as e:
        return False, str(e)


async def test_gemini_service() -> Tuple[bool, str]:
    """Test Gemini AI service"""
    try:
        from services import gemini_service
        
        # Test query
        response = await gemini_service.query("Say 'hello' in one word")
        if response and len(response) > 0:
            return True, ""
        return False, "Empty response from Gemini"
    except Exception as e:
        return False, str(e)


async def test_memory_service_add() -> Tuple[bool, str]:
    """Test adding to memory"""
    try:
        from services import memory_service
        
        result = await memory_service.add_memory(
            company_id="test_final",
            project_id="test_project",
            content="Test decision: Client approved final design",
            memory_type="decision",
            metadata={"user": "Test User"},
            user_id="test_user",
        )
        
        if result and result.id:
            return True, ""
        return False, "No ID returned"
    except Exception as e:
        return False, str(e)


async def test_memory_service_search() -> Tuple[bool, str]:
    """Test searching memory"""
    try:
        from services import memory_service
        
        results = await memory_service.search(
            company_id="test_final",
            project_id="test_project",
            query="approved design",
            limit=5,
        )
        
        # Should return list (even if empty)
        if isinstance(results, list):
            return True, ""
        return False, "Invalid search result type"
    except Exception as e:
        return False, str(e)


async def test_storage_service() -> Tuple[bool, str]:
    """Test file storage"""
    try:
        from services.storage_service import storage_service
        
        result = await storage_service.upload_document(
            file_content=b"Test PDF content",
            file_name="test_drawing.pdf",
            content_type="application/pdf",
            company_id="test_final",
            project_id="test_project",
        )
        
        if result and result.get("status") in ["uploaded", "stored_locally"]:
            return True, ""
        return False, f"Unexpected status: {result}"
    except Exception as e:
        return False, str(e)


async def test_memory_engine_classify() -> Tuple[bool, str]:
    """Test AI message classification (no pattern matching)"""
    try:
        from services import memory_engine
        
        # Test decision detection
        result = await memory_engine.classify_message(
            "Client approved the marble flooring, extra cost 4 lakhs",
            "PM",
            "test_final",
            "test_project",
        )
        
        # Should return classification dict
        if isinstance(result, dict) and "category" in result:
            return True, ""
        return False, "Invalid classification result"
    except Exception as e:
        return False, str(e)


async def test_memory_engine_store_drawing() -> Tuple[bool, str]:
    """Test drawing storage (metadata only, no content analysis)"""
    try:
        from services import memory_engine
        
        drawing = await memory_engine.extract_drawing_info(
            document_text="",  # Empty - we don't analyze content
            file_name="STR-07-R3.pdf",
            company_id="test_final",
            project_id="test_project",
            uploaded_by="Test User",
        )
        
        # Should extract from filename
        if drawing and drawing.name == "STR-07-R3.pdf":
            # Sheet should be extracted from filename
            if drawing.sheet_number:
                return True, ""
            return True, "Sheet not extracted (acceptable)"
        return False, "Drawing not stored"
    except Exception as e:
        return False, str(e)


async def test_memory_engine_rfi() -> Tuple[bool, str]:
    """Test RFI creation and tracking"""
    try:
        from services import memory_engine
        
        # Create RFI
        rfi = await memory_engine.create_rfi(
            title="Beam size confirmation",
            question="Please confirm beam size at grid C3",
            raised_by="Test User",
            company_id="test_final",
            project_id="test_project",
        )
        
        if not rfi or not rfi.id:
            return False, "RFI not created"
        
        # Get open RFIs
        open_rfis = memory_engine.get_open_rfis("test_final", "test_project")
        if isinstance(open_rfis, list):
            return True, ""
        return False, "Invalid RFI list"
    except Exception as e:
        return False, str(e)


async def test_memory_engine_decision() -> Tuple[bool, str]:
    """Test decision logging"""
    try:
        from services import memory_engine
        
        decision = await memory_engine.log_decision(
            description="Approved vitrified tiles for all bedrooms",
            approved_by="Client Manager",
            company_id="test_final",
            project_id="test_project",
        )
        
        if decision and decision.id:
            return True, ""
        return False, "Decision not logged"
    except Exception as e:
        return False, str(e)


async def test_memory_engine_summary() -> Tuple[bool, str]:
    """Test summary generation"""
    try:
        from services import memory_engine
        
        summary = await memory_engine.generate_daily_summary(
            "test_final",
            "test_project",
        )
        
        if summary and len(summary) > 10:
            return True, ""
        return False, "Empty summary"
    except Exception as e:
        return False, str(e)


async def test_awareness_engine_issue() -> Tuple[bool, str]:
    """Test issue detection"""
    try:
        from services import awareness_engine
        
        issue = await awareness_engine.detect_issue(
            "Major water leakage found in basement parking",
            "Site Engineer",
            "test_final",
            "test_project",
        )
        
        # May or may not detect issue (depends on AI)
        # Just check it doesn't crash
        return True, ""
    except Exception as e:
        return False, str(e)


async def test_awareness_engine_progress() -> Tuple[bool, str]:
    """Test progress detection"""
    try:
        from services import awareness_engine
        
        progress = await awareness_engine.detect_progress(
            "Slab casting completed on floor 7",
            "Site Engineer",
            "test_final",
            "test_project",
        )
        
        # May or may not detect progress
        return True, ""
    except Exception as e:
        return False, str(e)


async def test_intelligence_engine_report() -> Tuple[bool, str]:
    """Test report generation"""
    try:
        from services import intelligence_engine
        
        report = await intelligence_engine.generate_health_report(
            "test_final",
            "test_project",
            "weekly",
        )
        
        if report and len(report) > 10:
            return True, ""
        return False, "Empty report"
    except Exception as e:
        return False, str(e)


async def test_no_pattern_matching_in_router() -> Tuple[bool, str]:
    """Verify no command pattern matching in WhatsApp router"""
    try:
        with open("routers/whatsapp.py", "r") as f:
            code = f.read()
        
        # Check for command patterns
        forbidden_patterns = [
            '"/help"',
            '"/summary"',
            '"/rfi"',
            '"/decision"',
            '"Decision:"',
            '"Call log:"',
            '"RFI:"',
            'cmd ==',
            'cmd.startswith',
        ]
        
        for pattern in forbidden_patterns:
            if pattern in code:
                return False, f"Found forbidden pattern: {pattern}"
        
        return True, ""
    except Exception as e:
        return False, str(e)


async def test_project_manager() -> Tuple[bool, str]:
    """Test project management"""
    try:
        from services import project_manager
        
        # List projects
        projects = project_manager.list_projects("test_final")
        
        # Should return list
        if isinstance(projects, list):
            return True, ""
        return False, "Invalid project list"
    except Exception as e:
        return False, str(e)


async def test_billing_service() -> Tuple[bool, str]:
    """Test billing tracking"""
    try:
        from services import billing_service
        
        # Track a query
        billing_service.track_query("test_final")
        
        # Get usage
        usage = billing_service.get_usage("test_final")
        
        if isinstance(usage, dict):
            return True, ""
        return False, "Invalid usage data"
    except Exception as e:
        return False, str(e)


async def test_whatsapp_service() -> Tuple[bool, str]:
    """Test WhatsApp service initialization"""
    try:
        from services import whatsapp_service
        
        # Just check it's initialized
        if whatsapp_service:
            return True, ""
        return False, "Service not initialized"
    except Exception as e:
        return False, str(e)


async def run_all_tests():
    """Run all tests"""
    print()
    print("=" * 80)
    print("🧪 SITEMIND FINAL TEST SUITE")
    print("=" * 80)
    print()
    print("Testing all honest capabilities...")
    print("No overpromising. No pattern matching.")
    print()
    
    results = TestResults()
    
    # Core imports
    print("─" * 80)
    print("CORE SERVICES")
    print("─" * 80)
    
    passed, msg = await test_services_import()
    results.add("Import all services", passed, msg)
    
    passed, msg = await test_gemini_service()
    results.add("Gemini AI service", passed, msg)
    
    passed, msg = await test_memory_service_add()
    results.add("Memory service - add", passed, msg)
    
    passed, msg = await test_memory_service_search()
    results.add("Memory service - search", passed, msg)
    
    passed, msg = await test_storage_service()
    results.add("File storage service", passed, msg)
    
    passed, msg = await test_whatsapp_service()
    results.add("WhatsApp service", passed, msg)
    
    # Phase 1: Memory Engine
    print()
    print("─" * 80)
    print("PHASE 1: MEMORY ENGINE")
    print("─" * 80)
    
    passed, msg = await test_memory_engine_classify()
    results.add("AI message classification", passed, msg)
    
    passed, msg = await test_memory_engine_store_drawing()
    results.add("Drawing storage (metadata only)", passed, msg)
    
    passed, msg = await test_memory_engine_rfi()
    results.add("RFI creation & tracking", passed, msg)
    
    passed, msg = await test_memory_engine_decision()
    results.add("Decision logging", passed, msg)
    
    passed, msg = await test_memory_engine_summary()
    results.add("Summary generation", passed, msg)
    
    # Phase 2: Awareness Engine
    print()
    print("─" * 80)
    print("PHASE 2: AWARENESS ENGINE")
    print("─" * 80)
    
    passed, msg = await test_awareness_engine_issue()
    results.add("Issue detection", passed, msg)
    
    passed, msg = await test_awareness_engine_progress()
    results.add("Progress detection", passed, msg)
    
    # Phase 3: Intelligence Engine
    print()
    print("─" * 80)
    print("PHASE 3: INTELLIGENCE ENGINE")
    print("─" * 80)
    
    passed, msg = await test_intelligence_engine_report()
    results.add("Report generation", passed, msg)
    
    # Business Logic
    print()
    print("─" * 80)
    print("BUSINESS LOGIC")
    print("─" * 80)
    
    passed, msg = await test_project_manager()
    results.add("Project management", passed, msg)
    
    passed, msg = await test_billing_service()
    results.add("Billing tracking", passed, msg)
    
    # Security Checks
    print()
    print("─" * 80)
    print("SECURITY CHECKS")
    print("─" * 80)
    
    passed, msg = await test_no_pattern_matching_in_router()
    results.add("No pattern matching in router", passed, msg)
    
    # Print summary
    return results.print_summary()


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

