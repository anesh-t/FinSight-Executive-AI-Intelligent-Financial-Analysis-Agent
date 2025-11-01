"""
Layer-by-Layer Performance Profiling
Measures time for each component to identify bottlenecks
"""

import sys
from pathlib import Path
import time

print("\n" + "=" * 80)
print("LAYER-BY-LAYER PERFORMANCE PROFILING")
print("=" * 80 + "\n")

# Test query
test_query = "What are Apple's main cybersecurity risks in 2022?"

print(f"Test Query: {test_query}\n")
print("=" * 80)

# ============================================================================
# LAYER 1: EMBEDDING MODEL LOADING
# ============================================================================
print("\n🔍 LAYER 1: EMBEDDING MODEL LOADING")
print("─" * 80)

sys.path.insert(0, str(Path(__file__).parent / '2_retrieval'))

start = time.time()
from semantic_retriever import SemanticRetriever
load_time = time.time() - start

print(f"✅ Embedding model loaded: {load_time:.2f}s")
print(f"   Model: sentence-transformers/all-MiniLM-L6-v2")
print(f"   Size: ~22MB")

# ============================================================================
# LAYER 2: QUERY EMBEDDING GENERATION
# ============================================================================
print("\n🔍 LAYER 2: QUERY EMBEDDING GENERATION")
print("─" * 80)

retriever = SemanticRetriever()

start = time.time()
query_embedding = retriever.model.encode([test_query])[0]
embed_time = time.time() - start

print(f"✅ Query embedded: {embed_time:.3f}s")
print(f"   Input: '{test_query[:50]}...'")
print(f"   Output: 384-dimensional vector")

# ============================================================================
# LAYER 3: DATABASE CONNECTION
# ============================================================================
print("\n🔍 LAYER 3: DATABASE CONNECTION")
print("─" * 80)

start = time.time()
# Connection already established in retriever init
conn_time = time.time() - start

print(f"✅ Database connected: {conn_time:.3f}s")
print(f"   Already established during retriever init")

# ============================================================================
# LAYER 4: VECTOR SEARCH (DATABASE QUERY)
# ============================================================================
print("\n🔍 LAYER 4: VECTOR SEARCH")
print("─" * 80)

start = time.time()
chunks = retriever.retrieve(
    query=test_query,
    top_k=5,
    companies=["Apple"],
    years=[2022],
    sections=["Risk Factors"],
    min_similarity=0.3
)
search_time = time.time() - start

print(f"✅ Vector search completed: {search_time:.3f}s")
print(f"   Searched: 6,934 embeddings in PostgreSQL")
print(f"   Retrieved: {len(chunks)} chunks")
print(f"   Filters: Company=Apple, Year=2022, Section=Risk Factors")

# ============================================================================
# LAYER 5: CONTEXT BUILDING
# ============================================================================
print("\n🔍 LAYER 5: CONTEXT BUILDING")
print("─" * 80)

sys.path.insert(0, str(Path(__file__).parent / '2_retrieval'))
from context_builder import ContextBuilder

builder = ContextBuilder()

start = time.time()
context = builder.build_context(chunks, format_style="detailed")
context_time = time.time() - start

print(f"✅ Context built: {context_time:.3f}s")
print(f"   Chunks formatted: {len(context.chunks_used)}")
print(f"   Total tokens: {context.total_tokens}")
print(f"   Format: detailed")

# Test compact format
start = time.time()
context_compact = builder.build_context(chunks, format_style="compact")
context_compact_time = time.time() - start

print(f"✅ Context built (compact): {context_compact_time:.3f}s")
print(f"   Total tokens: {context_compact.total_tokens}")
print(f"   Savings: {context.total_tokens - context_compact.total_tokens} tokens ({100*(context.total_tokens - context_compact.total_tokens)/context.total_tokens:.1f}%)")

# ============================================================================
# LAYER 6: LLM API CALL (GPT-4-Turbo)
# ============================================================================
print("\n🔍 LAYER 6: LLM API CALL - GPT-4-TURBO")
print("─" * 80)

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from llm_client import LLMClient

