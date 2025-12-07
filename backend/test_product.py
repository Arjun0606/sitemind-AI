#!/usr/bin/env python3
"""
SiteMind Complete Product Test
Run this before demo to verify everything works

Usage:
    cd backend
    python test_product.py
"""

import asyncio
from datetime import datetime

# Banner
print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███████╗██╗████████╗███████╗███╗   ███╗██╗███╗   ██╗██████╗    ║
║   ██╔════╝██║╚══██╔══╝██╔════╝████╗ ████║██║████╗  ██║██╔══██╗   ║
║   ███████╗██║   ██║   █████╗  ██╔████╔██║██║██╔██╗ ██║██║  ██║   ║
║   ╚════██║██║   ██║   ██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║  ██║   ║
║   ███████║██║   ██║   ███████╗██║ ╚═╝ ██║██║██║ ╚████║██████╔╝   ║
║   ╚══════╝╚═╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝    ║
║                                                                   ║
║               COMPLETE PRODUCT TEST SUITE                         ║
║               Target: $10k/month from Urbanrise                   ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")


async def test_all():
    results = []
    
    def test(name, passed, details=""):
        status = "✅" if passed else "❌"
        results.append((name, passed))
        print(f"{status} {name}")
        if details and not passed:
            print(f"   └─ {details}")
    
    # =========================================================================
    # 1. IMPORTS TEST
    # =========================================================================
    print("\n━━━ 1. SERVICE IMPORTS ━━━")
    
    try:
        from services import (
            gemini_service,
            memory_service,
            intelligence_service,
            whatsapp_service,
            storage_service,
            pricing_service,
            billing_service,
            wow_service,
            daily_brief_service,
            report_service,
            alert_service,
            project_manager,
            command_handler,
        )
        test("All services import", True)
    except ImportError as e:
        test("All services import", False, str(e))
        return
    
    try:
        from database import db
        test("Database client import", True)
    except ImportError as e:
        test("Database client import", False, str(e))
    
    # =========================================================================
    # 2. GEMINI AI TEST
    # =========================================================================
    print("\n━━━ 2. GEMINI AI ENGINE ━━━")
    
    # Check configuration
    is_configured = gemini_service._is_configured()
    test("Gemini API configured", is_configured, "Set GOOGLE_API_KEY in .env")
    
    if is_configured:
        # Test query
        response = await gemini_service.query(
            "What is the minimum cover for RCC columns as per IS 456?",
            context=[],
            project_info={"name": "Test Project"}
        )
        
        has_answer = response.get("status") == "success"
        test("Gemini query response", has_answer)
        
        if has_answer:
            answer = response.get("answer", "")
            has_is_code = "456" in answer or "40" in answer.lower() or "mm" in answer.lower()
            test("Response includes IS code reference", has_is_code)
    
    # =========================================================================
    # 3. MEMORY SERVICE TEST
    # =========================================================================
    print("\n━━━ 3. MEMORY SERVICE ━━━")
    
    test_project = f"test_project_{datetime.now().timestamp():.0f}"
    
    # Add memory
    memory = await memory_service.add_memory(
        project_id=test_project,
        content="Test decision: Column size changed to 450x600mm",
        memory_type="decision",
        metadata={"reason": "structural revision"},
        user_id="test_user",
    )
    test("Add memory", memory.get("status") in ["stored", "stored_locally"])
    
    # Search memory
    results = await memory_service.search(
        project_id=test_project,
        query="column size",
        limit=5,
    )
    test("Search memory", len(results) > 0)
    
    # =========================================================================
    # 4. INTELLIGENCE SERVICE TEST
    # =========================================================================
    print("\n━━━ 4. INTELLIGENCE ENGINE ━━━")
    
    # Safety detection
    safety = await intelligence_service.analyze_safety(
        text="Worker working at height without safety harness",
        project_id=test_project,
    )
    test("Safety issue detection", not safety["is_safe"])
    test("Safety severity correct", safety["severity"] in ["warning", "critical"])
    
    # Urgency detection
    urgency = intelligence_service.detect_urgency("This is urgent, stop work immediately")
    test("Urgency detection", urgency["is_urgent"])
    
    # Expert tips
    tip = intelligence_service.get_expert_tip("concrete curing")
    test("Expert tips available", tip is not None)
    
    # =========================================================================
    # 5. PROJECT MANAGER TEST
    # =========================================================================
    print("\n━━━ 5. PROJECT MANAGER ━━━")
    
    test_company = "test_urbanrise"
    
    # Create projects
    project_manager.create_project(test_company, "proj1", "Marina Bay", "Chennai", "residential")
    project_manager.create_project(test_company, "proj2", "World of Joy", "Hyderabad", "residential")
    
    # List projects
    projects = project_manager.get_active_projects(test_company)
    test("Create projects", len(projects) >= 2)
    
    # Switch project
    project = project_manager.switch_project("test_user", test_company, "Marina Bay")
    test("Switch project", project is not None)
    
    # Get current project
    current = project_manager.get_current_project("test_user", test_company)
    test("Get current project", current is not None and "Marina" in current.name)
    
    # =========================================================================
    # 6. COMMAND HANDLER TEST
    # =========================================================================
    print("\n━━━ 6. COMMAND HANDLER ━━━")
    
    # Parse commands
    cmd, args = command_handler.parse("help")
    test("Parse 'help' command", cmd == "help")
    
    cmd, args = command_handler.parse("switch to Marina Bay")
    test("Parse 'switch to' command", cmd == "_cmd_switch")
    
    cmd, args = command_handler.parse("What is the cover for columns?")
    test("Parse query (not command)", cmd is None)
    
    # Intent detection
    intent = command_handler.detect_intent("urgent safety issue at site")
    test("Intent detection (urgent)", intent["priority"] == "high")
    
    # =========================================================================
    # 7. BILLING SERVICE TEST
    # =========================================================================
    print("\n━━━ 7. BILLING SERVICE ━━━")
    
    # Initialize usage
    billing_service.get_or_create_usage(test_company, "Test Company")
    
    # Track usage
    for _ in range(10):
        billing_service.track_query(test_company)
    billing_service.track_photo(test_company)
    billing_service.track_document(test_company)
    
    # Get usage
    usage = billing_service.get_usage(test_company)
    test("Track queries", usage and usage.get("queries", 0) >= 10)
    test("Track photos", usage and usage.get("photos", 0) >= 1)
    test("Track documents", usage and usage.get("documents", 0) >= 1)
    
    # =========================================================================
    # 8. WOW SERVICE TEST
    # =========================================================================
    print("\n━━━ 8. WOW SERVICE (Week 1 Value) ━━━")
    
    # Track interactions
    wow_service.track_query("test_user", test_company, had_code_reference=True)
    wow_service.track_photo("test_user", test_company)
    wow_service.track_safety_flag("test_user", test_company)
    wow_service.track_memory_recall("test_user", test_company)
    
    # Get ROI
    roi = wow_service.get_week1_roi(test_company)
    test("Track WOW metrics", roi.get("queries_answered", 0) > 0)
    test("Calculate ROI", roi.get("total_value_inr", 0) > 0)
    
    # =========================================================================
    # 9. DAILY BRIEF SERVICE TEST
    # =========================================================================
    print("\n━━━ 9. DAILY BRIEF SERVICE ━━━")
    
    # Track activity
    for _ in range(5):
        daily_brief_service.track_query("proj1")
    daily_brief_service.track_photo("proj1")
    daily_brief_service.track_safety_flag("proj1")
    
    # Generate brief
    brief = daily_brief_service.generate_brief("proj1", "Marina Bay")
    test("Generate daily brief", brief is not None)
    test("Brief has queries count", brief.queries_yesterday >= 0)
    
    # Format for WhatsApp
    formatted = daily_brief_service.format_brief_whatsapp(brief)
    test("Format brief for WhatsApp", "Marina Bay" in formatted)
    
    # =========================================================================
    # 10. REPORT SERVICE TEST
    # =========================================================================
    print("\n━━━ 10. REPORT SERVICE ━━━")
    
    # Generate weekly report
    report = report_service.generate_weekly_report(
        company_id=test_company,
        company_name="Urbanrise",
        activity_data={
            "queries": 150,
            "photos": 25,
            "documents": 10,
            "safety_flags": 3,
            "conflicts": 1,
            "active_users": 15,
            "active_projects": 5,
        }
    )
    test("Generate weekly report", report is not None)
    
    # Format for WhatsApp
    formatted = report_service.format_weekly_whatsapp(report)
    test("Format report for WhatsApp", "Urbanrise" in formatted)
    
    # =========================================================================
    # 11. ALERT SERVICE TEST
    # =========================================================================
    print("\n━━━ 11. ALERT SERVICE ━━━")
    
    # Create alerts
    alert_service.safety_alert(
        test_company, "proj1",
        "Worker without helmet",
        "Ensure all workers have PPE"
    )
    
    alert_service.conflict_alert(
        test_company, "proj1",
        "Column size mismatch between structural and architectural drawings"
    )
    
    # Get alerts
    alerts = alert_service.get_pending_alerts(test_company)
    test("Create and retrieve alerts", len(alerts) >= 2)
    
    # =========================================================================
    # 12. PRICING SERVICE TEST
    # =========================================================================
    print("\n━━━ 12. PRICING SERVICE ━━━")
    
    pricing = pricing_service.get_pricing()
    test("Get pricing info", pricing.get("flat_fee_usd") == 1000)
    test("Usage pricing available", len(pricing.get("included", {})) > 0)
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "═" * 60)
    
    # Count passed tests (handle both tuple and other cases)
    passed = 0
    for r in results:
        if isinstance(r, tuple) and len(r) >= 2:
            if r[1]:
                passed += 1
    
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed ({percentage:.0f}%)")
    
    if percentage == 100:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🎉 ALL TESTS PASSED!                                           ║
║                                                                   ║
║   ✅ Product is ready for Urbanrise demo                          ║
║   ✅ All core features working                                    ║
║   ✅ Intelligence engine operational                              ║
║   ✅ Billing system ready                                         ║
║                                                                   ║
║   NEXT STEPS:                                                     ║
║   1. Set up Supabase database                                    ║
║   2. Configure Twilio WhatsApp                                   ║
║   3. Deploy to Railway                                           ║
║   4. Call Sunil at Urbanrise                                     ║
║                                                                   ║
║   💰 TARGET: $10k/month → $100k/month → $1M/month                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    elif percentage >= 80:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ⚠️  MOSTLY READY - Check failed tests                          ║
║                                                                   ║
║   Most features working, but some need attention.                ║
║   Fix the ❌ items above before demo.                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    else:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ❌ NOT READY - Significant issues                              ║
║                                                                   ║
║   Check .env configuration:                                      ║
║   - GOOGLE_API_KEY for Gemini                                    ║
║   - SUPERMEMORY_API_KEY for memory                               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    return percentage >= 80


if __name__ == "__main__":
    asyncio.run(test_all())

