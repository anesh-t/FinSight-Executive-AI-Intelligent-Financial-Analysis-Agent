"""
Check what cash flow columns are available in the database
"""
import asyncio
from db.pool import db_pool


async def check_columns():
    """Check columns in various tables"""
    await db_pool.initialize()
    
    # Check fact_financials columns
    print("\n" + "="*80)
    print("FACT_FINANCIALS COLUMNS (checking for cash flow)")
    print("="*80)
    result = await db_pool.execute_query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'fact_financials' 
        AND (column_name ILIKE '%cash%' OR column_name ILIKE '%dividend%' OR column_name ILIKE '%buyback%' OR column_name ILIKE '%eps%')
        ORDER BY column_name
    """)
    for row in result:
        print(f"  {row['column_name']:<40} {row['data_type']}")
    
    # Check mv_financials_annual
    print("\n" + "="*80)
    print("MV_FINANCIALS_ANNUAL COLUMNS (checking for cash flow)")
    print("="*80)
    result = await db_pool.execute_query("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'mv_financials_annual' 
        AND (column_name ILIKE '%cash%' OR column_name ILIKE '%dividend%' OR column_name ILIKE '%buyback%' OR column_name ILIKE '%eps%')
        ORDER BY column_name
    """)
    for row in result:
        print(f"  {row['column_name']:<40} {row['data_type']}")
    
    # Check all column names in fact_financials
    print("\n" + "="*80)
    print("ALL FACT_FINANCIALS COLUMNS")
    print("="*80)
    result = await db_pool.execute_query("""
        SELECT column_name
        FROM information_schema.columns 
        WHERE table_name = 'fact_financials'
        ORDER BY ordinal_position
    """)
    cols = [row['column_name'] for row in result]
    for i in range(0, len(cols), 3):
        row_cols = cols[i:i+3]
        print("  " + " | ".join(f"{col:<30}" for col in row_cols))
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(check_columns())
