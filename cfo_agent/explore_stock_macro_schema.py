"""
Explore stock prices and macro indicator tables/views
"""
import asyncio
from db.pool import db_pool

async def explore_schema():
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("EXPLORING STOCK PRICES & MACRO INDICATORS SCHEMA")
    print("="*100)
    
    # 1. Find all tables/views with 'stock' or 'price' in the name
    print("\n[1] STOCK PRICE TABLES/VIEWS:")
    print("-"*100)
    
    stock_query = """
        SELECT 
            schemaname,
            tablename as name,
            'table' as type
        FROM pg_tables
        WHERE schemaname = 'public'
        AND (tablename LIKE '%stock%' OR tablename LIKE '%price%')
        
        UNION ALL
        
        SELECT 
            schemaname,
            viewname as name,
            'view' as type
        FROM pg_views
        WHERE schemaname = 'public'
        AND (viewname LIKE '%stock%' OR viewname LIKE '%price%')
        
        ORDER BY name
    """
    
    stock_tables = await db_pool.execute_query(stock_query)
    for table in stock_tables:
        print(f"  {table['type'].upper()}: {table['name']}")
    
    # 2. Check fact_stock_prices schema
    print("\n[2] FACT_STOCK_PRICES SCHEMA:")
    print("-"*100)
    
    price_schema_query = """
        SELECT 
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_name = 'fact_stock_prices'
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """
    
    price_cols = await db_pool.execute_query(price_schema_query)
    if price_cols:
        print(f"\n{'Column':<30} {'Type':<20} {'Nullable':<10}")
        print("-"*60)
        for col in price_cols:
            print(f"{col['column_name']:<30} {col['data_type']:<20} {col['is_nullable']:<10}")
        
        # Sample data
        print("\n📊 Sample Data (5 rows):")
        sample_query = """
            SELECT * FROM fact_stock_prices
            ORDER BY fiscal_year DESC, fiscal_quarter DESC
            LIMIT 5
        """
        sample = await db_pool.execute_query(sample_query)
        if sample:
            for row in sample:
                print(f"  {dict(row)}")
    else:
        print("  ❌ Table not found or no columns")
    
    # 3. Find all tables/views with 'macro' or 'indicator' in the name
    print("\n[3] MACRO INDICATOR TABLES/VIEWS:")
    print("-"*100)
    
    macro_query = """
        SELECT 
            schemaname,
            tablename as name,
            'table' as type
        FROM pg_tables
        WHERE schemaname = 'public'
        AND (tablename LIKE '%macro%' OR tablename LIKE '%indicator%' OR tablename LIKE '%economic%')
        
        UNION ALL
        
        SELECT 
            schemaname,
            viewname as name,
            'view' as type
        FROM pg_views
        WHERE schemaname = 'public'
        AND (viewname LIKE '%macro%' OR viewname LIKE '%indicator%' OR viewname LIKE '%economic%')
        
        ORDER BY name
    """
    
    macro_tables = await db_pool.execute_query(macro_query)
    if macro_tables:
        for table in macro_tables:
            print(f"  {table['type'].upper()}: {table['name']}")
    else:
        print("  No tables found with 'macro', 'indicator', or 'economic' in name")
    
    # 4. Check each macro table/view schema
    print("\n[4] MACRO TABLES/VIEWS DETAILED SCHEMA:")
    print("-"*100)
    
    for table in macro_tables:
        table_name = table['name']
        print(f"\n📊 {table_name} ({table['type'].upper()}):")
        
        schema_query = f"""
            SELECT 
                column_name,
                data_type
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """
        
        cols = await db_pool.execute_query(schema_query)
        if cols:
            print(f"  Columns: {', '.join([col['column_name'] for col in cols])}")
            
            # Sample data
            try:
                sample_query = f"SELECT * FROM {table_name} LIMIT 2"
                sample = await db_pool.execute_query(sample_query)
                if sample:
                    print(f"  Sample: {len(sample)} rows")
                    for i, row in enumerate(sample, 1):
                        print(f"    Row {i}: {dict(row)}")
            except Exception as e:
                print(f"  ⚠️ Could not fetch sample: {str(e)[:50]}")
    
    # 5. Check available macro indicators
    print("\n[5] AVAILABLE MACRO INDICATORS:")
    print("-"*100)
    
    # Check if there's a dim_macro_indicator or similar table
    indicator_query = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename LIKE '%dim%indicator%'
    """
    
    indicator_tables = await db_pool.execute_query(indicator_query)
    if indicator_tables:
        for table in indicator_tables:
            table_name = table['tablename']
            print(f"\n📊 Indicators from {table_name}:")
            indicators_query = f"SELECT * FROM {table_name} LIMIT 10"
            indicators = await db_pool.execute_query(indicators_query)
            for ind in indicators:
                print(f"  {dict(ind)}")
    
    # 6. Check data availability (date ranges)
    print("\n[6] DATA AVAILABILITY:")
    print("-"*100)
    
    # Stock prices date range
    if stock_tables:
        print("\n📈 Stock Prices (fact_stock_prices):")
        try:
            date_range_query = """
                SELECT 
                    MIN(fiscal_year) as earliest_year,
                    MAX(fiscal_year) as latest_year,
                    MIN(fiscal_quarter) as min_quarter,
                    MAX(fiscal_quarter) as max_quarter,
                    COUNT(DISTINCT company_id) as num_companies,
                    COUNT(*) as total_records
                FROM fact_stock_prices
            """
            date_range = await db_pool.execute_query(date_range_query)
            if date_range:
                r = date_range[0]
                print(f"  Fiscal Year Range: {r['earliest_year']} to {r['latest_year']}")
                print(f"  Quarters: Q{r['min_quarter']} to Q{r['max_quarter']}")
                print(f"  Companies: {r['num_companies']}")
                print(f"  Total Records: {r['total_records']:,}")
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
    
    # Macro indicators date range (if we find the main table)
    for table in macro_tables:
        if 'fact' in table['name'] or 'macro' in table['name']:
            print(f"\n📊 Macro Indicators ({table['name']}):")
            try:
                # Try to find date column
                date_col_query = f"""
                    SELECT column_name 
                    FROM information_schema.columns
                    WHERE table_name = '{table['name']}'
                    AND (column_name LIKE '%date%' OR column_name LIKE '%period%')
                    LIMIT 1
                """
                date_col = await db_pool.execute_query(date_col_query)
                if date_col:
                    col_name = date_col[0]['column_name']
                    range_query = f"""
                        SELECT 
                            MIN({col_name}) as earliest,
                            MAX({col_name}) as latest,
                            COUNT(*) as total_records
                        FROM {table['name']}
                    """
                    range_data = await db_pool.execute_query(range_query)
                    if range_data:
                        r = range_data[0]
                        print(f"  Date Range: {r['earliest']} to {r['latest']}")
                        print(f"  Total Records: {r['total_records']:,}")
            except Exception as e:
                print(f"  ⚠️ Could not check date range: {str(e)[:50]}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(explore_schema())
