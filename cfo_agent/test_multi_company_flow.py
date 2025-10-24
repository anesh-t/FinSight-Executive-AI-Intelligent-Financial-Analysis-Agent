"""Test multi-company stock query flow"""
import asyncio
from decomposer import QueryDecomposer

async def test_decomposition():
    decomposer = QueryDecomposer()
    
    # Test multi-company stock queries
    queries = [
        "show closing stock price for apple and microsoft for year 2023",
        "show apple, microsoft, google closing price 2023"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = await decomposer.decompose(query)
        
        print(f"\nGreeting: {result.get('greeting', 'None')}")
        print(f"Number of tasks: {len(result.get('tasks', []))}")
        
        for i, task in enumerate(result.get('tasks', [])):
            print(f"\n--- Task {i+1} ---")
            print(f"Intent: {task.get('intent')}")
            print(f"Entities: {task.get('entities')}")
            print(f"Period: {task.get('period')}")

if __name__ == "__main__":
    asyncio.run(test_decomposition())
