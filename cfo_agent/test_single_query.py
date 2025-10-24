"""Test a single query"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    query = "show Google revenue, net income, gross margin Q2 2023"
    print(f"Query: {query}\n")
    
    response = await cfo_agent_graph.run(query)
    print(f"Response:\n{response}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(test())
