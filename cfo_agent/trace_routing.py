"""
Trace which template the agent selects for debt/intensity queries
"""
import asyncio
import json
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def trace_routing():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("TRACING TEMPLATE SELECTION FOR QUARTERLY DEBT/INTENSITY QUERIES")
    print("="*120)
    
    # Test queries that are failing
    test_queries = [
        "show Apple debt to equity ratio for Q2 2023",
        "show Apple R&D intensity for Q2 2023",
    ]
    
    for query in test_queries:
        print(f"\n{'='*120}")
        print(f"Query: {query}")
        print("="*120)
        
        # We need to intercept the execution to see which template was selected
        # Let's manually run through the decomposer
        
        from decomposer import QueryDecomposer
        from catalog.loader import TemplateCatalog
        
        catalog = TemplateCatalog()
        decomposer = QueryDecomposer(catalog)
        
        # Decompose the query
        plan = await decomposer.decompose(query)
        
        print(f"\n📋 Execution Plan:")
        print(f"  Number of steps: {len(plan)}")
        
        for i, step in enumerate(plan, 1):
            print(f"\n  Step {i}:")
            print(f"    Intent: {step.get('intent', 'unknown')}")
            print(f"    Template: {step.get('template_name', 'unknown')}")
            print(f"    Params: {json.dumps(step.get('params', {}), indent=6)}")
            print(f"    SQL: {step.get('sql', 'N/A')[:150]}...")
        
        # Also run the full query to see output
        print(f"\n🤖 Agent Output:")
        result = await cfo_agent_graph.run(query)
        print(f"  {result.split(chr(10))[0]}")
    
    print("\n" + "="*120)
    print("DIAGNOSIS:")
    print("="*120)
    print("\nThe decomposer is likely selecting 'quarter_snapshot' instead of 'quarterly_ratios'")
    print("because the template descriptions don't emphasize debt/intensity keywords enough.")
    print("\nSolution: Enhance template descriptions or add keyword matching in decomposer.")
    
    await db_pool.close()

asyncio.run(trace_routing())
