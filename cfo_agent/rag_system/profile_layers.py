"""
Layer-by-Layer Performance Profiling
Measures exact time for each layer to identify bottlenecks
"""

import sys
from pathlib import Path
import time

print("\n" + "=" * 80)
print("⚡ LAYER-BY-LAYER PERFORMANCE PROFILING")
print("=" * 80 + "\n")

test_query = "What are Apple's top 3 cybersecurity risks in 2022?"
print(f"Test Query: {test_query}\n")

times = {}

# =============================================================================
# LAYER 1: QUERY ROUTING
# =============================================================================
print("🔍 LAYER 1: QUERY ROUTING")
print("─" * 80)

sys.path.insert(0, str(Path(__file__).parent / '2_retrieval'))
from query_router import QueryRouter

start = time.time()
router = QueryRouter()
analysis = router.route(test_query)
times['routing'] = time.time() - start

print(f"✅ Query routed: {times['routing']:.3f}s")
print(f"   Type: {analysis.query_type}")
print(f"   Companies: {analysis.companies}")
print(f"   Years: {analysis.years}")

# =============================================================================
# LAYER 2: EMBEDDING MODEL LOADING
# =============================================================================
print("\n🔍 LAYER 2: EMBEDDING MODEL LOADING")
print("─" * 80)

from semantic_retriever import SemanticRetriever

start = time.time()
retriever = SemanticRetriever()
times['model_loading'] = time.time() - start

print(f"✅ Model loaded: {times['model_loading']:.2f}s")

# =============================================================================
# LAYER 3: QUERY EMBEDDING GENERATION
# =============================================================================
print("\n🔍 LAYER 3: QUERY EMBEDDING GENERATION")
print("─" * 80)

start = time.time()
query_embedding = retriever.embedder.model.encode([test_query])[0]
times['embedding'] = time.time() - start

print(f"✅ Query embedded: {times['embedding']:.3f}s")

# =============================================================================
# LAYER 4: VECTOR DATABASE SEARCH
# =============================================================================
print("\n🔍 LAYER 4: VECTOR DATABASE SEARCH")
print("─" * 80)

start = time.time()
chunks = retriever.retrieve(
    query=test_query,
    top_k=3,
    companies=["Apple"],
    years=[2022],
    sections=["Risk Factors"],
    min_similarity=0.3
)
times['vector_search'] = time.time() - start

print(f"✅ Vector search: {times['vector_search']:.3f}s")
print(f"   Retrieved: {len(chunks)} chunks")

# =============================================================================
# LAYER 5: CONTEXT BUILDING
# =============================================================================
print("\n🔍 LAYER 5: CONTEXT BUILDING")
print("─" * 80)

from context_builder import ContextBuilder

builder = ContextBuilder()

# Test detailed format
start = time.time()
context_detailed = builder.build_context(chunks, format_style="detailed")
times['context_detailed'] = time.time() - start

print(f"✅ Context (detailed): {times['context_detailed']:.3f}s")
print(f"   Tokens: {context_detailed.total_tokens}")

# Test compact format
start = time.time()
context_compact = builder.build_context(chunks, format_style="compact")
times['context_compact'] = time.time() - start

print(f"✅ Context (compact): {times['context_compact']:.3f}s")
print(f"   Tokens: {context_compact.total_tokens}")
print(f"   Savings: {context_detailed.total_tokens - context_compact.total_tokens} tokens ({100*(context_detailed.total_tokens - context_compact.total_tokens)/context_detailed.total_tokens:.1f}%)")

# =============================================================================
# LAYER 6: LLM GENERATION (GPT-4-Turbo)
# =============================================================================
print("\n🔍 LAYER 6: LLM GENERATION - GPT-4-TURBO")
print("─" * 80)

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from llm_client import LLMClient

llm_gpt4 = LLMClient(model="gpt-4-turbo-preview", temperature=0.1, max_tokens=2048)

prompt = f"""You are a CFO analyst. Provide a concise analysis.

CONTEXT:
{context_compact.formatted_context}

QUESTION:
{test_query}

ANALYSIS:"""

