"""Test multi-company + macro query"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    query = "compare Apple with Google and how CPI affected both companies Q2 2023"
    print(f"Query: {query}\n")
    
    response = await cfo_agent_graph.run(query)
    print(f"Response:\n{response[:500]}...")
    
    # Check if both companies are in response
    if 'AAPL' in response and ('GOOG' in response or 'Google' in response or 'Alphabet' in response):
        print("\n✅ Both companies present!")
    elif 'AAPL' in response:
        print("\n❌ Only Apple present")
    else:
        print("\n❌ Unexpected response")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(test())
