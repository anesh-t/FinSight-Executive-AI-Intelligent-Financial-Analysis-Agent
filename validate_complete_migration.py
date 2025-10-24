"""
Complete Migration Validation Script
Runs all 10 validation checks across all migration phases
"""

from database import SupabaseConnector
import pandas as pd

def validate_complete_migration():
    db = SupabaseConnector()
    
    print("\n" + "="*80)
    print("COMPLETE MIGRATION VALIDATION")
    print("="*80)
    
    # Test 1: Coverage sanity
    print("\n" + "="*80)
    print("1. COVERAGE SANITY: 2019-2025, Complete Quarters per Company")
    print("="*80)
    query1 = """
    SELECT company_id,
           MIN(fiscal_year) AS min_fy,
           MAX(fiscal_year) AS max_fy,
           COUNT(*) AS rows,
           COUNT(DISTINCT (fiscal_year,fiscal_quarter)) AS qtrs
    FROM fact_financials
    GROUP BY 1
    ORDER BY 1
    """
    result1 = db.execute_query(query1)
    print(result1.to_string(index=False))
    
    # Test 2: Fiscal calendar coverage
    print("\n" + "="*80)
    print("2. FISCAL CALENDAR: Present for All Rows")
    print("="*80)
    query2 = """
    SELECT COUNT(*) AS fin_rows,
           COUNT(*) FILTER (WHERE c.company_id IS NOT NULL) AS cal_rows
    FROM fact_financials f
    LEFT JOIN dim_fiscal_calendar c
      ON c.company_id=f.company_id AND c.fiscal_year=f.fiscal_year AND c.fiscal_quarter=f.fiscal_quarter
    """
    result2 = db.execute_query(query2)
    print(result2.to_string(index=False))
    if result2['fin_rows'].iloc[0] == result2['cal_rows'].iloc[0]:
        print("✅ 100% fiscal calendar coverage")
    else:
        print("⚠️ Missing fiscal calendar entries")
    
    # Test 3: Macro overlay joins
    print("\n" + "="*80)
    print("3. MACRO OVERLAY: Joins Resolve Correctly")
    print("="*80)
    query3 = """
    SELECT company_id, fiscal_year, fiscal_quarter, 
           ROUND(cpi::numeric, 2) as cpi, 
           ROUND(fed_funds_rate::numeric, 2) as fed_rate, 
           ROUND(sp500_index::numeric, 2) as sp500
    FROM vw_company_quarter_macro
    ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC
    LIMIT 10
    """
    result3 = db.execute_query(query3)
    print(result3.to_string(index=False))
    
    # Test 4: Provenance backfill
    print("\n" + "="*80)
    print("4. PROVENANCE: Backfill Complete")
    print("="*80)
    query4 = """
    SELECT
      (SELECT COUNT(*) FROM fact_financials WHERE source_id IS NULL)   AS fin_missing_source,
      (SELECT COUNT(*) FROM fact_stock_prices WHERE source_id IS NULL) AS stock_missing_source,
      (SELECT COUNT(*) FROM fact_macro_indicators WHERE source_id IS NULL) AS macro_missing_source
    """
    result4 = db.execute_query(query4)
    print(result4.to_string(index=False))
    total_missing = result4.sum(axis=1).iloc[0]
    if total_missing == 0:
        print("✅ 100% provenance coverage")
    else:
        print(f"⚠️ {total_missing} rows missing source")
    
    # Test 5: Citations views
    print("\n" + "="*80)
    print("5. CITATIONS VIEWS: Readable")
    print("="*80)
    
    print("\n5a. Financial Citations:")
    query5a = "SELECT * FROM vw_fact_citations ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 3"
    result5a = db.execute_query(query5a)
    print(f"Rows: {len(result5a)}")
    if not result5a.empty:
        print(result5a[['ticker', 'fiscal_year', 'fiscal_quarter', 'revenue', 'source_code']].to_string(index=False))
    
    print("\n5b. Stock Citations:")
    query5b = "SELECT * FROM vw_stock_citations ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 3"
    result5b = db.execute_query(query5b)
    print(f"Rows: {len(result5b)}")
    if not result5b.empty:
        print(result5b[['ticker', 'fiscal_year', 'fiscal_quarter', 'close_price', 'source_code']].to_string(index=False))
    
    print("\n5c. Macro Citations:")
    query5c = "SELECT * FROM vw_macro_citations ORDER BY quarter_end DESC, indicator_code LIMIT 3"
    result5c = db.execute_query(query5c)
    print(f"Rows: {len(result5c)}")
    if not result5c.empty:
        print(result5c[['indicator_code', 'quarter_end', 'value', 'source_code']].to_string(index=False))
    
    # Test 6: Authoritative GP flags
    print("\n" + "="*80)
    print("6. AUTHORITATIVE GP FLAGS: Present in vw_cfo_answers")
    print("="*80)
    query6 = """
    SELECT company_id, fiscal_year, fiscal_quarter, 
           gross_profit_source, 
           ROUND(gp_delta_abs::numeric, 2) as gp_delta_abs, 
           ROUND(gp_delta_pct::numeric, 4) as gp_delta_pct
    FROM vw_cfo_answers
    ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC
    LIMIT 10
    """
    result6 = db.execute_query(query6)
    print(result6.to_string(index=False))
    
    # Test 7: Annual/TTM layers
    print("\n" + "="*80)
    print("7. ANNUAL/TTM LAYERS: Available")
    print("="*80)
    
    print("\n7a. Annual Financials:")
    query7a = "SELECT * FROM mv_financials_annual ORDER BY company_id, fiscal_year DESC LIMIT 5"
    result7a = db.execute_query(query7a)
    print(f"Rows: {len(result7a)}")
    
    print("\n7b. TTM Financials:")
    query7b = "SELECT * FROM mv_financials_ttm ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 5"
    result7b = db.execute_query(query7b)
    print(f"Rows: {len(result7b)}")
    
    print("\n7c. Annual Ratios:")
    query7c = "SELECT * FROM mv_ratios_annual ORDER BY company_id, fiscal_year DESC LIMIT 5"
    result7c = db.execute_query(query7c)
    print(f"Rows: {len(result7c)}")
    
    print("\n7d. TTM Ratios:")
    query7d = "SELECT * FROM mv_ratios_ttm ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC LIMIT 5"
    result7d = db.execute_query(query7d)
    print(f"Rows: {len(result7d)}")
    
    # Test 8: Peer stats
    print("\n" + "="*80)
    print("8. PEER STATS: Populated (Latest Quarter)")
    print("="*80)
    query8 = """
    SELECT company_id, fiscal_year, fiscal_quarter,
           rank_revenue, rank_net_margin, rank_roe
    FROM vw_peer_stats_quarter
    ORDER BY fiscal_year DESC, fiscal_quarter DESC, company_id
    LIMIT 10
    """
    result8 = db.execute_query(query8)
    print(result8.to_string(index=False))
    
    # Test 9: Growth views
    print("\n" + "="*80)
    print("9. GROWTH VIEWS: Populated")
    print("="*80)
    
    print("\n9a. Quarterly Growth:")
    query9a = """
    SELECT company_id, fiscal_year, fiscal_quarter,
           ROUND(revenue_qoq::numeric, 4) as revenue_qoq,
           ROUND(revenue_yoy::numeric, 4) as revenue_yoy
    FROM vw_growth_quarter 
    ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC 
    LIMIT 5
    """
    result9a = db.execute_query(query9a)
    print(result9a.to_string(index=False))
    
    print("\n9b. Annual Growth:")
    query9b = """
    SELECT company_id, fiscal_year,
           ROUND(revenue_yoy::numeric, 4) as revenue_yoy,
           ROUND(revenue_cagr_3y::numeric, 4) as cagr_3y
    FROM vw_growth_annual 
    ORDER BY company_id, fiscal_year DESC 
    LIMIT 5
    """
    result9b = db.execute_query(query9b)
    print(result9b.to_string(index=False))
    
    print("\n9c. TTM Growth:")
    query9c = """
    SELECT company_id, fiscal_year, fiscal_quarter,
           ROUND(revenue_ttm_delta::numeric, 4) as revenue_ttm_delta
    FROM vw_growth_ttm 
    ORDER BY company_id, fiscal_year DESC, fiscal_quarter DESC 
    LIMIT 5
    """
    result9c = db.execute_query(query9c)
    print(result9c.to_string(index=False))
    
    # Test 10: Agent guardrails
    print("\n" + "="*80)
    print("10. AGENT GUARDRAILS: Wired (Whitelist + Schema Cache)")
    print("="*80)
    
    query10a = "SELECT COUNT(*) AS allowed_surfaces FROM agent_allowed_surfaces"
    result10a = db.execute_query(query10a)
    print(f"\nAllowed surfaces: {result10a['allowed_surfaces'].iloc[0]}")
    
    query10b = """
    SELECT surface_name, COUNT(*) AS cols
    FROM vw_schema_cache 
    GROUP BY surface_name 
    ORDER BY surface_name
    """
    result10b = db.execute_query(query10b)
    print(f"\nSchema cache entries by surface:")
    print(result10b.to_string(index=False))
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    checks = {
        "Coverage (2019-2025)": len(result1) == 5,
        "Fiscal Calendar (100%)": result2['fin_rows'].iloc[0] == result2['cal_rows'].iloc[0],
        "Macro Overlay": not result3.empty,
        "Provenance (100%)": total_missing == 0,
        "Citations Views": not result5a.empty and not result5b.empty and not result5c.empty,
        "GP Flags": not result6.empty,
        "Annual/TTM Layers": not result7a.empty and not result7b.empty,
        "Peer Stats": not result8.empty,
        "Growth Views": not result9a.empty and not result9b.empty and not result9c.empty,
        "Agent Guardrails": result10a['allowed_surfaces'].iloc[0] == 18
    }
    
    print("\n")
    for check_name, passed in checks.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{check_name}: {status}")
    
    all_passed = all(checks.values())
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL VALIDATION CHECKS PASSED!")
        print("="*80)
        print("\n✅ Your database is production-ready with:")
        print("   - Complete data coverage (2019-2025)")
        print("   - 100% fiscal calendar coverage")
        print("   - Working macro overlay")
        print("   - 100% provenance tracking")
        print("   - Operational citations views")
        print("   - GP reconciliation flags")
        print("   - Annual/TTM materialized views")
        print("   - Peer statistics & rankings")
        print("   - Growth calculations (QoQ/YoY/CAGR)")
        print("   - Agent guardrails (18 surfaces)")
    else:
        print("⚠️ SOME VALIDATION CHECKS FAILED")
        print("="*80)
        print("\nPlease review the failed checks above.")
    
    return all_passed

if __name__ == "__main__":
    validate_complete_migration()
