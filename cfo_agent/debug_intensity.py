"""Debug intensity queries"""
import asyncio
from db.pool import db_pool

async def debug():
    await db_pool.initialize()
    
    # Check if intensity columns are in the annual query
    query = """
        SELECT 
            c.ticker,
            mv.fiscal_year,
            mv.r_and_d_expenses_annual/1e9 as rd_annual_b,
            mv.sg_and_a_expenses_annual/1e9 as sga_annual_b,
            r.rnd_to_revenue_annual,
            r.sgna_to_revenue_annual
        FROM mv_financials_annual mv
        JOIN mv_ratios_annual r USING (company_id, fiscal_year)
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND mv.fiscal_year = 2023
    """
    
    result = await db_pool.execute_query(query)
    
    if result:
        row = result[0]
        print("\nApple 2023 - R&D and SG&A Data:")
        print(f"  R&D Expenses: ${float(row['rd_annual_b']):.2f}B")
        print(f"  R&D Intensity: {float(row['rnd_to_revenue_annual'])*100:.2f}%")
        print(f"  SG&A Expenses: ${float(row['sga_annual_b']):.2f}B")
        print(f"  SG&A Intensity: {float(row['sgna_to_revenue_annual'])*100:.2f}%")
        print(f"\nColumns in result: {list(row.keys())}")
    
    await db_pool.close()

asyncio.run(debug())
