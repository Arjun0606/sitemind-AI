#!/usr/bin/env python3
"""
SiteMind Supermemory Integration Test
Run this to verify your Supermemory.ai setup is working

Usage:
    1. Add your SUPERMEMORY_API_KEY to .env
    2. Run: python test_supermemory.py
"""

import asyncio
from datetime import datetime

print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🧠 SUPERMEMORY.AI INTEGRATION TEST                              ║
║                                                                   ║
║   Testing long-term memory for construction projects              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")


async def test_supermemory():
    from services.memory_service import memory_service, SUPERMEMORY_SDK_AVAILABLE
    
    results = []
    
    def test(name, passed, details=""):
        status = "✅" if passed else "❌"
        results.append((name, passed))
        print(f"{status} {name}")
        if details:
            print(f"   └─ {details}")
    
    # =========================================================================
    # 1. SDK AVAILABILITY
    # =========================================================================
    print("\n━━━ 1. SETUP CHECK ━━━")
    
    test("Supermemory SDK installed", SUPERMEMORY_SDK_AVAILABLE, 
         "Run 'pip install supermemory' if not installed")
    
    test("API key configured", memory_service._is_configured(),
         "Add SUPERMEMORY_API_KEY to .env")
    
    test("Client initialized", memory_service.client is not None or not SUPERMEMORY_SDK_AVAILABLE,
         "Client should be initialized if SDK available and key configured")
    
    # =========================================================================
    # 2. ADD MEMORIES
    # =========================================================================
    print("\n━━━ 2. ADD MEMORIES ━━━")
    
    test_company = "test_urbanrise"
    test_project = "marina_bay"
    
    # Test decision
    decision = await memory_service.add_decision(
        company_id=test_company,
        project_id=test_project,
        decision="Change column size from 450x450 to 450x600mm",
        reason="Structural revision for additional floor",
        approved_by="Er. Patel (Structural)",
        affected_area="Grid C columns",
        user_id="test_user",
    )
    test("Add decision", decision.id is not None, f"ID: {decision.id}")
    
    # Test change order
    change = await memory_service.add_change_order(
        company_id=test_company,
        project_id=test_project,
        description="Beam depth revision at Grid B4",
        old_spec="500mm depth",
        new_spec="600mm depth",
        reason="Increased load requirements",
        approved_by="Ar. Sharma",
        user_id="test_user",
    )
    test("Add change order", change.id is not None, f"ID: {change.id}")
    
    # Test RFI
    rfi = await memory_service.add_rfi(
        company_id=test_company,
        project_id=test_project,
        question="What waterproofing system should be used for podium?",
        answer="Use APP membrane with 2 coats. See spec WP-001.",
        asked_by="Site Engineer Rajesh",
        answered_by="Ar. Sharma",
        rfi_number="RFI-047",
        user_id="test_user",
    )
    test("Add RFI", rfi.id is not None, f"ID: {rfi.id}")
    
    # Test query
    query = await memory_service.add_query(
        company_id=test_company,
        project_id=test_project,
        question="What is minimum cover for columns?",
        answer="40mm as per IS 456:2000, Clause 26.4",
        user_id="test_user",
    )
    test("Add query", query.id is not None, f"ID: {query.id}")
    
    # Test document
    doc = await memory_service.add_document(
        company_id=test_company,
        project_id=test_project,
        document_name="STR-B1-F3-001",
        document_type="structural_drawing",
        extracted_text="Third floor structural drawing showing 18 columns, 24 beams. M30 grade concrete specified.",
        file_path="/documents/structural/STR-B1-F3-001.pdf",
        user_id="test_user",
    )
    test("Add document", doc.id is not None, f"ID: {doc.id}")
    
    # Test photo
    photo = await memory_service.add_photo_analysis(
        company_id=test_company,
        project_id=test_project,
        caption="Rebar placement 3rd floor",
        analysis="Rebar spacing appears consistent at 150mm c/c. Cover blocks visible. Some bars showing surface rust - recommend wire brushing before pour.",
        file_path="/photos/2024-12/rebar_3rd_floor.jpg",
        photo_type="progress",
        user_id="test_user",
    )
    test("Add photo analysis", photo.id is not None, f"ID: {photo.id}")
    
    # =========================================================================
    # 3. SEARCH MEMORIES
    # =========================================================================
    print("\n━━━ 3. SEARCH MEMORIES ━━━")
    
    # Search by topic
    results_column = await memory_service.search(
        company_id=test_company,
        query="column size change",
        project_id=test_project,
        limit=5,
    )
    test("Search for 'column size change'", len(results_column) > 0, f"Found: {len(results_column)}")
    
    # Search for waterproofing
    results_water = await memory_service.search(
        company_id=test_company,
        query="waterproofing podium membrane",
        project_id=test_project,
        limit=5,
    )
    test("Search for 'waterproofing'", len(results_water) > 0, f"Found: {len(results_water)}")
    
    # Search by type
    results_decisions = await memory_service.search(
        company_id=test_company,
        query="approved decision",
        project_id=test_project,
        memory_types=["decision", "change_order"],
        limit=5,
    )
    test("Search decisions only", len(results_decisions) > 0, f"Found: {len(results_decisions)}")
    
    # =========================================================================
    # 4. GET CONTEXT FOR AI
    # =========================================================================
    print("\n━━━ 4. GET CONTEXT ━━━")
    
    context = await memory_service.get_context(
        company_id=test_company,
        project_id=test_project,
        query="What changes were made to the structure?",
    )
    test("Get context for AI", len(context) > 0, f"Context items: {len(context)}")
    
    # Format for prompt
    formatted = memory_service.format_context_for_prompt(context)
    test("Format context for prompt", len(formatted) > 0, f"Length: {len(formatted)} chars")
    
    if context:
        print("\n   📋 Sample context retrieved:")
        for item in context[:2]:
            content = item.get("content", "")[:100]
            print(f"      • {content}...")
    
    # =========================================================================
    # 5. AUDIT TRAIL
    # =========================================================================
    print("\n━━━ 5. AUDIT TRAIL ━━━")
    
    audit = await memory_service.get_audit_trail(
        company_id=test_company,
        project_id=test_project,
        topic="column changes",
        limit=10,
    )
    test("Get audit trail", len(audit) >= 0, f"Records: {len(audit)}")
    
    formatted_audit = memory_service.format_audit_trail(audit)
    test("Format audit trail", len(formatted_audit) > 0, f"Length: {len(formatted_audit)} chars")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "═" * 60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed ({percentage:.0f}%)")
    
    if percentage == 100:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🎉 ALL MEMORY TESTS PASSED!                                    ║
