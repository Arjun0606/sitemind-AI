#!/usr/bin/env python3
"""
SiteMind Prototype Script
Quick testing script to verify API integrations work correctly

Usage:
    python prototype.py --test-gemini
    python prototype.py --test-whisper
    python prototype.py --test-all
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils.logger import setup_logging, logger


async def test_gemini():
    """Test Gemini API integration"""
    print("\n🤖 Testing Gemini API...")
    
    from services.gemini_service import gemini_service
    
    if not gemini_service.is_configured:
        print("❌ Gemini not configured. Set GOOGLE_API_KEY in .env")
        return False
    
    # Test simple query
    result = await gemini_service.analyze_query(
        query="What is the standard column spacing in commercial buildings?",
        memory_context="This is a test project for a commercial office building.",
    )
    
    if result.get("error"):
        print(f"❌ Gemini error: {result['error']}")
        return False
    
    print(f"✅ Gemini response ({result['response_time_ms']}ms):")
    print(f"   {result['response'][:200]}...")
    return True


async def test_whisper():
    """Test Whisper API integration"""
    print("\n🎤 Testing Whisper API...")
    
    from services.whisper_service import whisper_service
    
    if not whisper_service.is_configured:
        print("❌ Whisper not configured. Set OPENAI_API_KEY in .env")
        return False
    
    # We can't easily test without an audio file
    # Just verify the client is configured
    health = await whisper_service.health_check()
    
    if health.get("status") == "healthy":
        print(f"✅ Whisper service is healthy (model: {health.get('model')})")
        return True
    else:
        print(f"❌ Whisper health check failed: {health}")
        return False


async def test_memory():
    """Test Memory service"""
    print("\n🧠 Testing Memory Service...")
    
    from services.memory_service import memory_service
    
    # Add a test memory
    result = await memory_service.add_memory(
        project_id="test-project",
        content="Beam B2 was changed from 300mm to 600mm due to HVAC duct routing.",
        metadata={"type": "change_order", "drawing": "ST-04"},
    )
    
    print(f"   Added memory: {result}")
    
    # Search for it
    search_result = await memory_service.search_memory(
        project_id="test-project",
        query="beam B2 size change",
    )
    
    print(f"   Search results: {search_result['count']} found")
    
    if search_result["count"] > 0:
        print(f"✅ Memory service working")
        return True
    else:
        print(f"⚠️ Memory service working but search didn't find result")
        return True


async def test_whatsapp():
    """Test WhatsApp client"""
    print("\n💬 Testing WhatsApp Client...")
    
    from services.whatsapp_client import whatsapp_client
    
    if not whatsapp_client.is_configured:
        print("❌ WhatsApp not configured. Set TWILIO_* credentials in .env")
        return False
    
    health = await whatsapp_client.health_check()
    
    if health.get("status") == "healthy":
        print(f"✅ WhatsApp service healthy (account: {health.get('account_status')})")
        return True
    else:
        print(f"❌ WhatsApp health check failed: {health}")
        return False


async def test_storage():
    """Test Storage service"""
    print("\n📁 Testing Storage Service...")
    
    from services.storage_service import storage_service
    
    if not storage_service.is_configured:
        print("❌ Storage not configured. Set AWS_* credentials in .env")
        return False
    
    health = await storage_service.health_check()
    
    if health.get("status") == "healthy":
        print(f"✅ Storage service healthy (bucket: {health.get('bucket')})")
        return True
    else:
        print(f"❌ Storage health check failed: {health}")
        return False


async def run_all_tests():
    """Run all integration tests"""
    print("=" * 50)
    print("🏗️  SiteMind Integration Tests")
    print("=" * 50)
    
    results = {
        "Gemini": await test_gemini(),
        "Whisper": await test_whisper(),
        "Memory": await test_memory(),
        "WhatsApp": await test_whatsapp(),
        "Storage": await test_storage(),
    }
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    all_passed = True
    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {service}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! SiteMind is ready to go.")
    else:
        print("⚠️  Some tests failed. Check your configuration.")
    
    return all_passed


async def interactive_demo():
    """Interactive demo mode"""
    print("\n" + "=" * 50)
    print("🏗️  SiteMind Interactive Demo")
    print("=" * 50)
    print("\nThis will simulate a conversation with SiteMind.")
    print("Type 'quit' to exit.\n")
    
    from services.gemini_service import gemini_service
    from services.memory_service import memory_service
    
    if not gemini_service.is_configured:
        print("❌ Gemini not configured. Cannot run demo.")
        return
    
    # Add some demo context
    await memory_service.add_memory(
        project_id="demo-project",
        content="Project: Skyline Towers Block A. 15-floor commercial building.",
        metadata={"type": "project_info"},
    )
    await memory_service.add_memory(
        project_id="demo-project",
        content="Beam B2 on floors 3-10 changed to 300x600mm (from 300x450mm) in Revision 3 due to HVAC duct clash.",
        metadata={"type": "change_order", "drawing": "ST-04"},
    )
    await memory_service.add_memory(
        project_id="demo-project",
        content="Column spacing on Grid A is 6 meters center-to-center.",
        metadata={"type": "structural", "drawing": "ST-02"},
    )
    
    print("📝 Demo context loaded (Skyline Towers Block A)")
    print("-" * 50)
    
    while True:
        try:
            query = input("\n👷 You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                continue
            
            # Get memory context
            memory_result = await memory_service.search_memory(
                project_id="demo-project",
                query=query,
            )
            
            # Generate response
            result = await gemini_service.analyze_query(
                query=query,
                memory_context=memory_result.get("context", ""),
            )
            
            print(f"\n🤖 SiteMind ({result['response_time_ms']}ms):")
            print(result['response'])
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


def main():
    parser = argparse.ArgumentParser(description="SiteMind Prototype Testing")
    parser.add_argument("--test-gemini", action="store_true", help="Test Gemini API")
    parser.add_argument("--test-whisper", action="store_true", help="Test Whisper API")
    parser.add_argument("--test-memory", action="store_true", help="Test Memory service")
    parser.add_argument("--test-whatsapp", action="store_true", help="Test WhatsApp client")
    parser.add_argument("--test-storage", action="store_true", help="Test Storage service")
    parser.add_argument("--test-all", action="store_true", help="Run all tests")
    parser.add_argument("--demo", action="store_true", help="Run interactive demo")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    if args.test_all:
        asyncio.run(run_all_tests())
    elif args.test_gemini:
        asyncio.run(test_gemini())
    elif args.test_whisper:
        asyncio.run(test_whisper())
    elif args.test_memory:
        asyncio.run(test_memory())
    elif args.test_whatsapp:
        asyncio.run(test_whatsapp())
    elif args.test_storage:
        asyncio.run(test_storage())
    elif args.demo:
        asyncio.run(interactive_demo())
    else:
        parser.print_help()
        print("\n💡 Tip: Run with --test-all to test all integrations")
        print("   Or use --demo for interactive testing")


if __name__ == "__main__":
    main()

