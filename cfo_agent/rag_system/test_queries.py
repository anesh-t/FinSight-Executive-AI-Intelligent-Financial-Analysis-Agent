"""
Test Real User Queries - See what the system can and cannot do
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / '2_retrieval'))

from query_router import QueryRouter
from semantic_retriever import SemanticRetriever
from context_builder import ContextBuilder

print("=" * 80)
print("TESTING REAL USER QUERIES")
print("=" * 80)
print()

retriever = SemanticRetriever()
router = QueryRouter(use_llm=False)
builder = ContextBuilder()

# Test Query 1
print("=" * 80)
print("TEST QUERY 1")
print("=" * 80)
query1 = "show apple top 10 risks in 2023"
print(f"Query: {query1}")
print()

# Route and extract filters
analysis1 = router.route(query1)
print(f"✅ Detected: Company={analysis1.companies}, Year={analysis1.years}, Section={analysis1.sections}")
print()

# Retrieve
chunks1 = retriever.retrieve(
    query="business risks challenges threats vulnerabilities",  # Broad risk query
    top_k=10,
    companies=["Apple"],
    years=[2023],
    sections=["Risk Factors"] if analysis1.sections else None
)

print(f"✅ Retrieved {len(chunks1)} risk chunks from Apple 2023")
print()

# Show what we got
print("📄 Retrieved Risks:")
for i, chunk in enumerate(chunks1, 1):
    print(f"{i}. {chunk.heading}")
    if chunk.subheading:
        print(f"   → {chunk.subheading}")
    print(f"   Preview: {chunk.chunk_text[:100]}...")
    print()

# What's missing
print("❌ WHAT WE'RE MISSING:")
print("   - No automatic answer generation")
print("   - We retrieved the chunks, but need an LLM to:")
print("     • Summarize the top 10 risks")
print("     • Format as a list")
print("     • Generate natural language response")
print()
print("✅ WHAT WE HAVE:")
print("   - All relevant risk chunks retrieved")
print("   - Properly filtered (Apple + 2023 + Risk Factors)")
print("   - Context ready to send to LLM manually")
print()

print("\n" + "="*80 + "\n")

# Test Query 2
print("=" * 80)
print("TEST QUERY 2")
print("=" * 80)
query2 = "compare apple and microsoft top 3 risks and mention what common risks they have"
print(f"Query: {query2}")
print()

# Route
analysis2 = router.route(query2)
print(f"✅ Detected: Companies={analysis2.companies}, Section={analysis2.sections}")
print()

# Retrieve for each company
print("Retrieving Apple risks...")
apple_chunks = retriever.retrieve(
    query="business risks challenges threats",
    top_k=3,
    companies=["Apple"],
    years=[2023, 2024],
    sections=["Risk Factors"]
)

print("Retrieving Microsoft risks...")
msft_chunks = retriever.retrieve(
    query="business risks challenges threats",
    top_k=3,
    companies=["Microsoft"],
    years=[2023, 2024],
    sections=["Risk Factors"]
)

print()
print(f"✅ Retrieved {len(apple_chunks)} Apple risks, {len(msft_chunks)} Microsoft risks")
print()

# Show what we got
print("📄 APPLE RISKS:")
for i, chunk in enumerate(apple_chunks, 1):
    print(f"{i}. {chunk.heading} ({chunk.fiscal_year})")
    print(f"   {chunk.chunk_text[:150]}...")
    print()

print("📄 MICROSOFT RISKS:")
for i, chunk in enumerate(msft_chunks, 1):
    print(f"{i}. {chunk.heading} ({chunk.fiscal_year})")
    print(f"   {chunk.chunk_text[:150]}...")
    print()

# What's missing
print("❌ WHAT WE'RE MISSING:")
print("   - No automatic comparison")
print("   - No common risk extraction")
print("   - We have the data, but need an LLM to:")
print("     • Compare the risk themes")
print("     • Identify common risks")
print("     • Generate comparative analysis")
print("     • Format as a structured answer")
print()
print("✅ WHAT WE HAVE:")
print("   - All relevant chunks from both companies")
print("   - Properly filtered by company and section")
print("   - Context ready for comparison")
print()

# Build context for manual LLM use
all_chunks = apple_chunks + msft_chunks
context = builder.build_context(all_chunks, format_style="compact")
rag_prompt = builder.build_rag_prompt(query2, context)

print("=" * 80)
print("SUMMARY: WHAT YOUR SYSTEM CAN DO NOW")
print("=" * 80)
print()
print("✅ YES - Retrieval:")
print("   • Extract company/year filters automatically")
print("   • Retrieve top-K most relevant chunks")
print("   • Filter by company, year, section")
print("   • Rank by relevance")
print("   • Format context with citations")
print()
print("❌ NO - Answer Generation:")
print("   • Cannot generate natural language answers")
print("   • Cannot compare and synthesize")
print("   • Cannot extract common themes automatically")
print("   • Cannot format as lists/tables")
print()
print("🔧 CURRENT WORKAROUND:")
print("   1. System retrieves relevant chunks ✅")
print("   2. System builds RAG prompt ✅")
print("   3. YOU manually send prompt to ChatGPT/Claude")
print("   4. LLM generates the answer")
print()
print("🚀 WHAT MODULE 4 WILL ADD:")
print("   • Automatic LLM integration")
print("   • Answer generation")
print("   • Comparison and synthesis")
print("   • Complete end-to-end responses")
print()
print(f"📝 RAG prompt ready ({len(rag_prompt)} chars)")
print("   You can copy this and paste into ChatGPT to get your answer!")
print()

# Show prompt preview
print("=" * 80)
print("RAG PROMPT (First 500 chars) - Ready to use in ChatGPT:")
print("=" * 80)
print(rag_prompt[:500])
print("...")
print()

retriever.close()