start = time.time()
response_gpt4 = llm_gpt4.generate(prompt, system_message="You are a CFO analyst.")
times['gpt4_turbo'] = time.time() - start

print(f"✅ GPT-4-Turbo: {times['gpt4_turbo']:.2f}s")
print(f"   Input tokens: ~{context_compact.total_tokens + 50}")
print(f"   Output tokens: {response_gpt4.total_tokens - context_compact.total_tokens - 50}")
print(f"   Cost: ${response_gpt4.cost:.4f}")

# =============================================================================
# LAYER 6B: LLM GENERATION (GPT-3.5-Turbo)
# =============================================================================
print("\n🔍 LAYER 6B: LLM GENERATION - GPT-3.5-TURBO (for comparison)")
print("─" * 80)

llm_gpt35 = LLMClient(model="gpt-3.5-turbo", temperature=0.1, max_tokens=2048)

start = time.time()
response_gpt35 = llm_gpt35.generate(prompt, system_message="You are a CFO analyst.")
times['gpt35_turbo'] = time.time() - start

print(f"✅ GPT-3.5-Turbo: {times['gpt35_turbo']:.2f}s")
print(f"   Input tokens: ~{context_compact.total_tokens + 50}")
print(f"   Output tokens: {response_gpt35.total_tokens - context_compact.total_tokens - 50}")
print(f"   Cost: ${response_gpt35.cost:.4f}")
print(f"   Speedup: {times['gpt4_turbo']/times['gpt35_turbo']:.1f}x faster than GPT-4-Turbo")

# =============================================================================
# LAYER 7: ANSWER FORMATTING
# =============================================================================
print("\n🔍 LAYER 7: ANSWER FORMATTING")
print("─" * 80)

start = time.time()
formatted = response_gpt4.text.strip()
times['formatting'] = time.time() - start

print(f"✅ Formatting: {times['formatting']:.4f}s")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("📊 PERFORMANCE BREAKDOWN")
print("=" * 80)

# Calculate totals
total_gpt4_first = (times['routing'] + times['model_loading'] + times['embedding'] + 
                    times['vector_search'] + times['context_compact'] + times['gpt4_turbo'] + 
                    times['formatting'])

total_gpt4_subsequent = (times['routing'] + times['embedding'] + times['vector_search'] + 
                        times['context_compact'] + times['gpt4_turbo'] + times['formatting'])

total_gpt35_subsequent = (times['routing'] + times['embedding'] + times['vector_search'] + 
                         times['context_compact'] + times['gpt35_turbo'] + times['formatting'])

print(f"\n1️⃣  FIRST QUERY (with model loading):")
print("─" * 80)
print(f"{'Layer':<40} {'Time (s)':<10} {'% of Total':<12}")
print("─" * 80)
print(f"{'1. Query Routing':<40} {times['routing']:>8.3f}s {100*times['routing']/total_gpt4_first:>10.1f}%")
print(f"{'2. Model Loading':<40} {times['model_loading']:>8.2f}s {100*times['model_loading']/total_gpt4_first:>10.1f}%")
print(f"{'3. Query Embedding':<40} {times['embedding']:>8.3f}s {100*times['embedding']/total_gpt4_first:>10.1f}%")
print(f"{'4. Vector Search (3 chunks)':<40} {times['vector_search']:>8.3f}s {100*times['vector_search']/total_gpt4_first:>10.1f}%")
print(f"{'5. Context Building (compact)':<40} {times['context_compact']:>8.3f}s {100*times['context_compact']/total_gpt4_first:>10.1f}%")
print(f"{'6. GPT-4-Turbo Generation':<40} {times['gpt4_turbo']:>8.2f}s {100*times['gpt4_turbo']/total_gpt4_first:>10.1f}%")
print(f"{'7. Formatting':<40} {times['formatting']:>8.4f}s {100*times['formatting']/total_gpt4_first:>10.1f}%")
print("─" * 80)
print(f"{'TOTAL (First Query)':<40} {total_gpt4_first:>8.2f}s {100.0:>10.1f}%")