llm_client = LLMClient(model="gpt-4-turbo-preview", temperature=0.1, max_tokens=2048)

prompt = f"""You are a CFO analyst. Answer this question based on the context.

CONTEXT:
{context.formatted_context}

QUESTION:
{test_query}

ANSWER:"""

start = time.time()
response = llm_client.generate(prompt, system_message="You are a CFO analyst.")
gpt4_time = time.time() - start

print(f"✅ GPT-4-Turbo response: {gpt4_time:.2f}s")
print(f"   Input tokens: ~{context.total_tokens + 100}")
print(f"   Output tokens: {response.total_tokens - context.total_tokens}")
print(f"   Cost: ${response.cost:.4f}")

# ============================================================================
# LAYER 6B: LLM API CALL (GPT-3.5-Turbo for comparison)
# ============================================================================
print("\n🔍 LAYER 6B: LLM API CALL - GPT-3.5-TURBO (for comparison)")
print("─" * 80)

llm_client_35 = LLMClient(model="gpt-3.5-turbo", temperature=0.1, max_tokens=2048)

start = time.time()
response_35 = llm_client_35.generate(prompt, system_message="You are a CFO analyst.")
gpt35_time = time.time() - start

print(f"✅ GPT-3.5-Turbo response: {gpt35_time:.2f}s")
print(f"   Input tokens: ~{context.total_tokens + 100}")
print(f"   Output tokens: {response_35.total_tokens - context.total_tokens}")
print(f"   Cost: ${response_35.cost:.4f}")
print(f"   Speed improvement: {gpt4_time/gpt35_time:.1f}x faster")

# ============================================================================
# LAYER 7: ANSWER FORMATTING
# ============================================================================
print("\n🔍 LAYER 7: ANSWER FORMATTING")
print("─" * 80)

start = time.time()
# Simple formatting (cleaning whitespace, etc.)
formatted_answer = response.text.strip()
format_time = time.time() - start

print(f"✅ Answer formatted: {format_time:.4f}s")
print(f"   Answer length: {len(formatted_answer)} characters")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("PERFORMANCE SUMMARY")
print("=" * 80)

total_gpt4 = load_time + embed_time + search_time + context_time + gpt4_time + format_time
total_gpt35 = load_time + embed_time + search_time + context_time + gpt35_time + format_time

print(f"\n📊 FULL PIPELINE BREAKDOWN (with GPT-4-Turbo):")
print("─" * 80)
print(f"{'Layer':<40} {'Time (s)':<10} {'% of Total':<12}")
print("─" * 80)
print(f"{'1. Embedding Model Loading':<40} {load_time:>8.2f}s {100*load_time/total_gpt4:>10.1f}%")
print(f"{'2. Query Embedding':<40} {embed_time:>8.3f}s {100*embed_time/total_gpt4:>10.1f}%")
print(f"{'3. Database Connection':<40} {conn_time:>8.3f}s {100*conn_time/total_gpt4:>10.1f}%")
print(f"{'4. Vector Search':<40} {search_time:>8.3f}s {100*search_time/total_gpt4:>10.1f}%")
print(f"{'5. Context Building':<40} {context_time:>8.3f}s {100*context_time/total_gpt4:>10.1f}%")
print(f"{'6. GPT-4-Turbo API Call':<40} {gpt4_time:>8.2f}s {100*gpt4_time/total_gpt4:>10.1f}%")
print(f"{'7. Answer Formatting':<40} {format_time:>8.4f}s {100*format_time/total_gpt4:>10.1f}%")
print("─" * 80)
print(f"{'TOTAL TIME':<40} {total_gpt4:>8.2f}s {100.0:>10.1f}%")

