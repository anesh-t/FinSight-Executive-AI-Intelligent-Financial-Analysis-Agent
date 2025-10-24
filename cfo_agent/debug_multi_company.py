"""
Debug multi-company query detection
"""
import asyncio
from decomposer import QueryDecomposer
from db.pool import db_pool
from db.resolve import load_ticker_cache

async def debug():
    await db_pool.initialize()
    await load_ticker_cache()
    
    decomposer = QueryDecomposer()
    
    queries = [
        "show Google and Apple revenue Q2 2023",
        "compare Apple and Google gross margin Q2 2023",
        "compare Apple with Google and how CPI affected both companies Q2 2023",
    ]
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print("-"*80)
        
        result = await decomposer.decompose(query)
        
        print(f"Tasks: {result.get('tasks')}")
        print(f"Intent: {result['tasks'][0]['intent'] if result.get('tasks') else 'NO TASKS'}")
        print(f"Entities: {result['tasks'][0]['entities'] if result.get('tasks') else 'NO ENTITIES'}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(debug())
