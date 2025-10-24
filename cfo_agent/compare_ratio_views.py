"""
Compare ratios available in mv_ratios_ttm vs mv_ratios_annual
"""
import asyncio
from db.pool import db_pool


async def compare_views():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("RATIO METRICS COMPARISON")
    print("="*100)
    
    # TTM ratios
    ttm_query = """
        SELECT r.*
        FROM mv_ratios_ttm r
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        ORDER BY r.fiscal_year DESC, r.fiscal_quarter DESC
        LIMIT 1
    """
    ttm_data = await db_pool.execute_query(ttm_query)
    
    # Annual ratios
    annual_query = """
        SELECT r.*
        FROM mv_ratios_annual r
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL'
        AND r.fiscal_year = 2023
    """
    annual_data = await db_pool.execute_query(annual_query)
    
    print("\n[1] TTM Ratios (Quarterly-based):")
    print("-"*100)
    if ttm_data:
        ttm = ttm_data[0]
        ttm_ratios = [k for k in ttm.keys() if k not in ['company_id', 'fiscal_year', 'fiscal_quarter', 'has_full_year']]
        for ratio in ttm_ratios:
            val = ttm[ratio]
            if val is not None:
                if 'margin' in ratio or ratio in ['roe_ttm', 'roa_ttm']:
                    print(f"  ✅ {ratio:<40} {float(val)*100:.2f}%")
                else:
                    print(f"  ✅ {ratio:<40} {float(val):.4f}")
    
    print("\n[2] Annual Ratios:")
    print("-"*100)
    if annual_data:
        annual = annual_data[0]
        annual_ratios = [k for k in annual.keys() if k not in ['company_id', 'fiscal_year', 'has_full_year']]
        for ratio in annual_ratios:
            val = annual[ratio]
            if val is not None:
                if 'margin' in ratio or ratio in ['roe_annual_avg_equity', 'roa_annual']:
                    print(f"  ✅ {ratio:<40} {float(val)*100:.2f}%")
                elif 'debt_to' in ratio:
                    print(f"  ✅ {ratio:<40} {float(val):.4f}")
                else:
                    print(f"  ✅ {ratio:<40} {float(val)*100:.2f}%")
    
    # Create mapping table
    print("\n[3] Ratio Mapping (from dim_ratio image):")
    print("-"*100)
    print(f"{'Code':<25} {'Name':<35} {'TTM':<10} {'Annual':<10}")
    print("-"*100)
    
    ratio_map = [
        ('roe', 'Return on Equity (ROE)', 'roe_ttm', 'roe_annual_avg_equity'),
        ('roa', 'Return on Assets (ROA)', 'roa_ttm', 'roa_annual'),
        ('gross_margin', 'Gross Margin', 'gross_margin_ttm', 'gross_margin_annual'),
        ('operating_margin', 'Operating Margin', 'operating_margin_ttm', 'operating_margin_annual'),
        ('net_margin', 'Net Profit Margin', 'net_margin_ttm', 'net_margin_annual'),
        ('debt_to_equity', 'Debt-to-Equity Ratio', '❌', 'debt_to_equity_annual'),
        ('debt_to_assets', 'Debt-to-Assets Ratio', '❌', 'debt_to_assets_annual'),
        ('rnd_to_revenue', 'R&D Intensity', '❌', 'rnd_to_revenue_annual'),
        ('sgna_to_revenue', 'SG&A Intensity', '❌', 'sgna_to_revenue_annual'),
    ]
    
    for code, name, ttm_col, annual_col in ratio_map:
        ttm_avail = "✅" if ttm_col != '❌' else "❌"
        annual_avail = "✅" if annual_col != '❌' else "❌"
        print(f"{code:<25} {name:<35} {ttm_avail:<10} {annual_avail:<10}")
    
    print("\n" + "="*100)
    print("SUMMARY:")
    print("  TTM (Quarterly):  5 ratios (margins + ROE + ROA)")
    print("  Annual:           9 ratios (margins + ROE + ROA + debt + intensity)")
    print("="*100)
    
    await db_pool.close()

asyncio.run(compare_views())
