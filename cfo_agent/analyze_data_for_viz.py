"""
Analyze data structure and coverage for visualization planning
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def analyze_data_structure():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    print('='*100)
    print('DATA STRUCTURE & COVERAGE ANALYSIS FOR VISUALIZATION')
    print('='*100)
    
    # 1. Annual data coverage
    print('\n1. ANNUAL DATA COVERAGE')
    print('-'*100)
    annual_range = await conn.fetchrow('''
        SELECT 
            MIN(fiscal_year) as min_year,
            MAX(fiscal_year) as max_year,
            COUNT(DISTINCT fiscal_year) as year_count,
            COUNT(DISTINCT company_id) as company_count
        FROM mv_financials_annual
    ''')
    print(f"   Year Range: {annual_range['min_year']} to {annual_range['max_year']}")
    print(f"   Total Years: {annual_range['year_count']}")
    print(f"   Companies: {annual_range['company_count']}")
    
    # 2. Quarterly data coverage
    print('\n2. QUARTERLY DATA COVERAGE')
    print('-'*100)
    quarterly_range = await conn.fetchrow('''
        SELECT 
            MIN(fiscal_year) as min_year,
            MAX(fiscal_year) as max_year,
            COUNT(*) as total_records
        FROM fact_financials
        WHERE fiscal_quarter IS NOT NULL
    ''')
    print(f"   Year Range: {quarterly_range['min_year']} to {quarterly_range['max_year']}")
    print(f"   Total Records: {quarterly_range['total_records']}")
    
    # 3. Sample Apple data - last 10 years
    print('\n3. SAMPLE TREND DATA - APPLE (Last 10 Years)')
    print('-'*100)
    apple_trend = await conn.fetch('''
        SELECT fiscal_year, 
               revenue_annual/1e9 as revenue_b, 
               net_margin_annual*100 as net_margin_pct,
               avg_price_annual as avg_price,
               roe_annual*100 as roe_pct
        FROM mv_company_complete_annual
        WHERE ticker = 'AAPL'
        ORDER BY fiscal_year DESC
        LIMIT 10
    ''')
    print(f"   {'Year':<8} {'Revenue ($B)':<15} {'Net Margin %':<15} {'Avg Price':<15} {'ROE %':<15}")
    print('   ' + '-'*96)
    for row in apple_trend:
        print(f"   {row['fiscal_year']:<8} "
              f"{row['revenue_b']:<15.2f} "
              f"{row['net_margin_pct']:<15.2f} "
              f"{row['avg_price']:<15.2f} "
              f"{row['roe_pct']:<15.2f}")
    
    # 4. Quarterly trend - Apple last 12 quarters
    print('\n4. QUARTERLY TREND DATA - APPLE (Last 12 Quarters)')
    print('-'*100)
    apple_quarterly = await conn.fetch('''
        SELECT fiscal_year, fiscal_quarter,
               revenue/1e9 as revenue_b,
               net_margin*100 as net_margin_pct,
               avg_price
        FROM vw_company_complete_quarter
        WHERE ticker = 'AAPL'
        ORDER BY fiscal_year DESC, fiscal_quarter DESC
        LIMIT 12
    ''')
    print(f"   {'Period':<12} {'Revenue ($B)':<15} {'Net Margin %':<15} {'Avg Price':<15}")
    print('   ' + '-'*96)
    for row in apple_quarterly:
        period = f"{row['fiscal_year']}-Q{row['fiscal_quarter']}"
        print(f"   {period:<12} "
              f"{row['revenue_b']:<15.2f} "
              f"{row['net_margin_pct']:<15.2f} "
              f"{row['avg_price']:<15.2f}")
    
    # 5. Multi-company comparison data
    print('\n5. MULTI-COMPANY COMPARISON DATA - FY2023')
    print('-'*100)
    comparison = await conn.fetch('''
        SELECT ticker, name,
               revenue_annual/1e9 as revenue_b,
               net_margin_annual*100 as net_margin_pct,
               roe_annual*100 as roe_pct,
               avg_price_annual as avg_price
        FROM mv_company_complete_annual
        WHERE fiscal_year = 2023
        ORDER BY revenue_annual DESC
    ''')
    print(f"   {'Ticker':<8} {'Company':<30} {'Revenue ($B)':<15} {'Net Margin %':<15} {'ROE %':<15}")
    print('   ' + '-'*96)
    for row in comparison:
        print(f"   {row['ticker']:<8} "
              f"{row['name'][:28]:<30} "
              f"{row['revenue_b']:<15.2f} "
              f"{row['net_margin_pct']:<15.2f} "
              f"{row['roe_pct']:<15.2f}")
    
    # 6. Available metrics
    print('\n6. AVAILABLE METRICS FOR VISUALIZATION')
    print('-'*100)
    print('   FINANCIALS:')
    print('   - Revenue, Net Income, Operating Income, Gross Profit')
    print('   - EBITDA, COGS, R&D, SG&A')
    print('   - Cash Flows (Operating, Investing, Financing)')
    print('   - CapEx, Dividends, Buybacks')
    
    print('\n   RATIOS:')
    print('   - Margins (Gross, Operating, Net)')
    print('   - Returns (ROE, ROA)')
    print('   - Leverage (Debt-to-Equity, Debt-to-Assets)')
    print('   - Efficiency (R&D Intensity, SG&A Intensity)')
    
    print('\n   STOCK PRICES:')
    print('   - Open, Close, High, Low, Average')
    print('   - Returns (QoQ, YoY, Annual)')
    print('   - Volatility, Volume, Dividend Yield')
    
    print('\n   MACRO INDICATORS:')
    print('   - GDP, CPI, Core CPI, PCE')
    print('   - Unemployment Rate, Fed Funds Rate')
    print('   - S&P 500, VIX, Term Spread')
    
    # 7. Data granularity check
    print('\n7. DATA COMPLETENESS CHECK')
    print('-'*100)
    completeness = await conn.fetchrow('''
        SELECT 
            COUNT(*) as total_records,
            COUNT(revenue_annual) as has_revenue,
            COUNT(net_margin_annual) as has_margin,
            COUNT(avg_price_annual) as has_stock,
            COUNT(roe_annual) as has_roe
        FROM mv_company_complete_annual
        WHERE fiscal_year >= 2019
    ''')
    total = completeness['total_records']
    print(f"   Total Records (2019+): {total}")
    print(f"   Has Revenue: {completeness['has_revenue']} ({completeness['has_revenue']/total*100:.1f}%)")
    print(f"   Has Margin: {completeness['has_margin']} ({completeness['has_margin']/total*100:.1f}%)")
    print(f"   Has Stock: {completeness['has_stock']} ({completeness['has_stock']/total*100:.1f}%)")
    print(f"   Has ROE: {completeness['has_roe']} ({completeness['has_roe']/total*100:.1f}%)")
    
    print('\n' + '='*100)
    print('ANALYSIS COMPLETE')
    print('='*100)
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_data_structure())
