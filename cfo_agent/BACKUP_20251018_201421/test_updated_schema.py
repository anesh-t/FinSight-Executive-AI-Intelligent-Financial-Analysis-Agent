"""
Test the updated schema matches with templates
"""
import asyncio
from db.pool import db_pool


async def test_schema():
    """Test that the SQL template works with actual schema"""
    
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("TESTING UPDATED SCHEMA COMPATIBILITY")
    print("="*100)
    
    # Test 1: Check mv_financials_annual columns
    print("\n[TEST 1] Checking mv_financials_annual columns:")
    print("-"*100)
    
    column_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'mv_financials_annual'
        ORDER BY ordinal_position
    """
    
    columns = await db_pool.execute_query(column_query)
    
    expected_columns = [
        'company_id', 'fiscal_year', 'quarters_count', 'has_full_year',
        'revenue_annual', 'operating_income_annual', 'net_income_annual',
        'gross_profit_annual', 'cogs_annual', 'r_and_d_expenses_annual',
        'sg_and_a_expenses_annual', 'ebit_annual', 'ebitda_annual',
        'cash_flow_ops_annual', 'cash_flow_investing_annual',
        'cash_flow_financing_annual', 'capex_annual',
        'total_assets_eoy', 'total_liabilities_eoy', 'equity_eoy'
    ]
    
    found_columns = [col['column_name'] for col in columns]
    
    print(f"Expected columns: {len(expected_columns)}")
    print(f"Found columns: {len(found_columns)}")
    
    missing = set(expected_columns) - set(found_columns)
    extra = set(found_columns) - set(expected_columns)
    
    if missing:
        print(f"\n❌ Missing columns: {missing}")
    if extra:
        print(f"\n✅ Extra columns (OK): {extra}")
    
    if not missing:
        print("\n✅ All expected columns present!")
    
    # Verify key columns
    key_checks = {
        'sg_and_a_expenses_annual': 'sg_and_a_expenses_annual' in found_columns,
        'cash_flow_ops_annual': 'cash_flow_ops_annual' in found_columns,
        'NOT eps_annual': 'eps_annual' not in found_columns,
        'NOT dividends_annual': 'dividends_annual' not in found_columns,
        'NOT buybacks_annual': 'buybacks_annual' not in found_columns,
    }
    
    print("\nKey column checks:")
    for check, result in key_checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    # Test 2: Execute the actual annual_metrics query
    print("\n[TEST 2] Testing annual_metrics query:")
    print("-"*100)
    
    test_query = """
        SELECT 
            c.ticker, 
            c.name, 
            mv.fiscal_year, 
            mv.revenue_annual/1e9 as revenue_b, 
            mv.net_income_annual/1e9 as net_income_b, 
            mv.operating_income_annual/1e9 as op_income_b, 
            mv.gross_profit_annual/1e9 as gross_profit_annual_b, 
            mv.r_and_d_expenses_annual/1e9 as rd_annual_b, 
            mv.sg_and_a_expenses_annual/1e9 as sga_annual_b, 
            mv.cogs_annual/1e9 as cogs_annual_b, 
            mv.cash_flow_ops_annual/1e9 as operating_cash_flow, 
            mv.cash_flow_investing_annual/1e9 as investing_cash_flow, 
            mv.cash_flow_financing_annual/1e9 as financing_cash_flow, 
            mv.capex_annual/1e9 as capex_annual_b, 
            SUM(f.eps) as eps, 
            SUM(f.dividends)/1e9 as dividends, 
            SUM(f.buybacks)/1e9 as buybacks, 
            r.gross_margin_annual, 
            r.operating_margin_annual, 
            r.net_margin_annual, 
            r.roe_annual_avg_equity, 
            r.roa_annual 
        FROM mv_financials_annual mv 
        JOIN mv_ratios_annual r USING (company_id, fiscal_year) 
        JOIN dim_company c USING (company_id) 
        LEFT JOIN fact_financials f 
            ON f.company_id = mv.company_id 
            AND f.fiscal_year = mv.fiscal_year 
        WHERE c.ticker = 'MSFT' 
            AND mv.fiscal_year = 2023 
        GROUP BY 
            c.ticker, c.name, mv.fiscal_year, 
            mv.revenue_annual, mv.net_income_annual, mv.operating_income_annual, 
            mv.gross_profit_annual, mv.r_and_d_expenses_annual, mv.sg_and_a_expenses_annual, 
            mv.cogs_annual, mv.cash_flow_ops_annual, mv.cash_flow_investing_annual, 
            mv.cash_flow_financing_annual, mv.capex_annual, 
            r.gross_margin_annual, r.operating_margin_annual, r.net_margin_annual, 
            r.roe_annual_avg_equity, r.roa_annual
    """
    
    try:
        result = await db_pool.execute_query(test_query)
        
        if result:
            print("✅ Query executed successfully!")
            row = result[0]
            print(f"\nMicrosoft 2023 Results:")
            print(f"  Ticker: {row['ticker']}")
            print(f"  Company: {row['name']}")
            print(f"  Year: {row['fiscal_year']}")
            print(f"  Revenue: ${float(row['revenue_b']):.2f}B")
            print(f"  Net Income: ${float(row['net_income_b']):.2f}B")
            print(f"  SG&A: ${float(row['sga_annual_b']):.2f}B")
            print(f"  Operating Cash Flow: ${float(row['operating_cash_flow']):.2f}B")
            print(f"  EPS (SUM): ${float(row['eps']):.2f}")
            print(f"  Dividends: ${float(row['dividends']):.2f}B" if row['dividends'] else "  Dividends: None")
            print(f"  Buybacks: ${float(row['buybacks']):.2f}B" if row['buybacks'] else "  Buybacks: None")
        else:
            print("❌ No results returned")
            
    except Exception as e:
        print(f"❌ Query failed: {str(e)}")
    
    # Test 3: Test with the agent
    print("\n[TEST 3] Testing with CFO Agent:")
    print("-"*100)
    
    from graph import cfo_agent_graph
    from db.whitelist import load_schema_cache
    from db.resolve import load_ticker_cache
    
    await load_schema_cache()
    await load_ticker_cache()
    
    test_queries = [
        "show microsoft revenue for 2023",
        "show microsoft EPS for 2023",
        "show apple SG&A for 2023",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            response = await cfo_agent_graph.run(query)
            print(f"Response: {response.split(chr(10))[0][:100]}...")
            print("✅ Success")
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
    
    print("\n" + "="*100)
    print("SCHEMA COMPATIBILITY TEST COMPLETE")
    print("="*100)
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(test_schema())