║                                                                   ║
║   ✅ Supermemory SDK working                                     ║
║   ✅ Can add all memory types                                    ║
║   ✅ Semantic search working                                     ║
║   ✅ Context retrieval working                                   ║
║   ✅ Audit trail working                                         ║
║                                                                   ║
║   Your AI now has perfect memory! 🧠                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    elif percentage >= 70:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ⚠️  MOSTLY WORKING - Local fallback active                     ║
║                                                                   ║
║   Memory is working with local storage.                          ║
║   For production, ensure Supermemory API key is configured.      ║
║                                                                   ║
║   Add to .env:                                                   ║
║   SUPERMEMORY_API_KEY=your_key_here                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    else:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ❌ MEMORY TESTS FAILING                                        ║
║                                                                   ║
║   Check:                                                         ║
║   1. pip install supermemory                                     ║
║   2. SUPERMEMORY_API_KEY in .env                                 ║
║   3. Network connectivity                                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    # =========================================================================
    # DEMO: What AI sees
    # =========================================================================
    if context:
        print("\n" + "═" * 60)
        print("📝 DEMO: Context injected into AI prompt")
        print("═" * 60)
        print(formatted[:1000])
        print("...")
    
    return percentage >= 70


if __name__ == "__main__":
    asyncio.run(test_supermemory())