print(f"\n📊 ALTERNATIVE CONFIGURATION (with GPT-3.5-Turbo):")
print("─" * 80)
print(f"{'Layer':<40} {'Time (s)':<10} {'% of Total':<12}")
print("─" * 80)
print(f"{'1. Embedding Model Loading (first time)':<40} {load_time:>8.2f}s {100*load_time/total_gpt35:>10.1f}%")
print(f"{'2. Query Embedding':<40} {embed_time:>8.3f}s {100*embed_time/total_gpt35:>10.1f}%")
print(f"{'3. Database Connection':<40} {conn_time:>8.3f}s {100*conn_time/total_gpt35:>10.1f}%")
print(f"{'4. Vector Search':<40} {search_time:>8.3f}s {100*search_time/total_gpt35:>10.1f}%")
print(f"{'5. Context Building':<40} {context_time:>8.3f}s {100*context_time/total_gpt35:>10.1f}%")
print(f"{'6. GPT-3.5-Turbo API Call':<40} {gpt35_time:>8.2f}s {100*gpt35_time/total_gpt35:>10.1f}%")
print(f"{'7. Answer Formatting':<40} {format_time:>8.4f}s {100*format_time/total_gpt35:>10.1f}%")
print("─" * 80)
print(f"{'TOTAL TIME':<40} {total_gpt35:>8.2f}s {100.0:>10.1f}%")

# ============================================================================
# OPTIMIZATION RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 80)
print("OPTIMIZATION OPPORTUNITIES")
print("=" * 80)

print("\n🎯 TARGET: 7-10 seconds per query\n")

# Calculate without model loading (subsequent queries)
subsequent_gpt4 = embed_time + search_time + context_time + gpt4_time + format_time
subsequent_gpt35 = embed_time + search_time + context_time + gpt35_time + format_time

print(f"📊 Current Performance (subsequent queries, model already loaded):")
print(f"   GPT-4-Turbo: {subsequent_gpt4:.2f}s")
print(f"   GPT-3.5-Turbo: {subsequent_gpt35:.2f}s")

print(f"\n⚠️  ANALYSIS:")
if subsequent_gpt4 > 10:
    print(f"   GPT-4-Turbo: {subsequent_gpt4:.1f}s - EXCEEDS TARGET by {subsequent_gpt4-10:.1f}s")
else:
    print(f"   GPT-4-Turbo: {subsequent_gpt4:.1f}s - MEETS TARGET ✅")

if subsequent_gpt35 > 10:
    print(f"   GPT-3.5-Turbo: {subsequent_gpt35:.1f}s - EXCEEDS TARGET by {subsequent_gpt35-10:.1f}s")
else:
    print(f"   GPT-3.5-Turbo: {subsequent_gpt35:.1f}s - MEETS TARGET ✅")

print(f"\n💡 RECOMMENDED OPTIMIZATIONS:")

optimizations = []

if load_time > 1:
    optimizations.append({
        'name': 'Keep model loaded (avoid reinitializing)',
        'time_saved': load_time,
        'how': 'Reuse RAGAgent instance across queries'
    })

if search_time > 1:
    optimizations.append({
        'name': 'Add database index on company + year',
        'time_saved': search_time * 0.3,
        'how': 'Create composite index on (company, year, section)'
    })

if context.total_tokens > 2000:
    optimizations.append({
        'name': 'Use compact format + fewer chunks',
        'time_saved': (context.total_tokens - context_compact.total_tokens) / context.total_tokens * gpt4_time,
        'how': 'format_style="compact", top_k=3'
    })

if gpt4_time > 10:
    optimizations.append({
        'name': 'Switch to GPT-3.5-Turbo',
        'time_saved': gpt4_time - gpt35_time,
        'how': 'model="gpt-3.5-turbo"'
    })

for i, opt in enumerate(optimizations, 1):
    print(f"\n{i}. {opt['name']}")
    print(f"   Time saved: ~{opt['time_saved']:.2f}s")
    print(f"   How: {opt['how']}")

# Calculate best case
best_case = embed_time + search_time*0.7 + context_compact_time + gpt35_time + format_time

print(f"\n" + "─" * 80)
print(f"🚀 BEST CASE SCENARIO (all optimizations applied):")
print(f"   Estimated time: {best_case:.2f}s")
if best_case <= 10:
    print(f"   Result: MEETS 7-10s TARGET ✅")
else:
    print(f"   Result: Still {best_case-10:.1f}s over 10s target")

print("\n" + "=" * 80)

# Cleanup
retriever.close()
print()
