"""
Test Streamlit Integration - Verify quick mode works through master agent
"""

import sys
from pathlib import Path
import time

# Test the full integration path (same as Streamlit uses)
from master_agent import UnifiedCFOAgent

print("="*80)
print("TESTING STREAMLIT INTEGRATION - QUICK MODE")
print("="*80)
print()

# Initialize agent (same way Streamlit does)
print("🚀 Initializing Unified CFO Agent...")
agent = UnifiedCFOAgent(verbose=False)  # Quick mode is default
print("✅ Agent initialized\n")

# Test query
query = "Summarize Apple's major risk factors in 2022"
print(f"Query: {query}")
print()

print("🔄 Processing (this should take 5-7 seconds)...")
start = time.time()

result = agent.query(query)

elapsed = time.time() - start

print()
print("="*80)
print("RESULT")
print("="*80)
print()
print(f"Success: {result.success}")
print(f"Time: {elapsed:.2f}s")
print(f"Intent: {result.intent}")
print(f"Data Sources: {result.data_sources}")
print()

if result.success:
    print("Answer (first 600 chars):")
    print("-"*80)
    print(result.answer[:600])
    if len(result.answer) > 600:
        print("...")
    print("-"*80)
    print()
    print(f"Full answer length: {len(result.answer)} characters")
    print()
    
    # Check for quick mode features
    has_quick_summary = "QUICK SUMMARY" in result.answer
    has_follow_ups = "WANT MORE DETAILS" in result.answer or "💡" in result.answer
    has_direct_answer = "DIRECT ANSWER" in result.answer
    
    print("Quick Mode Features:")
    print(f"  ✅ Quick Summary Format: {'Yes' if has_quick_summary else 'No'}")
    print(f"  ✅ Follow-up Questions: {'Yes' if has_follow_ups else 'No'}")
    print(f"  ✅ Direct Answer: {'Yes' if has_direct_answer else 'No'}")
    print()
    
    if elapsed <= 10:
        print("✅ PERFORMANCE TARGET MET: <= 10 seconds")
    elif elapsed <= 15:
        print("⚠️  ACCEPTABLE: <= 15 seconds")
    else:
        print("❌ SLOW: > 15 seconds")
else:
    print("Error:")
    print(result.answer)

print()

agent.close()

print("="*80)
print("INTEGRATION TEST COMPLETE")
print("="*80)
print()

if result.success and elapsed <= 10:
    print("🎉 SUCCESS: Quick mode is working through master agent!")
    print("   Ready to use in Streamlit!")
else:
    print("⚠️  Check results above")

print()
