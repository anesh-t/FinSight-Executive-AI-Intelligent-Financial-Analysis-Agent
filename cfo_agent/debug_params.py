"""
Debug parameter binding for multi-company queries
"""
import asyncio
from decomposer import QueryDecomposer
from router import IntentRouter
from planner import TaskPlanner
from db.pool import db_pool
from db.resolve import load_ticker_cache
from db.whitelist import load_schema_cache

async def debug():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    decomposer = QueryDecomposer()
    router = IntentRouter()
    planner = TaskPlanner()
    
    query = "compare Apple with Google and how CPI affected both companies Q2 2023"
    print(f"Query: {query}")
    print("="*80)
    
    # Step 1: Decompose
    decomposed = await decomposer.decompose(query)
    print(f"\n1. Decomposed:")
    print(f"   Tasks: {decomposed.get('tasks')}")
    
    # Step 2: Route
    if decomposed.get('tasks'):
        task = decomposed['tasks'][0]
        routed = router.route_task(task)
        print(f"\n2. Routed:")
        print(f"   Intent: {routed['intent']}")
        print(f"   Template: {routed['template_name']}")
        print(f"   Entities: {routed['entities']}")
        
        # Step 3: Plan
        plan = await planner.plan_task(routed)
        print(f"\n3. Planned:")
        print(f"   SQL: {plan['sql'][:200]}...")
        print(f"   Params: {plan['params']}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(debug())
