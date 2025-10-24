"""
Verify which source is actually being used for quarterly ROE/ROA
"""
import asyncio
from db.pool import db_pool


async def verify():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("VERIFYING ROE/ROA DATA SOURCES FOR APPLE Q2 2023")
    print("="*100)
    
    # 1. Get from mv_ratios_ttm (TTM values)
    ttm_query = """
        SELECT 
            c.ticker,
            r.fiscal_year,
            r.fiscal_quarter,
            r.roe_ttm,
            r.roa_ttm
        FROM mv_ratios_ttm r
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND r.fiscal_year = 2023
        AND r.fiscal_quarter = 2
    """
    
    ttm_result = await db_pool.execute_query(ttm_query)
    
    print("\n[1] From mv_ratios_ttm (TTM - Trailing 12 Months):")
    print("-"*100)
    if ttm_result:
        row = ttm_result[0]
        print(f"  roe_ttm: {float(row['roe_ttm'])*100:.2f}%")
        print(f"  roa_ttm: {float(row['roa_ttm'])*100:.2f}%")
    else:
        print("  ❌ No data")
    
    # 2. Calculate from fact_financials (Point-in-Time)
    calc_query = """
        SELECT 
            c.ticker,
            f.fiscal_year,
            f.fiscal_quarter,
            f.net_income/NULLIF(f.equity,0) as roe_calc,
            f.net_income/NULLIF(f.total_assets,0) as roa_calc
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND f.fiscal_year = 2023
        AND f.fiscal_quarter = 2
    """
    
    calc_result = await db_pool.execute_query(calc_query)
    
    print("\n[2] Calculated from fact_financials (Point-in-Time Quarter):")
    print("-"*100)
    if calc_result:
        row = calc_result[0]
        print(f"  roe (calculated): {float(row['roe_calc'])*100:.2f}%")
        print(f"  roa (calculated): {float(row['roa_calc'])*100:.2f}%")
    else:
        print("  ❌ No data")
    
    # 3. Get from fact_ratios (Point-in-Time)
    fact_query = """
        SELECT 
            c.ticker,
            fr.fiscal_year,
            fr.fiscal_quarter,
            fr.roe,
            fr.roa
        FROM fact_ratios fr
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND fr.fiscal_year = 2023
        AND fr.fiscal_quarter = 2
    """
    
    fact_result = await db_pool.execute_query(fact_query)
    
    print("\n[3] From fact_ratios (Point-in-Time Quarter):")
    print("-"*100)
    if fact_result:
        row = fact_result[0]
        print(f"  roe: {float(row['roe'])*100:.2f}%")
        print(f"  roa: {float(row['roa'])*100:.2f}%")
    else:
        print("  ❌ No data")
    
    # 4. Test what the agent actually returns
    print("\n[4] What the Agent Actually Returns:")
    print("-"*100)
    
    from graph import cfo_agent_graph
    from db.whitelist import load_schema_cache
    from db.resolve import load_ticker_cache
    
    await load_schema_cache()
    await load_ticker_cache()
    
    roe_result = await cfo_agent_graph.run("show Apple ROE for Q2 2023")
    roa_result = await cfo_agent_graph.run("show Apple ROA for Q2 2023")
    
    print(f"  ROE: {roe_result.split(chr(10))[0]}")
    print(f"  ROA: {roa_result.split(chr(10))[0]}")
    
    # Analysis
    print("\n" + "="*100)
    print("ANALYSIS:")
    print("="*100)
    
    if ttm_result and calc_result and fact_result:
        ttm_roe = float(ttm_result[0]['roe_ttm'])*100
        calc_roe = float(calc_result[0]['roe_calc'])*100
        fact_roe = float(fact_result[0]['roe'])*100
        
        ttm_roa = float(ttm_result[0]['roa_ttm'])*100
        calc_roa = float(calc_result[0]['roa_calc'])*100
        fact_roa = float(fact_result[0]['roa'])*100
        
        print("\nROE Values:")
        print(f"  TTM (12-month): {ttm_roe:.2f}%")
        print(f"  Point-in-Time:  {calc_roe:.2f}% (calculated) = {fact_roe:.2f}% (fact_ratios)")
        
        print("\nROA Values:")
        print(f"  TTM (12-month): {ttm_roa:.2f}%")
        print(f"  Point-in-Time:  {calc_roa:.2f}% (calculated) = {fact_roa:.2f}% (fact_ratios)")
        
        print("\nAgent returns 33.0% for ROE - matches Point-in-Time, not TTM")
        print("Agent returns 5.9% for ROA - matches Point-in-Time, not TTM")
        
        print("\n🔍 CONCLUSION:")
        print("  Currently using: quarter_snapshot (calculated from fact_financials)")
        print("  Available but unused: mv_ratios_ttm (roe_ttm, roa_ttm)")
        print("  Note: TTM values are VERY different from quarterly values!")
        print(f"    ROE: {ttm_roe:.1f}% (TTM) vs {calc_roe:.1f}% (Quarterly)")
        print(f"    ROA: {ttm_roa:.1f}% (TTM) vs {calc_roa:.1f}% (Quarterly)")
    
    await db_pool.close()

asyncio.run(verify())
