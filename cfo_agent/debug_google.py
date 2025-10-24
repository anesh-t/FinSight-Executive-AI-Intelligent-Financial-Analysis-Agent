"""
Debug Google queries
"""
import asyncio
from decomposer import QueryDecomposer
from db.pool import db_pool
from db.resolve import load_ticker_cache

async def debug():
    await db_pool.initialize()
    await load_ticker_cache()
    
    decomposer = QueryDecomposer()
    
    query = "show Google revenue, net income, gross margin Q2 2023"
    print(f"Query: {query}")
    
    result = await decomposer.decompose(query)
    
    print(f"\nDecomposed result:")
    print(f"  Tasks: {result.get('tasks')}")
    if result.get('tasks'):
        print(f"  Intent: {result['tasks'][0]['intent']}")
        print(f"  Entities: {result['tasks'][0]['entities']}")
        print(f"  Period: {result['tasks'][0]['period']}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(debug())
