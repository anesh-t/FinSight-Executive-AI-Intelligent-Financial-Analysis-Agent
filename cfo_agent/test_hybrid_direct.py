"""
Direct test of hybrid orchestrator (bypassing API)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from master_agent.core.orchestrator import MasterOrchestrator
import asyncio

print("="*100)
print("🧪 DIRECT HYBRID ORCHESTRATOR TEST")
print("="*100)
print()

# Test queries
test_queries = [
    "Show me Apple revenue for 2022 and explain what drove it from their 10-K",
    "What drove Apple's margin changes in 2022? Show me the numbers and business context.",
]

async def test_query(orchestrator, question, test_num):
    print(f"\n{'='*100}")
    print(f"TEST {test_num}: {question[:80]}...")
    print(f"{'='*100}\n")
    
    try:
        result = await orchestrator.query_async(question, session_id=f"test_{test_num}")
        
        print(f"✅ SUCCESS")
        print(f"   Intent: {result.intent}")
        print(f"   Agents: {', '.join(result.agents_used)}")
        print(f"   Success: {result.success}")
        print(f"   Latency: {result.total_latency:.2f}s")
        print(f"\n💬 RESPONSE:")
        print("─" * 100)
        print(result.text[:500] + "..." if len(result.text) > 500 else result.text)
        print("─" * 100)
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    orchestrator = MasterOrchestrator(verbose=False, use_quick_mode=True)
    
    results = []
    for i, question in enumerate(test_queries, 1):
        success = await test_query(orchestrator, question, i)
        results.append(success)
        
        if i < len(test_queries):
            print(f"\n⏳ Waiting 2 seconds...")
            await asyncio.sleep(2)
    
    orchestrator.close()
    
    print(f"\n\n{'='*100}")
    print(f"📊 SUMMARY: {sum(results)}/{len(results)} queries succeeded")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    asyncio.run(main())
