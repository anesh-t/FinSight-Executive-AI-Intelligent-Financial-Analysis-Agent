"""Check the full response from agent"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def check():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    query = "compare Apple with Google and how CPI affected both companies Q2 2023"
    print(f"Query: {query}\n")
    
    response = await cfo_agent_graph.run(query)
    
    print("="*100)
    print("FULL RESPONSE:")
    print("="*100)
    print(response)
    print("="*100)
    
    # Check for both companies in full response
    has_apple = any(word in response for word in ['AAPL', 'Apple'])
    has_google = any(word in response for word in ['GOOG', 'Google', 'Alphabet'])
    has_cpi = any(word in response for word in ['CPI', 'cpi', 'inflation'])
    
    print(f"\n✅ Apple mentioned: {has_apple}")
    print(f"✅ Google mentioned: {has_google}")
    print(f"✅ CPI mentioned: {has_cpi}")
    
    if has_apple and has_google and has_cpi:
        print("\n🎉 ALL EXPECTED KEYWORDS PRESENT!")
    else:
        print(f"\n⚠️ Missing: Apple={has_apple}, Google={has_google}, CPI={has_cpi}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check())
