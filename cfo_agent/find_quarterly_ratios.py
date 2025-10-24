"""
Find where quarterly ratio data comes from
"""
import asyncio
from db.pool import db_pool


async def find_quarterly_ratios():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("SEARCHING FOR QUARTERLY RATIO DATA")
    print("="*100)
    
    # Check all views/tables with 'ratio' in name
    query = """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND (table_name LIKE '%ratio%' OR table_name LIKE '%margin%')
        ORDER BY table_name
    """
    
    tables = await db_pool.execute_query(query)
    
    print("\nTables/Views with 'ratio' or 'margin':")
    for t in tables:
        print(f"  - {t['table_name']} ({t['table_type']})")
    
    # Check if we can calculate ratios from fact_financials
    print("\n" + "="*100)
    print("QUARTERLY RATIOS FROM fact_financials (calculated on-the-fly)")
    print("="*100)
    
    calc_query = """
        SELECT 
            c.ticker,
            f.fiscal_year,
            f.fiscal_quarter,
            -- Margins (already calculated in quarter_snapshot)
            f.gross_profit/NULLIF(f.revenue,0) as gross_margin,
            f.operating_income/NULLIF(f.revenue,0) as operating_margin,
            f.net_income/NULLIF(f.revenue,0) as net_margin,
            -- Return ratios (need to calculate)
            f.net_income/NULLIF(f.equity,0) as roe,
            f.net_income/NULLIF(f.total_assets,0) as roa,
            -- Debt ratios
            f.total_liabilities/NULLIF(f.total_assets,0) as debt_to_assets,
            f.total_liabilities/NULLIF(f.equity,0) as debt_to_equity,
            -- Intensity ratios
            f.r_and_d_expenses/NULLIF(f.revenue,0) as rnd_to_revenue,
            f.sg_and_a_expenses/NULLIF(f.revenue,0) as sgna_to_revenue
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND f.fiscal_year = 2023
        AND f.fiscal_quarter = 2
    """
    
    result = await db_pool.execute_query(calc_query)
    
    if result:
        print("\nApple Q2 2023 Ratios (calculated from fact_financials):")
        row = result[0]
        print(f"  Ticker: {row['ticker']}")
        print(f"  Period: Q{row['fiscal_quarter']} {row['fiscal_year']}")
        print(f"\n  Margins:")
        print(f"    Gross Margin:      {float(row['gross_margin'])*100:.2f}%" if row['gross_margin'] else "    Gross Margin: N/A")
        print(f"    Operating Margin:  {float(row['operating_margin'])*100:.2f}%" if row['operating_margin'] else "    Operating Margin: N/A")
        print(f"    Net Margin:        {float(row['net_margin'])*100:.2f}%" if row['net_margin'] else "    Net Margin: N/A")
        print(f"\n  Return Ratios:")
        print(f"    ROE:               {float(row['roe'])*100:.2f}%" if row['roe'] else "    ROE: N/A")
        print(f"    ROA:               {float(row['roa'])*100:.2f}%" if row['roa'] else "    ROA: N/A")
        print(f"\n  Debt Ratios:")
        print(f"    Debt-to-Assets:    {float(row['debt_to_assets'])*100:.2f}%" if row['debt_to_assets'] else "    Debt-to-Assets: N/A")
        print(f"    Debt-to-Equity:    {float(row['debt_to_equity']):.2f}x" if row['debt_to_equity'] else "    Debt-to-Equity: N/A")
        print(f"\n  Intensity Ratios:")
        print(f"    R&D Intensity:     {float(row['rnd_to_revenue'])*100:.2f}%" if row['rnd_to_revenue'] else "    R&D Intensity: N/A")
        print(f"    SG&A Intensity:    {float(row['sgna_to_revenue'])*100:.2f}%" if row['sgna_to_revenue'] else "    SG&A Intensity: N/A")
    
    print("\n" + "="*100)
    print("CONCLUSION:")
    print("  - For QUARTERLY ratios: Calculate on-the-fly from fact_financials")
    print("  - For ANNUAL ratios: Use mv_ratios_annual (pre-calculated)")
    print("="*100)
    
    await db_pool.close()

asyncio.run(find_quarterly_ratios())
