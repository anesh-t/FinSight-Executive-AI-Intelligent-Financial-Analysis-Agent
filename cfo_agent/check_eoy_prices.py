"""Check EOY closing prices vs averages"""
import asyncio
from db.pool import db_pool

async def check_prices():
    await db_pool.initialize()
    
    query = """
    SELECT c.ticker, c.name, sa.fiscal_year,
           sa.avg_close_price_annual,
           sa.close_price_eoy
    FROM mv_stock_prices_annual sa
    JOIN dim_company c USING (company_id)
    WHERE c.ticker IN ('AAPL', 'MSFT') AND sa.fiscal_year = 2023
    ORDER BY c.ticker
    """
    
    results = await db_pool.execute_query(query)
    
    print("Closing Prices for 2023:")
    print("=" * 80)
    for row in results:
        print(f"\n{row['name']} ({row['ticker']}):")
        print(f"  Average closing price (yearly avg): ${float(row['avg_close_price_annual']):.2f}")
        print(f"  EOY closing price (Dec 31):          ${float(row['close_price_eoy']):.2f}")
        diff = float(row['close_price_eoy']) - float(row['avg_close_price_annual'])
        print(f"  Difference: ${diff:.2f}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(check_prices())
