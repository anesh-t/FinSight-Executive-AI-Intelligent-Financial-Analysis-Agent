"""Check which ticker Google data is stored under"""
import asyncio
from db.pool import db_pool

async def check():
    await db_pool.initialize()
    
    # Check both GOOG and GOOGL
    for ticker in ['GOOG', 'GOOGL']:
        sql = """
        SELECT c.ticker, c.name, COUNT(*) as count
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = :ticker
        GROUP BY c.ticker, c.name
        """
        result = await db_pool.execute_query(sql, {'ticker': ticker})
        print(f"{ticker}: {result}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check())
