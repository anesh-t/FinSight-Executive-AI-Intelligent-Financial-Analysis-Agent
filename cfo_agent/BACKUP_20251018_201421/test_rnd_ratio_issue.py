"""Test the R&D to revenue ratio query"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    queries = [
        "show amazon r and d to revenue ratio for amazon 2023",
        "show Amazon R&D intensity for 2023",
        "show AMZN R&D to revenue for 2023",
    ]
    
    print("\n" + "="*100)
    print("TESTING R&D TO REVENUE RATIO QUERIES")
    print("="*100)
    
    for query in queries:
        print(f"\n\nQuery: '{query}'")
        print("-"*100)
        result = await cfo_agent_graph.run(query)
        print(f"Result:\n{result}")
    
    await db_pool.close()

asyncio.run(test())
