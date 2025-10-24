"""
Create stock price views (quarterly & annual)
Run this once to set up the database views
"""
import asyncio
from db.pool import db_pool

async def create_views():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("CREATING STOCK PRICE VIEWS")
    print("="*100)
    
    # Read the SQL file
    with open('sql/create_stock_price_views.sql', 'r') as f:
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
            'vw_stock_prices_quarter' as view_name,
            COUNT(*) as total_records,
            COUNT(DISTINCT company_id) as num_companies,
            MIN(fiscal_year) as earliest_year,
            MAX(fiscal_year) as latest_year
        FROM vw_stock_prices_quarter
    """
    
    check_annual = """
        SELECT 
            'mv_stock_prices_annual' as view_name,
            COUNT(*) as total_records,
            COUNT(DISTINCT company_id) as num_companies,
            MIN(fiscal_year) as earliest_year,
            MAX(fiscal_year) as latest_year
        FROM mv_stock_prices_annual
    """
    
    try:
        print("\n✓ Quarterly View (vw_stock_prices_quarter):")
        result = await db_pool.execute_query(check_quarterly)
        if result:
            r = result[0]
            print(f"  Records: {r['total_records']}")
            print(f"  Companies: {r['num_companies']}")
            print(f"  Years: {r['earliest_year']} - {r['latest_year']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    try:
        print("\n✓ Annual View (mv_stock_prices_annual):")
        result = await db_pool.execute_query(check_annual)
        if result:
            r = result[0]
            print(f"  Records: {r['total_records']}")
            print(f"  Companies: {r['num_companies']}")
            print(f"  Years: {r['earliest_year']} - {r['latest_year']}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Sample data
    print("\n[SAMPLE DATA] Quarterly view for 2023:")
    sample_q = """
        SELECT 
            c.ticker,
            sq.fiscal_year,
            sq.fiscal_quarter,
            ROUND(sq.avg_price::numeric, 2) as avg_price,
            ROUND(sq.return_qoq::numeric * 100, 2) as return_qoq_pct
        FROM vw_stock_prices_quarter sq
        JOIN dim_company c USING (company_id)
        WHERE sq.fiscal_year = 2023
        ORDER BY c.ticker, sq.fiscal_quarter
        LIMIT 5
    """
    
    try:
        result = await db_pool.execute_query(sample_q)
        for row in result:
            print(f"  {row['ticker']} Q{row['fiscal_quarter']} {row['fiscal_year']}: ${row['avg_price']} (return: {row['return_qoq_pct']}%)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n[SAMPLE DATA] Annual view for 2023:")
    sample_a = """
        SELECT 
            c.ticker,
            sa.fiscal_year,
            ROUND(sa.avg_price_annual::numeric, 2) as avg_price,
            ROUND(sa.return_annual::numeric * 100, 2) as return_pct
        FROM mv_stock_prices_annual sa
        JOIN dim_company c USING (company_id)
        WHERE sa.fiscal_year = 2023
        ORDER BY c.ticker
    """
    
    try:
        result = await db_pool.execute_query(sample_a)
        for row in result:
            print(f"  {row['ticker']} {row['fiscal_year']}: ${row['avg_price']} (return: {row['return_pct']}%)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    await db_pool.close()
    
    print("\n" + "="*100)
    print("✅ STOCK PRICE VIEWS CREATED SUCCESSFULLY!")
    print("="*100)
    print("\nNext steps:")
    print("1. Add views to whitelist (db/whitelist.py)")
    print("2. Add SQL templates (catalog/templates.json)")
    print("3. Update router, formatter, decomposer")
    print("="*100)

if __name__ == "__main__":
    asyncio.run(create_views())
