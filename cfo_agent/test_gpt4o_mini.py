"""
Test GPT-4o-mini API - Quick validation
"""

import os
import sys
from pathlib import Path
import time
from dotenv import load_dotenv

# Load .env file
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '3_generation'))

print("="*80)
print("TESTING GPT-4O-MINI API")
print("="*80)
print()

# Check API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("❌ ERROR: OPENAI_API_KEY not found")
    print("   Set it in your .env file")
    sys.exit(1)

print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}\n")

# Test with gpt-4o-mini
try:
    from llm_client import LLMClient
    
    print("🔄 Testing gpt-4o-mini...")
    start = time.time()
    
    client = LLMClient(
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=50
    )
    
    response = client.generate(
        prompt="Say 'Working' in one word.",
        system_message="You are helpful."
    )
    
    elapsed = time.time() - start
    
    print(f"✅ Response in {elapsed:.2f}s")
    print(f"   Model: {response.model}")
    print(f"   Text: {response.text}")
    print(f"   Tokens: {response.total_tokens}")
    print(f"   Cost: ${response.cost:.6f}")
    print()
    
    if elapsed < 5:
        print("✅ FAST - Response time is excellent!")
    elif elapsed < 10:
        print("⚠️  MODERATE - Response time is acceptable")
    else:
        print("❌ SLOW - Response time is too high")
    
    print()
    print("="*80)
    print("✅ GPT-4O-MINI IS WORKING!")
    print("="*80)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)
