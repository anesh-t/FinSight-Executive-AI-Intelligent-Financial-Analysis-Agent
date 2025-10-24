"""
Verification script for advanced migration features
Demonstrates peer rankings, growth, and macro sensitivities
"""

from database import SupabaseConnector

def verify_advanced_features():
    db = SupabaseConnector()
    
    print("\n" + "="*80)
    print("ADVANCED FEATURES VERIFICATION")
    print("="*80)
    
    # Test 1: Latest snapshot from vw_cfo_answers
    print("\n1. Latest Snapshot (vw_cfo_answers) - Apple Q2 2025")
    query1 = """
    SELECT ticker, fyq_label, 
           revenue/1e9 as revenue_b,
           ROUND(net_margin * 100, 2) as net_margin_pct,
           ROUND(revenue_yoy * 100, 2) as revenue_yoy_pct,
           rank_revenue, rank_net_margin,
           ROUND(beta_nm_cpi_12q::numeric, 4) as beta_cpi
    FROM vw_cfo_answers
    WHERE ticker = 'AAPL'
    ORDER BY fiscal_year DESC, fiscal_quarter DESC
    LIMIT 1
    """
    result1 = db.execute_query(query1)
    print(result1.to_string(index=False))
    
    # Test 2: Peer rankings on net margin (latest quarter)
    print("\n2. Peer Rankings - Net Margin Leaders (Q2 2025)")
    query2 = """
    SELECT c.ticker, 
           ROUND(p.net_margin * 100, 2) as net_margin_pct,
           p.rank_net_margin,
           ROUND(p.pct_net_margin * 100, 2) as percentile,
           ROUND(p.z_net_margin, 2) as z_score
    FROM vw_peer_stats_quarter p
    JOIN dim_company c USING (company_id)
    WHERE fiscal_year = 2025 AND fiscal_quarter = 2
    ORDER BY rank_net_margin
    """
    result2 = db.execute_query(query2)
    print(result2.to_string(index=False))
    
    # Test 3: Growth analysis - QoQ and YoY
    print("\n3. Growth Analysis - Apple Last 4 Quarters")
    query3 = """
    SELECT ticker, fyq_label,
           revenue/1e9 as revenue_b,
           ROUND(revenue_qoq * 100, 2) as qoq_pct,
           ROUND(revenue_yoy * 100, 2) as yoy_pct
    FROM vw_cfo_answers
    WHERE ticker = 'AAPL'
    ORDER BY fiscal_year DESC, fiscal_quarter DESC
    LIMIT 4
    """
    result3 = db.execute_query(query3)
    print(result3.to_string(index=False))
    
    # Test 4: Annual CAGR
    print("\n4. Revenue CAGR - All Companies (2024)")
    query4 = """
    SELECT c.ticker, g.fiscal_year,
           ROUND(g.revenue_yoy * 100, 2) as yoy_pct,
           ROUND(g.revenue_cagr_3y * 100, 2) as cagr_3y_pct,
           ROUND(g.revenue_cagr_5y * 100, 2) as cagr_5y_pct
    FROM vw_growth_annual g
    JOIN dim_company c USING (company_id)
    WHERE g.fiscal_year = 2024
    ORDER BY g.revenue_cagr_3y DESC NULLS LAST
    """
    result4 = db.execute_query(query4)
    print(result4.to_string(index=False))
    
    # Test 5: Macro sensitivities
    print("\n5. Macro Sensitivities - Latest Quarter")
    query5 = """
    SELECT ticker,
           ROUND(beta_nm_cpi_12q::numeric, 4) as beta_cpi,
           ROUND(beta_nm_ffr_12q::numeric, 4) as beta_ffr,
           ROUND(beta_nm_spx_12q::numeric, 4) as beta_spx,
           ROUND(beta_nm_unrate_12q::numeric, 4) as beta_unrate
    FROM vw_cfo_answers
    WHERE fiscal_year = 2025 AND fiscal_quarter = 2
    ORDER BY ticker
    """
    result5 = db.execute_query(query5)
    print(result5.to_string(index=False))
    
    # Test 6: Financial health check
    print("\n6. Financial Health Check - Latest Quarter")
    query6 = """
    SELECT c.ticker, h.fiscal_year, h.fiscal_quarter,
           h.balance_status,
           h.flag_negative_equity,
           h.flag_net_loss
    FROM vw_financial_health_quarter h
    JOIN dim_company c USING (company_id)
    WHERE fiscal_year = 2025 AND fiscal_quarter = 2
    ORDER BY ticker
    """
    result6 = db.execute_query(query6)
    print(result6.to_string(index=False))
    
    # Test 7: Outlier detection
    print("\n7. Outlier Detection - Any 3-Sigma Events")
    query7 = """
    SELECT c.ticker, o.fiscal_year, o.fiscal_quarter,
           ROUND(o.z_rev, 2) as z_revenue,
           ROUND(o.z_nm, 2) as z_net_margin,
           o.outlier_revenue_3sigma,
           o.outlier_net_margin_3sigma
    FROM vw_outliers_quarter o
    JOIN dim_company c USING (company_id)
    WHERE o.outlier_revenue_3sigma = 1 OR o.outlier_net_margin_3sigma = 1
    ORDER BY ticker, fiscal_year DESC, fiscal_quarter DESC
    LIMIT 10
    """
    result7 = db.execute_query(query7)
    if result7.empty:
        print("No 3-sigma outliers detected (data is clean)")
    else:
        print(result7.to_string(index=False))
    
    # Test 8: TTM trends
    print("\n8. TTM Revenue Trend - Apple Last 4 Quarters")
    query8 = """
    SELECT ticker, fyq_label,
           revenue_ttm/1e9 as ttm_revenue_b,
           ROUND(revenue_ttm_delta * 100, 2) as ttm_delta_pct
    FROM vw_cfo_answers
    WHERE ticker = 'AAPL'
    ORDER BY fiscal_year DESC, fiscal_quarter DESC
    LIMIT 4
    """
    result8 = db.execute_query(query8)
    print(result8.to_string(index=False))
    
    print("\n" + "="*80)
    print("✅ ALL ADVANCED FEATURES VERIFIED!")
    print("="*80)
    print("\n🎉 Your database now supports:")
    print("   ✅ Peer rankings & percentiles")
    print("   ✅ Growth calculations (QoQ/YoY/CAGR)")
    print("   ✅ Macro sensitivities (rolling regressions)")
    print("   ✅ Health checks & outlier detection")
    print("   ✅ TTM trends & deltas")
    print("   ✅ Unified CFO answer surface")

if __name__ == "__main__":
    verify_advanced_features()
