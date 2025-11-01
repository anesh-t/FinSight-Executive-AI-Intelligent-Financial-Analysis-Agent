"""
Speed-Optimized Test
Compare before/after optimization
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

print("\n" + "=" * 80)
print("⚡ SPEED OPTIMIZATION TEST")
print("=" * 80)

# Test questions (representative sample)
test_questions = [
    "What are Apple's top 3 risks in 2022?",
    "Compare Apple and Microsoft's cybersecurity risks in 2022",
    "How did Microsoft's supply chain risks evolve from 2019 to 2022?",
    "What strategic priorities did Apple highlight in 2022?",
    "Summarize Apple's management discussion about innovation in 2022",
]

print(f"\nTesting {len(test_questions)} questions...\n")

# ============================================================================
# TEST 1: BASELINE (max_tokens=2048)
# ============================================================================
print("─" * 80)
print("📊 TEST 1: BASELINE (max_tokens=2048)")
print("─" * 80)

agent_baseline = RAGAgent(
    model="gpt-3.5-turbo",
    max_tokens=2048,
    verbose=False
)

baseline_times = []
baseline_costs = []

for i, question in enumerate(test_questions, 1):
    print(f"\n  {i}. {question[:60]}...")
    
    start = time.time()
    result = agent_baseline.query(question, top_k=5)
    elapsed = time.time() - start
    
    baseline_times.append(elapsed)
    baseline_costs.append(result.metadata["cost"])
    
    print(f"     Time: {elapsed:.2f}s, Cost: ${result.metadata['cost']:.4f}")
    time.sleep(0.3)

agent_baseline.close()

baseline_avg = sum(baseline_times) / len(baseline_times)
baseline_total_cost = sum(baseline_costs)

print(f"\n  📈 Baseline Average: {baseline_avg:.2f}s")
print(f"  💰 Baseline Total Cost: ${baseline_total_cost:.4f}")

# ============================================================================
# TEST 2: OPTIMIZED (max_tokens=1500)
# ============================================================================
print("\n" + "─" * 80)
print("⚡ TEST 2: OPTIMIZED (max_tokens=1500)")
print("─" * 80)

agent_optimized = RAGAgent(
    model="gpt-3.5-turbo",
    max_tokens=1500,  # Reduced for speed
    verbose=False
)

optimized_times = []
optimized_costs = []

for i, question in enumerate(test_questions, 1):
    print(f"\n  {i}. {question[:60]}...")
    
    start = time.time()
    result = agent_optimized.query(question, top_k=5)
    elapsed = time.time() - start
    
    optimized_times.append(elapsed)
    optimized_costs.append(result.metadata["cost"])
    
    print(f"     Time: {elapsed:.2f}s, Cost: ${result.metadata['cost']:.4f}")
    time.sleep(0.3)

agent_optimized.close()

optimized_avg = sum(optimized_times) / len(optimized_times)
optimized_total_cost = sum(optimized_costs)

print(f"\n  📈 Optimized Average: {optimized_avg:.2f}s")
print(f"  💰 Optimized Total Cost: ${optimized_total_cost:.4f}")

# ============================================================================
# TEST 3: MAXIMUM SPEED (max_tokens=1200, top_k=3)
# ============================================================================
print("\n" + "─" * 80)
print("🚀 TEST 3: MAXIMUM SPEED (max_tokens=1200, top_k=3)")
print("─" * 80)

agent_max_speed = RAGAgent(
    model="gpt-3.5-turbo",
    max_tokens=1200,  # Even more reduced
    top_k=3,  # Fewer chunks
    verbose=False
)

max_speed_times = []
max_speed_costs = []

for i, question in enumerate(test_questions, 1):
    print(f"\n  {i}. {question[:60]}...")
    
    start = time.time()
    result = agent_max_speed.query(question, top_k=3)
    elapsed = time.time() - start
    
    max_speed_times.append(elapsed)
    max_speed_costs.append(result.metadata["cost"])
    
    print(f"     Time: {elapsed:.2f}s, Cost: ${result.metadata['cost']:.4f}")
    time.sleep(0.3)

agent_max_speed.close()

max_speed_avg = sum(max_speed_times) / len(max_speed_times)
max_speed_total_cost = sum(max_speed_costs)

print(f"\n  📈 Max Speed Average: {max_speed_avg:.2f}s")
print(f"  💰 Max Speed Total Cost: ${max_speed_total_cost:.4f}")

# ============================================================================
# COMPARISON
# ============================================================================
print("\n\n" + "=" * 80)
print("📊 SPEED OPTIMIZATION RESULTS")
print("=" * 80)

print(f"\n{'Configuration':<30} {'Avg Time':<15} {'Improvement':<15} {'Cost'}")
print("─" * 80)

print(f"{'Baseline (2048 tokens)':<30} {baseline_avg:>7.2f}s      {'Baseline':<15} ${baseline_total_cost:.4f}")

optimized_improvement = ((baseline_avg - optimized_avg) / baseline_avg) * 100
print(f"{'Optimized (1500 tokens)':<30} {optimized_avg:>7.2f}s      {optimized_improvement:>6.1f}% faster  ${optimized_total_cost:.4f}")

max_speed_improvement = ((baseline_avg - max_speed_avg) / baseline_avg) * 100
print(f"{'Max Speed (1200, k=3)':<30} {max_speed_avg:>7.2f}s      {max_speed_improvement:>6.1f}% faster  ${max_speed_total_cost:.4f}")

print("─" * 80)

# Recommendations
print("\n💡 RECOMMENDATIONS:")

if optimized_avg <= 5:
    print(f"   ✅ OPTIMIZED config achieves {optimized_avg:.1f}s - EXCELLENT!")
    print(f"   → Use: max_tokens=1500, top_k=5")
elif max_speed_avg <= 5:
    print(f"   ✅ MAX SPEED config achieves {max_speed_avg:.1f}s - EXCELLENT!")
    print(f"   → Use: max_tokens=1200, top_k=3")
else:
    print(f"   ⚠️  Even with optimization, avg time is {optimized_avg:.1f}s")
    print(f"   → Consider: Reduce tokens further or optimize prompts")

print(f"\n🎯 BEST CONFIGURATION:")
if optimized_avg <= 6 and optimized_avg <= max_speed_avg + 1:
    print(f"   model='gpt-3.5-turbo'")
    print(f"   max_tokens=1500")
    print(f"   top_k=5")
    print(f"   → Balanced: {optimized_avg:.1f}s avg, good quality")
else:
    print(f"   model='gpt-3.5-turbo'")
    print(f"   max_tokens=1200")
    print(f"   top_k=3")
    print(f"   → Fastest: {max_speed_avg:.1f}s avg, acceptable quality")

print("\n" + "=" * 80)
print()
