"""Test direct query to fact_ratios"""
import asyncio
from db.pool import db_pool

async def test():
    await db_pool.initialize()
    
    # Test the quarterly_ratios template SQL
    query = """
        SELECT 
            c.ticker, 
            c.name, 
            fr.fiscal_year, 
            fr.fiscal_quarter, 
            fr.debt_to_equity, 
            fr.debt_to_assets, 
            fr.rnd_to_revenue, 
            fr.sgna_to_revenue
        FROM fact_ratios fr
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND fr.fiscal_year = 2023
        AND fr.fiscal_quarter = 2
    """
    
    result = await db_pool.execute_query(query)
    
    if result:
        row = result[0]
        print("\nApple Q2 2023 from fact_ratios:")
        print(f"  Debt-to-Equity: {float(row['debt_to_equity']):.2f}")
        print(f"  Debt-to-Assets: {float(row['debt_to_assets']):.2f}")
        print(f"  R&D Intensity: {float(row['rnd_to_revenue'])*100:.1f}%")
        print(f"  SG&A Intensity: {float(row['sgna_to_revenue'])*100:.1f}%")
        print("\n✅ Data is available in fact_ratios!")
        print("❌ Problem: Queries not routing to quarterly_ratios template")
    
    await db_pool.close()

asyncio.run(test())
