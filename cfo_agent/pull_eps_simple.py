"""
Pull EPS data separately from quarterly and annual views
"""
import asyncio
from db.pool import db_pool


async def pull_eps_data():
    """Pull quarterly and annual EPS separately"""
    
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("QUARTERLY EPS DATA (from fact_financials)")
    print("="*100)
    
    # Pull quarterly data
    quarterly_query = """
        SELECT 
            c.ticker,
            c.name,
            f.fiscal_year,
            f.fiscal_quarter,
            f.eps
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker IN ('AAPL', 'MSFT', 'GOOG', 'AMZN', 'META')
        AND f.eps IS NOT NULL
        ORDER BY c.ticker, f.fiscal_year, f.fiscal_quarter
    """
    
    quarterly_results = await db_pool.execute_query(quarterly_query)
    
    # Display quarterly data by company
    current_ticker = None
    for row in quarterly_results:
        if row['ticker'] != current_ticker:
            current_ticker = row['ticker']
            print(f"\n{row['name']} ({row['ticker']}):")
            print("-"*100)
            print(f"{'Year':<8} {'Quarter':<10} {'EPS':<10}")
            print("-"*100)
        
        print(f"{row['fiscal_year']:<8} Q{row['fiscal_quarter']:<9} ${row['eps']:.2f}")
    
    print(f"\nTotal Quarterly Records: {len(quarterly_results)}")
    
    # Pull annual data
    print("\n\n" + "="*100)
    print("ANNUAL EPS DATA (aggregated from fact_financials)")
    print("="*100)
    
    annual_query = """
        SELECT 
            c.ticker,
            c.name,
            f.fiscal_year,
            AVG(f.eps) as avg_eps,
            SUM(f.eps) as sum_eps,
            COUNT(*) as quarter_count
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker IN ('AAPL', 'MSFT', 'GOOG', 'AMZN', 'META')
        AND f.eps IS NOT NULL
        GROUP BY c.ticker, c.name, f.fiscal_year
        ORDER BY c.ticker, f.fiscal_year
    """
    
    annual_results = await db_pool.execute_query(annual_query)
    
    # Display annual data by company
    current_ticker = None
    for row in annual_results:
        if row['ticker'] != current_ticker:
            current_ticker = row['ticker']
            print(f"\n{row['name']} ({row['ticker']}):")
            print("-"*100)
            print(f"{'Year':<8} {'Avg EPS':<12} {'Sum EPS':<12} {'Quarters':<10}")
            print("-"*100)
        
        print(f"{row['fiscal_year']:<8} ${row['avg_eps']:.2f}{' '*6} ${row['sum_eps']:.2f}{' '*6} {row['quarter_count']}")
    
    print(f"\nTotal Annual Records: {len(annual_results)}")
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(pull_eps_data())
