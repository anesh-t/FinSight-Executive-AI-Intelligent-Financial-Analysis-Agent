"""Quick test for ratio fixes"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    tests = [
        "show Apple ROE for Q2 2023",
        "show Apple ROA for Q2 2023",
        "show Apple R&D intensity for 2023",
        "show Apple SG&A intensity for 2023",
    ]
    
    for query in tests:
        print(f"\n{'='*100}")
        print(f"Query: {query}")
        print("="*100)
        result = await cfo_agent_graph.run(query)
        print(result)
    
    await db_pool.close()

asyncio.run(test())
