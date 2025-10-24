"""Check what columns exist in stock price data"""
import asyncio
from db.pool import db_pool

async def check_columns():
    await db_pool.initialize()
    
    # Query stock price data for Apple 2023
    query = """
    SELECT *
    FROM mv_stock_prices_annual sa
    JOIN dim_company c USING (company_id)
    WHERE c.ticker = 'AAPL' AND sa.fiscal_year = 2023
    LIMIT 1
    """
    
    result = await db_pool.execute_one(query)
    
    if result:
        print("Available columns:")
        for key in result.keys():
            print(f"  - {key}: {result[key]}")
    else:
        print("No data found!")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check_columns())
