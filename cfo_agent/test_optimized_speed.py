"""
Test Optimized Speed - Compare Quick Mode vs Detailed Mode
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '4_enhanced_capabilities'))

from enhanced_rag_agent import EnhancedRAGAgent

print("="*80)
print("SPEED OPTIMIZATION TEST")
print("="*80)
print()

# Test query
query = "Summarize Apple's major risk factors in 2022"

# Test 1: Quick Mode (Optimized)
print("TEST 1: QUICK MODE (Optimized)")
print("-"*80)
print(f"Query: {query}\n")

agent_quick = EnhancedRAGAgent(verbose=False, use_quick_mode=True)

start = time.time()
result_quick = agent_quick.query(query)
time_quick = time.time() - start

print(f"✅ Success: {result_quick.success}")
print(f"⏱️  Time: {time_quick:.2f}s")
print(f"📊 Capability: {result_quick.capability}")
print()
print("📄 Answer Preview (first 400 chars):")
print("-"*80)
print(result_quick.answer[:400] + "...")
print("-"*80)
print()

agent_quick.close()

# Test 2: Detailed Mode (Original)
print("\nTEST 2: DETAILED MODE (Original)")
print("-"*80)
print(f"Query: {query}\n")

agent_detailed = EnhancedRAGAgent(verbose=False, use_quick_mode=False)

start = time.time()
result_detailed = agent_detailed.query(query)
time_detailed = time.time() - start

print(f"✅ Success: {result_detailed.success}")
print(f"⏱️  Time: {time_detailed:.2f}s")
print(f"📊 Capability: {result_detailed.capability}")
print()
print("📄 Answer Preview (first 400 chars):")
print("-"*80)
print(result_detailed.answer[:400] + "...")
print("-"*80)
print()

agent_detailed.close()

# Comparison
print("\n" + "="*80)
print("PERFORMANCE COMPARISON")
print("="*80)
print()
print(f"Quick Mode:    {time_quick:.2f}s")
print(f"Detailed Mode: {time_detailed:.2f}s")
print()

improvement = ((time_detailed - time_quick) / time_detailed) * 100
print(f"Speed Improvement: {improvement:.1f}% faster")
print(f"Time Saved: {time_detailed - time_quick:.2f}s")
print()

if time_quick < 10:
    print("✅ TARGET ACHIEVED: < 10 seconds")
elif time_quick < 15:
    print("⚠️  GOOD: < 15 seconds")
else:
    print("❌ NEEDS MORE OPTIMIZATION")

print()
print("="*80)
