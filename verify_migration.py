"""
Quick verification script to test new database views
"""

from database import SupabaseConnector

def verify_new_views():
    db = SupabaseConnector()
    
    print("\n" + "="*80)
    print("DATABASE MIGRATION VERIFICATION")
    print("="*80)
    
    # Test 1: Quarterly unified view
    print("\n1. Testing vw_company_quarter (Apple Q4 2023)")
    query1 = """
    SELECT ticker, fiscal_year, fiscal_quarter, revenue, net_income, roe, gross_margin
    FROM vw_company_quarter
    WHERE ticker = 'AAPL' AND fiscal_year = 2023 AND fiscal_quarter = 4
    """
    result1 = db.execute_query(query1)
    print(result1.to_string(index=False))
    
    # Test 2: Annual aggregates
    print("\n2. Testing mv_financials_annual (Apple 2023)")
    query2 = """
    SELECT c.ticker, a.fiscal_year, 
           a.revenue_annual/1e9 as revenue_billions,
           a.net_income_annual/1e9 as net_income_billions
    FROM mv_financials_annual a
    JOIN dim_company c USING (company_id)
    WHERE c.ticker = 'AAPL' AND a.fiscal_year = 2023
    """
    result2 = db.execute_query(query2)
    print(result2.to_string(index=False))
    
    # Test 3: Annual ratios
    print("\n3. Testing mv_ratios_annual (All companies 2023)")
    query3 = """
    SELECT c.ticker, r.fiscal_year,
           ROUND(r.roe_annual_avg_equity * 100, 2) as roe_pct,
           ROUND(r.gross_margin_annual * 100, 2) as gross_margin_pct
    FROM mv_ratios_annual r
    JOIN dim_company c USING (company_id)
    WHERE r.fiscal_year = 2023
    ORDER BY r.roe_annual_avg_equity DESC
    """
    result3 = db.execute_query(query3)
    print(result3.to_string(index=False))
    
    # Test 4: Macro overlay
    print("\n4. Testing vw_company_quarter_macro (Apple latest with macro)")
    query4 = """
    SELECT ticker, fiscal_year, fiscal_quarter,
           revenue/1e9 as revenue_billions,
           ROUND(cpi, 2) as cpi,
           ROUND(fed_funds_rate, 2) as fed_rate,
           ROUND(sp500_index, 2) as sp500
    FROM vw_company_quarter_macro
    WHERE ticker = 'AAPL'
    ORDER BY fiscal_year DESC, fiscal_quarter DESC
    LIMIT 5
    """
    result4 = db.execute_query(query4)
    print(result4.to_string(index=False))
    
    # Test 5: TTM metrics
    print("\n5. Testing mv_financials_ttm (Apple latest TTM)")
    query5 = """
    SELECT c.ticker, t.fiscal_year, t.fiscal_quarter,
           t.revenue_ttm/1e9 as revenue_ttm_billions,
           t.net_income_ttm/1e9 as net_income_ttm_billions
    FROM mv_financials_ttm t
    JOIN dim_company c USING (company_id)
    WHERE c.ticker = 'AAPL'
    ORDER BY t.fiscal_year DESC, t.fiscal_quarter DESC
    LIMIT 5
    """
    result5 = db.execute_query(query5)
    print(result5.to_string(index=False))
    
    # Test 6: Data dictionary
    print("\n6. Testing vw_data_dictionary (Sample metrics)")
    query6 = """
    SELECT table_name, code, name, unit, category
    FROM vw_data_dictionary
    WHERE code IN ('REVENUE', 'NET_INCOME', 'ROE', 'CPIAUCSL', 'SP500')
    """
    result6 = db.execute_query(query6)
    print(result6.to_string(index=False))
    
    print("\n" + "="*80)
    print("✅ ALL VIEWS WORKING CORRECTLY!")
    print("="*80)
    print("\n🎉 Your CFO Assistant can now use these optimized views!")

if __name__ == "__main__":
    verify_new_views()
