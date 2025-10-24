"""
Debug which template is being used for ratio queries
"""
import asyncio
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def debug_routing():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("DEBUGGING RATIO QUERY ROUTING")
    print("="*100)
    
    # Test direct SQL queries
    print("\n[1] Direct query to quarter_snapshot (fact_financials with calculated ratios):")
    print("-"*100)
    
    q1 = """
        SELECT 
            c.ticker, 
            f.fiscal_year, 
            f.fiscal_quarter,
            f.gross_profit/NULLIF(f.revenue,0) as gross_margin,
            f.operating_income/NULLIF(f.revenue,0) as operating_margin,
            f.net_income/NULLIF(f.revenue,0) as net_margin,
            f.net_income/NULLIF(f.equity,0) as roe,
            f.net_income/NULLIF(f.total_assets,0) as roa
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND f.fiscal_year = 2023
        AND f.fiscal_quarter = 2
    """
    
    r1 = await db_pool.execute_query(q1)
    if r1:
        row = r1[0]
        print(f"Period: Q{row['fiscal_quarter']} {row['fiscal_year']}")
        print(f"  Gross Margin: {float(row['gross_margin'])*100:.2f}%")
        print(f"  Operating Margin: {float(row['operating_margin'])*100:.2f}%")
        print(f"  Net Margin: {float(row['net_margin'])*100:.2f}%")
        print(f"  ROE (quarterly, not TTM): {float(row['roe'])*100:.2f}%")
        print(f"  ROA (quarterly, not TTM): {float(row['roa'])*100:.2f}%")
    
    print("\n[2] Direct query to ttm_snapshot (mv_ratios_ttm):")
    print("-"*100)
    
    q2 = """
        SELECT 
            c.ticker,
            r.fiscal_year,
            r.fiscal_quarter,
            r.gross_margin_ttm,
            r.operating_margin_ttm,
            r.net_margin_ttm,
            r.roe_ttm,
            r.roa_ttm
        FROM mv_ratios_ttm r
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND r.fiscal_year = 2023
        AND r.fiscal_quarter = 2
    """
    
    r2 = await db_pool.execute_query(q2)
    if r2:
        row = r2[0]
        print(f"Period: Q{row['fiscal_quarter']} {row['fiscal_year']} (TTM)")
        print(f"  Gross Margin (TTM): {float(row['gross_margin_ttm'])*100:.2f}%")
        print(f"  Operating Margin (TTM): {float(row['operating_margin_ttm'])*100:.2f}%")
        print(f"  Net Margin (TTM): {float(row['net_margin_ttm'])*100:.2f}%")
        print(f"  ROE (TTM): {float(row['roe_ttm'])*100:.2f}%")
        print(f"  ROA (TTM): {float(row['roa_ttm'])*100:.2f}%")
    
    print("\n[3] Comparison:")
    print("-"*100)
    print("For quarterly ratio queries, we should use:")
    print("  ✅ TTM ratios (mv_ratios_ttm) for ROE, ROA - more meaningful")
    print("  ✅ Quarterly ratios (fact_financials) for margins - already correct")
    print("\nCurrent templates:")
    print("  quarter_snapshot: Uses fact_financials (calculates margins quarterly)")
    print("  ttm_snapshot: Uses mv_ratios_ttm (has all 5 TTM ratios)")
    
    await db_pool.close()

asyncio.run(debug_routing())
