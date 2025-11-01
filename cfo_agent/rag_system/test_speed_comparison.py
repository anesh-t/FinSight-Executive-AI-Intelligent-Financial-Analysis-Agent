"""
Speed Comparison Test
Test different model configurations to see speed vs quality trade-offs
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / '3_generation'))
from rag_agent import RAGAgent

print("\n" + "=" * 80)
print("SPEED OPTIMIZATION TEST")
print("=" * 80 + "\n")

# Test query
query = "What are Apple's main cybersecurity risks?"

# Test configurations
configs = [
    {
        "name": "GPT-4 (Original)",
        "model": "gpt-4",
        "top_k": 5,
        "format": "detailed"
    },
    {
        "name": "GPT-4-Turbo (2x Faster)",
        "model": "gpt-4-turbo-preview",
        "top_k": 5,
        "format": "detailed"
    },
    {
        "name": "GPT-4-Turbo + Compact (2.5x Faster)",
        "model": "gpt-4-turbo-preview",
        "top_k": 4,
        "format": "compact"
    },
    {
        "name": "GPT-3.5-Turbo (5x Faster)",
        "model": "gpt-3.5-turbo",
        "top_k": 4,
        "format": "compact"
    }
]

results = []

for i, config in enumerate(configs, 1):
    print(f"\n{'#' * 80}")
    print(f"TEST {i}/{len(configs)}: {config['name']}")
    print(f"{'#' * 80}")
    print(f"Model: {config['model']}")
    print(f"Chunks: {config['top_k']}")
    print(f"Format: {config['format']}")
    print()
    
    try:
        # Initialize agent
        start = time.time()
        agent = RAGAgent(model=config['model'], verbose=False)
        init_time = time.time() - start
        
        # Run query
        query_start = time.time()
        result = agent.query(
            query, 
            top_k=config['top_k'],
            format_style=config['format']
        )
        query_time = time.time() - query_start
        
        agent.close()
        
        # Show preview
        print("ANSWER PREVIEW:")
        print("-" * 80)
        preview = result.text[:300] + "..." if len(result.text) > 300 else result.text
        print(preview)
        print()
        
        print("PERFORMANCE:")
        print(f"  ⏱️  Init time: {init_time:.1f}s")
        print(f"  ⏱️  Query time: {query_time:.1f}s")
        print(f"  ⏱️  Total time: {init_time + query_time:.1f}s")
        print(f"  💰 Cost: ${result.metadata['cost']:.4f}")
        print(f"  📊 Tokens: {result.metadata['tokens']}")
        print(f"  📝 Answer length: {len(result.text)} chars")
        
        results.append({
            'config': config['name'],
            'init_time': init_time,
            'query_time': query_time,
            'total_time': init_time + query_time,
            'cost': result.metadata['cost'],
            'tokens': result.metadata['tokens'],
            'answer_length': len(result.text)
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        results.append({
            'config': config['name'],
            'error': str(e)
        })

# Summary
print("\n" + "=" * 80)
print("SPEED COMPARISON SUMMARY")
print("=" * 80)

if len([r for r in results if 'error' not in r]) > 0:
    print("\n{:<40} {:>10} {:>10} {:>10}".format(
        "Configuration", "Time (s)", "Cost ($)", "Speed"
    ))
    print("-" * 80)
    
    baseline_time = None
    for r in results:
        if 'error' in r:
            continue
            
        if baseline_time is None:
            baseline_time = r['total_time']
            speedup = "1.0x"
        else:
            speedup = f"{baseline_time / r['total_time']:.1f}x"
        
        print("{:<40} {:>10.1f} {:>10.4f} {:>10}".format(
            r['config'],
            r['total_time'],
            r['cost'],
            speedup
        ))
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    
    # Find fastest with good quality
    gpt4_turbo = [r for r in results if 'GPT-4-Turbo' in r['config'] and 'error' not in r]
    if gpt4_turbo:
        best = min(gpt4_turbo, key=lambda x: x['total_time'])
        print(f"\n✅ RECOMMENDED: {best['config']}")
        print(f"   ⏱️  {best['total_time']:.1f}s per query")
        print(f"   💰 ${best['cost']:.4f} per query")
        print(f"   📊 Best balance of speed, cost, and quality")
    
    print()

print()
