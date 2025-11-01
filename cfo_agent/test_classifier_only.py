"""
Quick test - Just test the classifier (no API calls)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'rag_system' / '4_enhanced_capabilities' / 'classifiers'))

from enhanced_classifier import EnhancedQueryClassifier

print("="*80)
print("TESTING ENHANCED CLASSIFIER - NO API CALLS")
print("="*80)
print()

classifier = EnhancedQueryClassifier()

test_queries = [
    ("Summarize all major risk factors for Apple in 2022", "disclosure_summary"),
    ("What are Apple's ESG commitments in 2022?", "esg_regulatory"),
    ("Create a board briefing from Apple's 2022 10-K", "board_briefing"),
    ("What was Apple's operating cash flow in 2022?", "financial_extraction"),
    ("How did R&D expense change over 3 years?", "historical_comparison"),
    ("Compare Apple and Microsoft debt ratios", "peer_benchmark"),
    ("Analyze CEO tone in MD&A", "sentiment_analysis"),
    ("List SOX compliance disclosures", "compliance_review"),
]

print(f"Testing {len(test_queries)} queries...\n")

correct = 0
for query, expected in test_queries:
    result = classifier.classify(query)
    actual = result.capability.value
    match = "✅" if actual == expected else "❌"
    
    if actual == expected:
        correct += 1
    
    print(f"{match} Expected: {expected:<25} Got: {actual:<25}")
    print(f"   Query: {query[:60]}...")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Entities: Companies={result.entities['companies']}, Years={result.entities['years']}")
    print()

print("="*80)
print(f"RESULTS: {correct}/{len(test_queries)} correct ({correct/len(test_queries)*100:.0f}%)")
print("="*80)

if correct == len(test_queries):
    print("\n🎉 ALL TESTS PASSED!")
    sys.exit(0)
else:
    print(f"\n⚠️  {len(test_queries) - correct} test(s) failed")
    sys.exit(1)
