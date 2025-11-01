"""
Quick API Test - Check if OpenAI API is working
"""

import os
import sys
from pathlib import Path
import time

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '3_generation'))

print("="*80)
print("QUICK API TEST - OpenAI Connection")
print("="*80)
print()

# Check API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("❌ ERROR: OPENAI_API_KEY not found in environment")
    print("   Please set it in your .env file")
    sys.exit(1)
else:
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    print()

# Test LLM Client
try:
    from llm_client import LLMClient
    
    print("🔄 Testing OpenAI API connection...")
    print()
    
    # Create client
    client = LLMClient(
        model="gpt-3.5-turbo",
        temperature=0.1,
        max_tokens=100
    )
    
    print(f"✅ LLM Client created: {client.model}")
    print()
    
    # Test simple query
    print("🔄 Sending test query...")
    start_time = time.time()
    
    response = client.generate(
        prompt="Say 'API is working' in exactly 3 words.",
        system_message="You are a helpful assistant."
    )
    
    elapsed = time.time() - start_time
    
    print(f"✅ Response received in {elapsed:.2f}s")
    print()
    print("Response:")
    print(f"  Text: {response.text}")
    print(f"  Tokens: {response.total_tokens}")
    print(f"  Cost: ${response.cost:.4f}")
    print()
    
    if elapsed > 10:
        print("⚠️  WARNING: Response took > 10 seconds")
        print("   This is slower than expected")
        print("   Possible issues:")
        print("   - Network latency")
        print("   - OpenAI API rate limits")
        print("   - Model availability")
    else:
        print("✅ Response time is normal")
    
    print()
    print("="*80)
    print("API TEST COMPLETE - API IS WORKING")
    print("="*80)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print()
    print("Possible issues:")
    print("  1. Invalid API key")
    print("  2. Network connection problem")
    print("  3. OpenAI API is down")
    print("  4. Rate limit exceeded")
    print()
    import traceback
    print("Full error:")
    print(traceback.format_exc())
    sys.exit(1)
