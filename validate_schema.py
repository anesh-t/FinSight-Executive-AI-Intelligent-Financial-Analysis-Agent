"""
Schema Validation Script
Checks all expected tables, views, and materialized views
"""

from database import SupabaseConnector
import pandas as pd

def validate_schema():
    db = SupabaseConnector()
    
    print("\n" + "="*80)
    print("SCHEMA VALIDATION: ALL DATABASE OBJECTS")
    print("="*80)
    
    query = """
    WITH expected AS (
      SELECT * FROM (VALUES
        -- tables
        ('dim_company','table'),('dim_financial_metric','table'),('dim_ratio','table'),
        ('dim_stock_metric','table'),('dim_macro_indicator','table'),
        ('dim_peer_group','table'),('bridge_company_peer_group','table'),
        ('dim_fiscal_calendar','table'),('dim_data_source','table'),
        ('etl_lineage_log','table'),('agent_allowed_surfaces','table'),
        ('fact_financials','table'),('fact_ratios','table'),
        ('fact_stock_prices','table'),('fact_macro_indicators','table'),
        -- optional tables (FX)
        ('dim_currency','table'),('fx_quarterly','table'),

        -- views
        ('vw_latest_company_quarter','view'),('vw_gross_profit_reconciled','view'),
        ('vw_ratios_canonical','view'),('vw_company_quarter','view'),
        ('vw_quarter_end','view'),('vw_company_quarter_macro','view'),
        ('vw_growth_quarter','view'),('vw_growth_annual','view'),('vw_growth_ttm','view'),
        ('vw_peer_stats_quarter','view'),('vw_peer_stats_annual','view'),
        ('vw_financial_health_quarter','view'),('vw_outliers_quarter','view'),
        ('vw_macro_sensitivity_rolling','view'),('vw_cfo_answers','view'),
        ('vw_metric_dictionary','view'),
        ('vw_fact_citations','view'),('vw_stock_citations','view'),('vw_macro_citations','view'),
        ('vw_schema_cache','view'),

        -- materialized views
        ('mv_financials_annual','matview'),('mv_financials_ttm','matview'),
        ('mv_ratios_annual','matview'),('mv_ratios_ttm','matview')
      ) AS t(name, kind)
    ),
    actual AS (
      SELECT table_name AS name, 'table' AS kind FROM information_schema.tables
       WHERE table_schema='public' AND table_type='BASE TABLE'
      UNION ALL
      SELECT table_name, 'view' FROM information_schema.views
       WHERE table_schema='public'
      UNION ALL
      SELECT matviewname, 'matview' FROM pg_matviews
       WHERE schemaname='public'
    )
    SELECT e.kind, e.name,
           CASE WHEN a.name IS NOT NULL THEN 'present' ELSE 'missing' END AS status,
           CASE WHEN e.name IN ('dim_currency','fx_quarterly') THEN 'optional' ELSE 'core' END AS expectation
    FROM expected e
    LEFT JOIN actual a USING (name, kind)
    ORDER BY e.kind, e.name
    """
    
    result = db.execute_query(query)
    
    # Group by kind
    tables = result[result['kind'] == 'table']
    views = result[result['kind'] == 'view']
    matviews = result[result['kind'] == 'matview']
    
    # Print tables
    print("\n" + "="*80)
    print("TABLES")
    print("="*80)
    print(tables.to_string(index=False))
    
    tables_core = tables[tables['expectation'] == 'core']
    tables_core_present = tables_core[tables_core['status'] == 'present']
    tables_core_missing = tables_core[tables_core['status'] == 'missing']
    
    tables_optional = tables[tables['expectation'] == 'optional']
    tables_optional_present = tables_optional[tables_optional['status'] == 'present']
    tables_optional_missing = tables_optional[tables_optional['status'] == 'missing']
    
    print(f"\nCore Tables: {len(tables_core_present)}/{len(tables_core)} present")
    if len(tables_core_missing) > 0:
        print(f"⚠️ Missing core tables: {', '.join(tables_core_missing['name'].tolist())}")
    else:
        print("✅ All core tables present")
    
    print(f"Optional Tables: {len(tables_optional_present)}/{len(tables_optional)} present")
    if len(tables_optional_missing) > 0:
        print(f"ℹ️ Missing optional tables: {', '.join(tables_optional_missing['name'].tolist())}")
    
    # Print views
    print("\n" + "="*80)
    print("VIEWS")
    print("="*80)
    print(views.to_string(index=False))
    
    views_present = views[views['status'] == 'present']
    views_missing = views[views['status'] == 'missing']
    
    print(f"\nViews: {len(views_present)}/{len(views)} present")
    if len(views_missing) > 0:
        print(f"⚠️ Missing views: {', '.join(views_missing['name'].tolist())}")
    else:
        print("✅ All views present")
    
    # Print materialized views
    print("\n" + "="*80)
    print("MATERIALIZED VIEWS")
    print("="*80)
    print(matviews.to_string(index=False))
    
    matviews_present = matviews[matviews['status'] == 'present']
    matviews_missing = matviews[matviews['status'] == 'missing']
    
    print(f"\nMaterialized Views: {len(matviews_present)}/{len(matviews)} present")
    if len(matviews_missing) > 0:
        print(f"⚠️ Missing materialized views: {', '.join(matviews_missing['name'].tolist())}")
    else:
        print("✅ All materialized views present")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_core = len(tables_core) + len(views) + len(matviews)
    total_core_present = len(tables_core_present) + len(views_present) + len(matviews_present)
    total_optional = len(tables_optional)
    total_optional_present = len(tables_optional_present)
    
    print(f"\nCore Objects: {total_core_present}/{total_core} present ({total_core_present/total_core*100:.1f}%)")
    print(f"Optional Objects: {total_optional_present}/{total_optional} present")
    
    # Check if all core objects present
    all_core_present = (len(tables_core_missing) == 0 and 
                        len(views_missing) == 0 and 
                        len(matviews_missing) == 0)
    
    print("\n" + "="*80)
    if all_core_present:
        print("✅ ALL CORE DATABASE OBJECTS PRESENT!")
        print("="*80)
        print("\n🎉 Your schema is complete with:")
        print(f"   - {len(tables_core_present)} core tables")
        print(f"   - {len(views_present)} views")
        print(f"   - {len(matviews_present)} materialized views")
        if len(tables_optional_present) > 0:
            print(f"   - {len(tables_optional_present)} optional tables")
        print("\n✅ Database is production-ready!")
    else:
        print("⚠️ SOME CORE OBJECTS ARE MISSING")
        print("="*80)
        missing_count = len(tables_core_missing) + len(views_missing) + len(matviews_missing)
        print(f"\nTotal missing core objects: {missing_count}")
        if len(tables_core_missing) > 0:
            print(f"Missing tables: {', '.join(tables_core_missing['name'].tolist())}")
        if len(views_missing) > 0:
            print(f"Missing views: {', '.join(views_missing['name'].tolist())}")
        if len(matviews_missing) > 0:
            print(f"Missing materialized views: {', '.join(matviews_missing['name'].tolist())}")
    
    return all_core_present

if __name__ == "__main__":
    validate_schema()
