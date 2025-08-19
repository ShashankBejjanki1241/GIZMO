#!/usr/bin/env python3
"""
Test script to verify environment setup for Gizmo AI
Tests OpenAI API key configuration and environment loading
"""

import os
from dotenv import load_dotenv

def test_environment_setup():
    """Test environment variable loading"""
    print("🧪 Testing Gizmo AI Environment Setup")
    print("=" * 50)
    
    # Test 1: Load environment from .env file
    print("\n🔌 Test 1: Environment File Loading")
    print("-" * 40)
    
    # Load .env file
    load_dotenv()
    print("✅ dotenv.load_dotenv() called")
    
    # Test 2: Check OpenAI configuration
    print("\n🔑 Test 2: OpenAI API Configuration")
    print("-" * 40)
    
    api_key = os.getenv('OPENAI_API_KEY')
    agent_model = os.getenv('AGENT_MODEL', 'gpt-4o-mini')
    
    if api_key:
        print(f"✅ OPENAI_API_KEY: {'SET' if api_key else 'NOT SET'}")
        print(f"🔧 AGENT_MODEL: {agent_model}")
        
        # Check if it's a valid format (starts with sk-)
        if api_key.startswith('sk-'):
            print("✅ API key format appears valid")
        else:
            print("⚠️ API key format may be invalid")
    else:
        print("❌ OPENAI_API_KEY: NOT SET")
        print("⚠️ Real LLM integration will use stubbed responses")
    
    # Test 3: Check other environment variables
    print("\n🌍 Test 3: Other Environment Variables")
    print("-" * 40)
    
    env_vars = {
        'DB_HOST': os.getenv('DB_HOST'),
        'REDIS_HOST': os.getenv('REDIS_HOST'),
        'LOG_LEVEL': os.getenv('LOG_LEVEL'),
        'DEBUG': os.getenv('DEBUG')
    }
    
    for var, value in env_vars.items():
        status = "✅ SET" if value else "⚠️ NOT SET"
        print(f"{var}: {status} ({value if value else 'None'})")
    
    # Test 4: Environment Summary
    print("\n🎯 Environment Setup Test Results")
    print("=" * 40)
    
    if api_key:
        print("🎉 OPENAI API KEY CONFIGURED SUCCESSFULLY!")
        print("✅ Real LLM integration should work")
        print("✅ Agents can use OpenAI for planning, coding, and testing")
    else:
        print("⚠️ OPENAI API KEY NOT CONFIGURED")
        print("📝 System will fall back to stubbed responses")
        print("💡 To enable real LLM integration:")
        print("   1. Set OPENAI_API_KEY in .env file")
        print("   2. Restart the orchestrator service")
    
    print(f"\n🔧 Current Configuration:")
    print(f"   Model: {agent_model}")
    print(f"   API Key: {'Available' if api_key else 'Not Available'}")
    print(f"   Environment: {os.getenv('NODE_ENV', 'development')}")

if __name__ == "__main__":
    test_environment_setup()
