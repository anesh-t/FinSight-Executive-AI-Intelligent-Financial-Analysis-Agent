"""Quick test"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    result = await cfo_agent_graph.run("show Apple debt to equity for Q2 2023")
    print(result)
    
    await db_pool.close()

asyncio.run(test())
