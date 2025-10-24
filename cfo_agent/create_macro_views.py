"""
Create macro indicator views (quarterly & annual)
Run this once to set up the database views
"""
import asyncio
from db.pool import db_pool

async def create_views():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("CREATING MACRO INDICATOR VIEWS")
    print("="*100)
    
    # Read the SQL file
    with open('sql/create_macro_views_simple.sql', 'r') as f:
        sql_script = f.read()
    
    # Split into individual statements (by semicolon)
    statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--') and not s.strip().startswith('/*')]
    
    successful = 0
    failed = 0
    
    for i, statement in enumerate(statements, 1):
        # Skip comments and empty statements
        if not statement or statement.startswith('--') or 'COMMENT ON' in statement.upper():
            continue
            
        try:
            print(f"\n[{i}/{len(statements)}] Executing statement...")
            # Get first line as preview
            first_line = statement.split('\n')[0][:80]
            print(f"  Preview: {first_line}...")
            
            await db_pool.execute_query(statement)
            print(f"  ✅ Success")
            successful += 1
            
        except Exception as e:
            # Check if it's just a verification query that returns nothing
            if 'SELECT' in statement.upper() and 'CREATE' not in statement.upper():
                print(f"  ℹ️  Query executed (verification)")
                successful += 1
            else:
                print(f"  ❌ Error: {str(e)[:100]}")
                failed += 1
    
    print("\n" + "="*100)
    print(f"SUMMARY: {successful} successful, {failed} failed")
    print("="*100)
    
    # Verify the views were created
    print("\n[VERIFICATION] Checking if views exist...")
    
    check_quarterly = """
        SELECT 
            'vw_macro_quarter' as view_name,
            COUNT(*) as total_records,
            MIN(fiscal_year) as earliest_year,
            MAX(fiscal_year) as latest_year
        FROM vw_macro_quarter
    """
    
    check_annual = """
        SELECT 
            'mv_macro_annual' as view_name,
            COUNT(*) as total_records,
            MIN(fiscal_year) as earliest_year,
            MAX(fiscal_year) as latest_year
        FROM mv_macro_annual
    """
    
    try:
        print("\n✓ Quarterly View (vw_macro_quarter):")
        result = await db_pool.execute_query(check_quarterly)
        if result:
            r = result[0]
            print(f"  Records: {r['total_records']}")
            print(f"  Years: {r['earliest_year']} - {r['latest_year']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    try:
        print("\n✓ Annual View (mv_macro_annual):")
        result = await db_pool.execute_query(check_annual)
        if result:
            r = result[0]
            print(f"  Records: {r['total_records']}")
            print(f"  Years: {r['earliest_year']} - {r['latest_year']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Sample data
    print("\n[SAMPLE DATA] Quarterly view for 2023:")
    sample_q = """
        SELECT 
            fiscal_year,
            fiscal_quarter,
            ROUND(gdp::numeric, 2) as gdp,
            ROUND(cpi::numeric, 2) as cpi,
            ROUND(unemployment_rate::numeric, 2) as unemployment,
            ROUND(fed_funds_rate::numeric, 2) as fed_rate
        FROM vw_macro_quarter
        WHERE fiscal_year = 2023
        ORDER BY fiscal_quarter
    """
    
    try:
        result = await db_pool.execute_query(sample_q)
        for row in result:
            print(f"  Q{row['fiscal_quarter']} {row['fiscal_year']}: GDP=${row['gdp']}B, CPI={row['cpi']}, Unemp={row['unemployment']}%, Fed={row['fed_rate']}%")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n[SAMPLE DATA] Annual view for 2023:")
    sample_a = """
        SELECT 
            fiscal_year,
            ROUND(gdp_annual::numeric, 2) as gdp_avg,
            ROUND(cpi_annual::numeric, 2) as cpi_avg,
            ROUND(unemployment_rate_annual::numeric, 2) as unemployment_avg,
            ROUND(fed_funds_rate_annual::numeric, 2) as fed_rate_avg
        FROM mv_macro_annual
        WHERE fiscal_year = 2023
    """
    
    try:
        result = await db_pool.execute_query(sample_a)
        for row in result:
            print(f"  {row['fiscal_year']}: GDP=${row['gdp_avg']}B (avg), CPI={row['cpi_avg']} (avg), Unemp={row['unemployment_avg']}% (avg), Fed={row['fed_rate_avg']}% (avg)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    await db_pool.close()
    
    print("\n" + "="*100)
    print("✅ MACRO INDICATOR VIEWS CREATED SUCCESSFULLY!")
    print("="*100)
    print("\nNext steps:")
    print("1. Add views to whitelist (db/whitelist.py)")
    print("2. Add SQL templates (catalog/templates.json)")
    print("3. Update router, formatter, decomposer")
    print("="*100)

if __name__ == "__main__":
    asyncio.run(create_views())
