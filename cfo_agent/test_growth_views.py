"""
Test if growth views have data
"""
import asyncio
from db.pool import db_pool

async def test_growth_views():
    print("Testing growth views...")
    
    # Test quarterly growth
    print("\n1. Testing vw_growth_quarter:")
    result = await db_pool.execute_query("""
        SELECT * FROM vw_growth_quarter 
        WHERE ticker = 'AAPL' AND fiscal_year = 2023 AND fiscal_quarter = 2 
        LIMIT 1
    """)
    print(f"   Rows: {len(result) if result else 0}")
    if result:
        print(f"   Columns: {list(result[0].keys())}")
        print(f"   Sample: {result[0]}")
    
    # Test annual growth
    print("\n2. Testing vw_growth_annual:")
    result = await db_pool.execute_query("""
        SELECT * FROM vw_growth_annual 
        WHERE ticker = 'AAPL' AND fiscal_year = 2023 
        LIMIT 1
    """)
    print(f"   Rows: {len(result) if result else 0}")
    if result:
        print(f"   Columns: {list(result[0].keys())[:10]}")
    
    # Test peer stats
    print("\n3. Testing vw_peer_stats_quarter:")
    result = await db_pool.execute_query("""
        SELECT * FROM vw_peer_stats_quarter 
        WHERE fiscal_year = 2023 AND fiscal_quarter = 2 
        LIMIT 1
    """)
    print(f"   Rows: {len(result) if result else 0}")
    if result:
        print(f"   Columns: {list(result[0].keys())[:10]}")
    
    # Check if views exist
    print("\n4. Checking if views exist:")
    result = await db_pool.execute_query("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%growth%'
        ORDER BY table_name
    """)
    print(f"   Growth views: {[r['table_name'] for r in result] if result else 'None'}")
    
    result = await db_pool.execute_query("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%peer%'
        ORDER BY table_name
    """)
    print(f"   Peer views: {[r['table_name'] for r in result] if result else 'None'}")

asyncio.run(test_growth_views())
