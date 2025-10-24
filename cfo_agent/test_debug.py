"""
Debug query execution step by step
"""
import asyncio
import json
from db.pool import db_pool

async def test_query_manually():
    """Manually test the query flow"""
    await db_pool.initialize()
    
    print("="*70)
    print("MANUAL QUERY TEST")
    print("="*70)
    
    # Test the SQL directly with parameters
    sql = """
    SELECT c.ticker, c.name, f.fiscal_year, f.revenue_annual/1e9 as revenue_b, 
           f.net_income_annual/1e9 as net_income_b, f.operating_income_annual/1e9 as op_income_b, 
           r.gross_margin_annual, r.operating_margin_annual, r.net_margin_annual, r.roe_annual_avg_equity 
    FROM mv_financials_annual f 
    JOIN mv_ratios_annual r USING (company_id, fiscal_year) 
    JOIN dim_company c USING (company_id) 
    WHERE c.ticker = :ticker AND (CAST(:fy AS INTEGER) IS NULL OR f.fiscal_year = :fy) 
    ORDER BY f.fiscal_year DESC 
    LIMIT :limit
    """
    
    # Test 1: With year specified
    print("\nTest 1: AAPL with fy=2019")
    print("-"*70)
    params1 = {"ticker": "AAPL", "fy": 2019, "limit": 1}
    print(f"Params: {params1}")
    
    try:
        result1 = await db_pool.execute_query(sql, params1)
        print(f"✅ Found {len(result1)} rows")
        if result1:
            row = result1[0]
            print(f"   {row['ticker']} FY{row['fiscal_year']}: ${row['revenue_b']:.2f}B revenue")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: With fy=NULL (latest)
    print("\nTest 2: AAPL with fy=null (latest)")
    print("-"*70)
    params2 = {"ticker": "AAPL", "fy": None, "limit": 1}
    print(f"Params: {params2}")
    
    try:
        result2 = await db_pool.execute_query(sql, params2)
        print(f"✅ Found {len(result2)} rows")
        if result2:
            row = result2[0]
            print(f"   {row['ticker']} FY{row['fiscal_year']}: ${row['revenue_b']:.2f}B revenue")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Quarterly query
    print("\nTest 3: AAPL Q2 2019 (quarterly)")
    print("-"*70)
    sql_quarterly = """
    SELECT c.ticker, c.name, q.fiscal_year, q.fiscal_quarter, q.revenue/1e9 as revenue_b, 
           q.net_income/1e9 as net_income_b, q.gross_margin, q.operating_margin, q.net_margin, q.roe 
    FROM vw_company_quarter q 
    JOIN dim_company c USING (company_id) 
    WHERE c.ticker = :ticker AND (CAST(:fy AS INTEGER) IS NULL OR q.fiscal_year = :fy) AND (CAST(:fq AS INTEGER) IS NULL OR q.fiscal_quarter = :fq) 
    ORDER BY q.fiscal_year DESC, q.fiscal_quarter DESC 
    LIMIT :limit
    """
    
    params3 = {"ticker": "AAPL", "fy": 2019, "fq": 2, "limit": 4}
    print(f"Params: {params3}")
    
    try:
        result3 = await db_pool.execute_query(sql_quarterly, params3)
        print(f"✅ Found {len(result3)} rows")
        for row in result3:
            print(f"   {row['ticker']} Q{row['fiscal_quarter']} FY{row['fiscal_year']}: ${row['revenue_b']:.2f}B revenue")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await db_pool.close()
    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(test_query_manually())
