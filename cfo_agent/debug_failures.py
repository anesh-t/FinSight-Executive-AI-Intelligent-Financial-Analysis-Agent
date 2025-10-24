"""
Debug failing queries
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def debug():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    queries = [
        "compare Apple with Google and how CPI affected both companies Q2 2023",
        "show Apple vs Google with inflation Q2 2023", 
        "show Google revenue, net income, gross margin Q2 2023",
    ]
    
    for query in queries:
        print(f"\n{'='*100}")
        print(f"Query: {query}")
        print("-"*100)
        
        try:
            response = await cfo_agent_graph.run(query)
            print(f"Response: {response[:300]}...")
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(debug())
