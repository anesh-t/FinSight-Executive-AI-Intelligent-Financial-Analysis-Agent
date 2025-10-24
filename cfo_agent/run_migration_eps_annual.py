"""
Run migration to add eps_annual to mv_financials_annual
"""
import asyncio
from db.pool import db_pool


async def run_migration():
    """Execute the migration to add eps_annual column"""
    
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("MIGRATION: Adding eps_annual to mv_financials_annual")
    print("="*100)
    
    # Read the migration SQL
    with open('migrations/add_eps_annual.sql', 'r') as f:
        migration_sql = f.read()
    
    # Split into individual statements
    statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    for i, statement in enumerate(statements, 1):
        if not statement:
            continue
            
        print(f"\n[Step {i}] Executing...")
        
        # Show what we're doing
        if 'DROP' in statement.upper():
            print("  → Dropping existing mv_financials_annual view")
        elif 'CREATE MATERIALIZED VIEW' in statement.upper():
            print("  → Creating mv_financials_annual with eps_annual column")
        elif 'CREATE INDEX' in statement.upper():
            print("  → Creating performance indexes")
        elif 'GRANT' in statement.upper():
            print("  → Granting permissions")
        elif 'REFRESH' in statement.upper():
            print("  → Refreshing materialized view with data")
        
        try:
            # Execute using the pool's connection
            async with db_pool.pool.acquire() as conn:
                await conn.execute(statement)
            print("  ✅ Success")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            if 'does not exist' not in str(e).lower():
                raise
    
    # Verify the new column exists
    print("\n" + "="*100)
    print("VERIFICATION: Checking if eps_annual column exists")
    print("="*100)
    
    verify_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'mv_financials_annual'
        AND column_name = 'eps_annual'
    """
    
    result = await db_pool.execute_query(verify_query)
    
    if result:
        print(f"\n✅ Column 'eps_annual' exists with type: {result[0]['data_type']}")
    else:
        print("\n❌ Column 'eps_annual' not found!")
    
    # Show sample data
    print("\n" + "="*100)
    print("SAMPLE DATA: eps_annual for Microsoft")
    print("="*100)
    
    sample_query = """
        SELECT 
            c.ticker,
            c.name,
            mv.fiscal_year,
            mv.eps_annual,
            mv.quarter_count
        FROM mv_financials_annual mv
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'MSFT'
        ORDER BY mv.fiscal_year DESC
        LIMIT 5
    """
    
    sample_data = await db_pool.execute_query(sample_query)
    
    print(f"\n{'Year':<10} {'EPS Annual':<15} {'Quarters':<10}")
    print("-"*100)
    for row in sample_data:
        eps = float(row['eps_annual']) if row['eps_annual'] else 0
        print(f"{row['fiscal_year']:<10} ${eps:<14.2f} {row['quarter_count']}")
    
    # Compare with quarterly data
    print("\n" + "="*100)
    print("COMPARISON: Annual vs Quarterly Sum (Microsoft 2023)")
    print("="*100)
    
    comparison_query = """
        SELECT 
            'Quarterly Data' as source,
            fiscal_year,
            fiscal_quarter,
            eps
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'MSFT' AND fiscal_year = 2023
        ORDER BY fiscal_quarter
    """
    
    quarterly_data = await db_pool.execute_query(comparison_query)
    
    print("\nQuarterly EPS:")
    total = 0
    for row in quarterly_data:
        eps = float(row['eps'])
        print(f"  Q{row['fiscal_quarter']} 2023: ${eps:.2f}")
        total += eps
    
    print(f"  ──────────────")
    print(f"  Sum: ${total:.2f}")
    
    annual_query = """
        SELECT eps_annual
        FROM mv_financials_annual mv
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'MSFT' AND fiscal_year = 2023
    """
    
    annual_data = await db_pool.execute_query(annual_query)
    if annual_data:
        annual_eps = float(annual_data[0]['eps_annual'])
        print(f"\nAnnual EPS (from view): ${annual_eps:.2f}")
        
        if abs(annual_eps - total) < 0.01:
            print("\n✅ VERIFIED: Annual EPS matches sum of quarterly EPS!")
        else:
            print(f"\n⚠️  WARNING: Mismatch! Annual: ${annual_eps:.2f}, Quarterly Sum: ${total:.2f}")
    
    print("\n" + "="*100)
    print("MIGRATION COMPLETE")
    print("="*100)
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(run_migration())
