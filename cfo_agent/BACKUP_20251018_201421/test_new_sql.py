"""Test the new quarter_snapshot SQL"""
import asyncio
from db.pool import db_pool

async def test():
    await db_pool.initialize()
    
    # Test the new SQL with JOIN to fact_ratios
    query = """
        SELECT 
            c.ticker, 
            c.name, 
            f.fiscal_year, 
            f.fiscal_quarter,
            f.revenue/1e9 as revenue_b,
            fr.debt_to_equity,
            fr.debt_to_assets,
            fr.rnd_to_revenue,
            fr.sgna_to_revenue
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        LEFT JOIN fact_ratios fr ON fr.company_id = f.company_id 
            AND fr.fiscal_year = f.fiscal_year 
            AND fr.fiscal_quarter = f.fiscal_quarter
        WHERE c.ticker = 'AAPL'
        AND f.fiscal_year = 2023
        AND f.fiscal_quarter = 2
    """
    
    result = await db_pool.execute_query(query)
    
    if result:
        row = result[0]
        print("\n✅ Query works! Results:")
        for key, val in row.items():
            if val is not None:
                print(f"  {key:<30} {val}")
    else:
        print("\n❌ No results")
    
    await db_pool.close()

asyncio.run(test())
