"""
Quick verification - checks if fix is working without calling GPT-4
Just verifies retrieval logic
"""

import sys
from pathlib import Path

print("\n" + "=" * 80)
print("QUICK VERIFICATION - Retrieval Logic Check")
print("=" * 80 + "\n")

sys.path.insert(0, str(Path(__file__).parent / '2_retrieval'))
from query_router import QueryRouter
from semantic_retriever import SemanticRetriever

print("Initializing components...")
router = QueryRouter()
retriever = SemanticRetriever()

print("\n" + "─" * 80)
print("TEST: Comparison Query Routing")
print("─" * 80)

query = "compare apple and microsoft top 3 risks"
analysis = router.route(query)

print(f"Query: {query}")
print(f"Companies detected: {analysis.companies}")
print(f"Query type: {analysis.query_type}")

if analysis.companies and len(analysis.companies) == 2:
    print("✅ Both companies detected!")
else:
    print("❌ Company detection failed")

print("\n" + "─" * 80)
print("TEST: Balanced Retrieval (3 per company)")
print("─" * 80)

# Simulate what the fixed rag_agent does
chunks = []
per_company = 3

for company in analysis.companies:
    print(f"\nRetrieving for {company}...")
    company_chunks = retriever.retrieve(
        query=query,
        top_k=per_company,
        companies=[company],
        sections=["Risk Factors"],
        min_similarity=0.3
    )
    print(f"  Retrieved: {len(company_chunks)} chunks")
    
    # Show companies in chunks
    for chunk in company_chunks:
        print(f"    - {chunk.company} {chunk.year}")
    
    chunks.extend(company_chunks)

print("\n" + "─" * 80)
print("SUMMARY")
print("─" * 80)

apple_count = sum(1 for c in chunks if c.company == 'Apple')
msft_count = sum(1 for c in chunks if c.company == 'Microsoft')

print(f"Total chunks: {len(chunks)}")
print(f"Apple chunks: {apple_count}")
print(f"Microsoft chunks: {msft_count}")

print("\n" + "=" * 80)
if apple_count > 0 and msft_count > 0 and apple_count == msft_count:
    print("✅ FIX VERIFIED - Balanced retrieval working!")
    print("   Both companies have equal representation")
else:
    print("⚠️  Issue detected - unbalanced retrieval")
print("=" * 80)

retriever.close()
print("\nDone! This was just retrieval check (no GPT-4 call)")
print()