print(f"\n2️⃣  SUBSEQUENT QUERIES (model already loaded) - GPT-4-Turbo:")
print("─" * 80)
print(f"{'Layer':<40} {'Time (s)':<10} {'% of Total':<12}")
print("─" * 80)
print(f"{'1. Query Routing':<40} {times['routing']:>8.3f}s {100*times['routing']/total_gpt4_subsequent:>10.1f}%")
print(f"{'2. Query Embedding':<40} {times['embedding']:>8.3f}s {100*times['embedding']/total_gpt4_subsequent:>10.1f}%")
print(f"{'3. Vector Search':<40} {times['vector_search']:>8.3f}s {100*times['vector_search']/total_gpt4_subsequent:>10.1f}%")
print(f"{'4. Context Building':<40} {times['context_compact']:>8.3f}s {100*times['context_compact']/total_gpt4_subsequent:>10.1f}%")
print(f"{'5. GPT-4-Turbo Generation':<40} {times['gpt4_turbo']:>8.2f}s {100*times['gpt4_turbo']/total_gpt4_subsequent:>10.1f}%")
print(f"{'6. Formatting':<40} {times['formatting']:>8.4f}s {100*times['formatting']/total_gpt4_subsequent:>10.1f}%")
print("─" * 80)
print(f"{'TOTAL (Subsequent)':<40} {total_gpt4_subsequent:>8.2f}s {100.0:>10.1f}%")

print(f"\n3️⃣  SUBSEQUENT QUERIES - GPT-3.5-Turbo (FASTEST):")
print("─" * 80)
print(f"{'Layer':<40} {'Time (s)':<10} {'% of Total':<12}")
print("─" * 80)
print(f"{'1. Query Routing':<40} {times['routing']:>8.3f}s {100*times['routing']/total_gpt35_subsequent:>10.1f}%")
print(f"{'2. Query Embedding':<40} {times['embedding']:>8.3f}s {100*times['embedding']/total_gpt35_subsequent:>10.1f}%")
print(f"{'3. Vector Search':<40} {times['vector_search']:>8.3f}s {100*times['vector_search']/total_gpt35_subsequent:>10.1f}%")
print(f"{'4. Context Building':<40} {times['context_compact']:>8.3f}s {100*times['context_compact']/total_gpt35_subsequent:>10.1f}%")
print(f"{'5. GPT-3.5-Turbo Generation':<40} {times['gpt35_turbo']:>8.2f}s {100*times['gpt35_turbo']/total_gpt35_subsequent:>10.1f}%")
print(f"{'6. Formatting':<40} {times['formatting']:>8.4f}s {100*times['formatting']/total_gpt35_subsequent:>10.1f}%")
print("─" * 80)
print(f"{'TOTAL (Subsequent)':<40} {total_gpt35_subsequent:>8.2f}s {100.0:>10.1f}%")

# =============================================================================
# RECOMMENDATIONS
# =============================================================================
print("\n" + "=" * 80)
print("🎯 OPTIMIZATION TO REACH 7-10 SECONDS TARGET")
print("=" * 80)

print(f"\nCurrent Performance:")
print(f"  GPT-4-Turbo:  {total_gpt4_subsequent:.1f}s")
print(f"  GPT-3.5-Turbo: {total_gpt35_subsequent:.1f}s")

if total_gpt35_subsequent <= 10:
    print(f"\n✅ GPT-3.5-Turbo MEETS YOUR 7-10 SECOND TARGET!")
    print(f"   Result: {total_gpt35_subsequent:.1f} seconds")
else:
    print(f"\n⚠️  Even GPT-3.5-Turbo exceeds target by {total_gpt35_subsequent-10:.1f}s")

print(f"\n💡 RECOMMENDED CONFIGURATION:")
print(f"   model = 'gpt-3.5-turbo'")
print(f"   top_k = 3")
print(f"   format_style = 'compact'")
print(f"\n   Expected time: {total_gpt35_subsequent:.1f} seconds")
print(f"   Cost per query: ${response_gpt35.cost:.4f}")
print(f"   Speed improvement: {total_gpt4_subsequent/total_gpt35_subsequent:.1f}x faster than GPT-4-Turbo")

retriever.close()
print("\n" + "=" * 80)
print()
