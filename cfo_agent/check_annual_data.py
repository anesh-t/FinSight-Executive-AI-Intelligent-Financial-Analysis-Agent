"""Check what data is in mv_financials_annual and mv_ratios_annual"""
import asyncio
from db.pool import db_pool

async def check():
    await db_pool.initialize()
    
    # Get sample row to see columns
    query1 = """
        SELECT *
        FROM mv_financials_annual
        JOIN dim_company USING (company_id)
        WHERE ticker = 'AAPL'
        AND fiscal_year = 2023
        LIMIT 1
    """
    
    result1 = await db_pool.execute_query(query1)
    
    if result1:
        print("\nColumns in mv_financials_annual:")
        for key in sorted(result1[0].keys()):
            print(f"  {key}")
    
    # Check mv_ratios_annual
    query2 = """
        SELECT *
        FROM mv_ratios_annual
        JOIN dim_company USING (company_id)
        WHERE ticker = 'AAPL'
        AND fiscal_year = 2023
        LIMIT 1
    """
    
    result2 = await db_pool.execute_query(query2)
    
    if result2:
        print("\nColumns in mv_ratios_annual:")
        for key in sorted(result2[0].keys()):
            val = result2[0][key]
            if val is not None and isinstance(val, (int, float)):
                print(f"  {key:<50} {val}")
            else:
                print(f"  {key}")
    
    await db_pool.close()

asyncio.run(check())
