"""
Verify ALL column names across all tables and views before creating combined views
"""
import asyncio
from db.pool import db_pool

async def check_all_schemas():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("VERIFYING ALL TABLE/VIEW SCHEMAS FOR COMBINED VIEWS")
    print("="*100)
    
    # List of all tables/views we need to check
    sources = [
        # Quarterly sources
        'fact_financials',
        'vw_ratios_quarter',
        'vw_stock_prices_quarter',
        'vw_macro_quarter',
        'vw_macro_sensitivity_rolling',
        # Annual sources
        'mv_financials_annual',
        'mv_ratios_annual',
        'mv_stock_prices_annual',
        'mv_macro_annual',
        'mv_macro_sensitivity_annual',
        # Dimension
        'dim_company'
    ]
    
    all_columns = {}
    
    for source in sources:
        print(f"\n{'='*100}")
        print(f"[{source}]")
        print("-"*100)
        
        query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{source}'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """
        
        try:
            cols = await db_pool.execute_query(query)
            
            if not cols:
                print(f"❌ NOT FOUND or NO COLUMNS")
                all_columns[source] = []
                continue
            
            all_columns[source] = [col['column_name'] for col in cols]
            
            print(f"✅ Found {len(cols)} columns:")
            print(f"\n{'Column Name':<40} {'Data Type':<20}")
            print("-"*60)
            for col in cols:
                print(f"{col['column_name']:<40} {col['data_type']:<20}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            all_columns[source] = []
    
    # Now generate the corrected SQL based on actual columns
    print("\n" + "="*100)
    print("GENERATING COLUMN MAPPINGS FOR COMBINED VIEWS")
    print("="*100)
    
    # Check what we need for quarterly Layer 1
    print("\n[QUARTERLY LAYER 1 - Core Company]")
    print("-"*100)
    
    print("\nFrom fact_financials:")
    fact_cols = all_columns.get('fact_financials', [])
    for col in fact_cols:
        if col not in ['financial_id', 'company_id', 'fiscal_year', 'fiscal_quarter', 'source_id', 'as_reported', 'version_ts']:
            print(f"  f.{col}")
    
    print("\nFrom vw_ratios_quarter:")
    ratio_cols = all_columns.get('vw_ratios_quarter', [])
    for col in ratio_cols:
        if col not in ['company_id', 'fiscal_year', 'fiscal_quarter']:
            print(f"  r.{col}")
    
    print("\nFrom vw_stock_prices_quarter:")
    stock_cols = all_columns.get('vw_stock_prices_quarter', [])
    for col in stock_cols:
        if col not in ['company_id', 'fiscal_year', 'fiscal_quarter']:
            print(f"  sp.{col}")
    
    # Check annual sources
    print("\n[ANNUAL LAYER 1 - Core Company]")
    print("-"*100)
    
    print("\nFrom mv_financials_annual:")
    fact_annual_cols = all_columns.get('mv_financials_annual', [])
    for col in fact_annual_cols:
        if col not in ['company_id', 'fiscal_year']:
            print(f"  fa.{col}")
    
    print("\nFrom mv_ratios_annual:")
    ratio_annual_cols = all_columns.get('mv_ratios_annual', [])
    for col in ratio_annual_cols:
        if col not in ['company_id', 'fiscal_year']:
            print(f"  ra.{col}")
    
    print("\nFrom mv_stock_prices_annual:")
    stock_annual_cols = all_columns.get('mv_stock_prices_annual', [])
    for col in stock_annual_cols:
        if col not in ['company_id', 'fiscal_year']:
            print(f"  sa.{col}")
    
    # Layer 2 additions
    print("\n[LAYER 2 - Macro Context]")
    print("-"*100)
    
    print("\nFrom vw_macro_quarter:")
    macro_q_cols = all_columns.get('vw_macro_quarter', [])
    for col in macro_q_cols:
        if col not in ['fiscal_year', 'fiscal_quarter']:
            print(f"  m.{col}")
    
    print("\nFrom mv_macro_annual:")
    macro_a_cols = all_columns.get('mv_macro_annual', [])
    for col in macro_a_cols:
        if col not in ['fiscal_year']:
            print(f"  ma.{col}")
    
    # Layer 3 additions
    print("\n[LAYER 3 - Sensitivity]")
    print("-"*100)
    
    print("\nFrom vw_macro_sensitivity_rolling:")
    sens_q_cols = all_columns.get('vw_macro_sensitivity_rolling', [])
    for col in sens_q_cols:
        if col not in ['company_id', 'fiscal_year', 'fiscal_quarter']:
            print(f"  ms.{col}")
    
    print("\nFrom mv_macro_sensitivity_annual:")
    sens_a_cols = all_columns.get('mv_macro_sensitivity_annual', [])
    for col in sens_a_cols:
        if col not in ['company_id', 'fiscal_year']:
            print(f"  msa.{col}")
    
    await db_pool.close()
    
    print("\n" + "="*100)
    print("✅ VERIFICATION COMPLETE")
    print("="*100)
    
    return all_columns

if __name__ == "__main__":
    asyncio.run(check_all_schemas())
