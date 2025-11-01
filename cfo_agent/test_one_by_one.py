"""
Test One Query at a Time - Manual Control
Run each test individually to see immediate output
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '4_enhanced_capabilities'))

from enhanced_rag_agent import EnhancedRAGAgent

# Get test number from command line
if len(sys.argv) < 2:
    print("Usage: python test_one_by_one.py <test_number>")
    print()
    print("Available tests:")
    print("  1. Disclosure: Summarize Apple's risks")
    print("  2. Disclosure: What are key risks?")
    print("  3. ESG: Apple's ESG commitments")
    print("  4. ESG: Environmental initiatives")
    print("  5. Board: Create board briefing")
    print("  6. Board: Executive overview")
    print("  7. Financial: Cash flow")
    print("  8. Financial: Revenue")
    print()
    print("Example: python test_one_by_one.py 1")
    sys.exit(0)

test_num = int(sys.argv[1])

# Test cases
tests = [
    ("Disclosure Summarization", "Summarize Apple's major risk factors in 2022"),
    ("Disclosure Summarization", "What are the key risks for Apple?"),
    ("ESG & Regulatory", "What are Apple's ESG commitments in 2022?"),
    ("ESG & Regulatory", "Summarize Apple's environmental initiatives"),
    ("Board Briefing", "Create a board briefing from Apple's 2022 10-K"),
    ("Board Briefing", "Generate an executive overview for Apple"),
    ("Financial Extraction", "What was Apple's cash flow in 2022?"),
    ("Financial Extraction", "Show me Apple's revenue in 2022?"),
]

if test_num < 1 or test_num > len(tests):
    print(f"Error: Test number must be between 1 and {len(tests)}")
    sys.exit(1)

category, query = tests[test_num - 1]

print("="*80)
print(f"TEST {test_num}/{len(tests)}: {category}")
print("="*80)
print()
print(f"Query: {query}")
print()

# Initialize agent
print("🚀 Initializing Enhanced RAG Agent...")
agent = EnhancedRAGAgent(verbose=True, use_quick_mode=True)
print()

# Run query
print("🔄 Processing query...")
print()

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
print(f"Capability: {result.capability}")
print(f"Confidence: {result.confidence:.2f}")
print()

if result.success:
    print("Answer (first 500 chars):")
    print("-"*80)
    print(result.answer[:500])
    if len(result.answer) > 500:
        print("...")
    print("-"*80)
    print()
    print(f"Full answer length: {len(result.answer)} characters")
else:
    print("Error:")
    print(result.answer)

print()

agent.close()

print("="*80)
print("TEST COMPLETE")
print("="*80)
