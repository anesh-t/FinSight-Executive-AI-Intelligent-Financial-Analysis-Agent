"""Quick test for quarterly debt ratios"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    query = "show Apple debt to equity ratio for Q2 2023"
    print(f"\nQuery: {query}\n")
    result = await cfo_agent_graph.run(query)
    print(result)
    
    await db_pool.close()

asyncio.run(test())
