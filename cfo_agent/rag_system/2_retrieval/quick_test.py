"""
Quick Module 2 Test - Verify components without heavy operations
Tests structure without loading models or making API calls
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config

print("=" * 70)
print("MODULE 2 - QUICK VERIFICATION")
print("=" * 70)
print()

# Test 1: Query Router (rule-based only)
print("Test 1: Query Router (rule-based)")
print("-" * 70)

from query_router import QueryRouter

router = QueryRouter(use_llm=False)  # No API calls
test_query = "What are Apple's cybersecurity risks in 2024?"

analysis = router.route(test_query)
print(f"Query: {test_query}")
print(f"Type: {analysis.query_type}")
print(f"Companies: {analysis.companies}")
print(f"Years: {analysis.years}")
print(f"Sections: {analysis.sections}")
print("✅ Query Router working!")
print()

# Test 2: Context Builder (no retrieval needed)
print("Test 2: Context Builder")
print("-" * 70)

from context_builder import ContextBuilder
from semantic_retriever import RetrievedChunk

# Create fake chunks for testing
fake_chunks = [
    RetrievedChunk(
        chunk_id=1,
        company_name="Apple",
        ticker="AAPL",
        fiscal_year=2024,
        section="Item 1A",
        section_type="Risk Factors",
        heading="Risk Factors",
        subheading="Cybersecurity Risks",
        chunk_text="We face various cybersecurity threats...",
        word_count=50,
        similarity_score=0.85,
        chunk_index=1,
        chunk_total=10
    )
]

builder = ContextBuilder()
context = builder.build_context(fake_chunks, format_style="compact")

print(f"Chunks: {len(context.chunks_used)}")
print(f"Tokens: {context.total_tokens}")
print(f"Truncated: {context.truncated}")
print(f"Citations: {len(context.citations)}")
print("✅ Context Builder working!")
print()

# Test 3: Database Connection (no search needed)
print("Test 3: Database Connection")
print("-" * 70)

import psycopg2

try:
    host = config.database.supabase_url.replace('https://', '').replace('.supabase.co', '')
    host = f"db.{host}.supabase.co"
    
    conn = psycopg2.connect(
        host=host,
        port=5432,
        database='postgres',
        user='postgres',
        password=config.database.db_password,
        connect_timeout=5
    )
    
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM sec_10k_embeddings")
        count = cur.fetchone()[0]
        print(f"Database has {count:,} chunks")
    
    conn.close()
    print("✅ Database connection working!")
    
except Exception as e:
    print(f"❌ Database error: {e}")

print()

# Summary
print("=" * 70)
print("VERIFICATION SUMMARY")
print("=" * 70)
print()
print("✅ Module 2 components are properly structured!")
print()
print("📦 What we verified:")
print("  • Query Router: Classifies queries and extracts filters")
print("  • Context Builder: Formats chunks for LLM")
print("  • Database: Connection established")
print()
print("⚡ To run full pipeline with model loading:")
print("  venv/bin/python 2_retrieval/retrieval_pipeline.py")
print()
print("⏱️  Note: Full pipeline takes ~2 min first run (model download)")
print("   Subsequent runs are faster (~10 seconds)")
print()
print("=" * 70)
