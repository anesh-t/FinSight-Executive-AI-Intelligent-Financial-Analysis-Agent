"""
Test stock price queries (quarterly & annual)
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test_stock_prices():
    """Test all stock price query types"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("TESTING STOCK PRICE QUERIES - Quarterly & Annual")
    print("="*100)
    
    test_cases = [
        # Quarterly queries
        ("Quarterly - Basic Price", "show Apple stock price Q2 2023"),
        ("Quarterly - Return", "show Microsoft stock return Q3 2023"),
        ("Quarterly - Volatility", "show Google volatility Q2 2023"),
        ("Quarterly - Generic Stock", "show Amazon stock Q2 2023"),
        
        # Annual queries
        ("Annual - Basic Price", "show Apple stock price 2023"),
        ("Annual - Return", "show Microsoft annual return 2023"),
        ("Annual - Full Year", "show Google stock performance 2023"),
        ("Annual - Generic", "show Meta stock 2023"),
    ]
    
    results = []
    
    for label, query in test_cases:
        print(f"\n{'='*100}")
        print(f"[{label}]")
        print(f"Query: '{query}'")
        print("-"*100)
        
        try:
            result = await cfo_agent_graph.run(query)
            
            # Get first line
            first_line = result.split('\n')[0] if result else "No response"
            
            # Check if we got stock price data
            has_price = any(word in first_line.lower() for word in ['stock price', 'price of', 'averaged', 'closing price'])
            has_return = 'return' in first_line.lower()
            has_volatility = 'volatility' in first_line.lower()
            
            if has_price or has_return or has_volatility:
                status = "✅ SUCCESS"
            elif "no data" in first_line.lower() or "not found" in first_line.lower():
                status = "❌ NO DATA"
            else:
                status = "⚠️ UNEXPECTED"
            
            print(f"{status}")
            print(f"Response: {first_line}")
            
            results.append({
                'label': label,
                'query': query,
                'status': status,
                'response': first_line
            })
            
        except Exception as e:
            print(f"❌ ERROR")
            print(f"Error: {str(e)[:100]}")
            results.append({
                'label': label,
                'query': query,
                'status': "❌ ERROR",
                'response': str(e)[:100]
            })
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY TABLE")
    print("="*100)
    print(f"\n{'#':<4} {'Test Case':<35} {'Status':<15} {'Response Preview':<45}")
    print("-"*100)
    
    for i, r in enumerate(results, 1):
        preview = r['response'][:42] + "..." if len(r['response']) > 45 else r['response']
        print(f"{i:<4} {r['label']:<35} {r['status']:<15} {preview:<45}")
    
    # Count successes
    success = sum(1 for r in results if "✅" in r['status'])
    total = len(results)
    
    print("\n" + "="*100)
    print(f"RESULTS: {success}/{total} tests passing ({success/total*100:.1f}%)")
    print("="*100)
    
    # Test direct database queries to verify views
    print("\n" + "="*100)
    print("DATABASE VERIFICATION - Direct View Queries")
    print("="*100)
    
    # Test quarterly view
    print("\n[1] Quarterly View (vw_stock_prices_quarter):")
    q_test = """
        SELECT 
            c.ticker,
            sq.fiscal_year,
            sq.fiscal_quarter,
            ROUND(sq.avg_price::numeric, 2) as avg_price,
            ROUND(sq.return_qoq::numeric * 100, 2) as return_qoq_pct
        FROM vw_stock_prices_quarter sq
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL' 
        AND sq.fiscal_year = 2023 
        AND sq.fiscal_quarter = 2
        LIMIT 1
    """
    
    try:
        result = await db_pool.execute_query(q_test)
        if result:
            r = result[0]
            print(f"  ✅ Found: {r['ticker']} Q{r['fiscal_quarter']} {r['fiscal_year']}")
            print(f"     Avg Price: ${r['avg_price']}")
            print(f"     QoQ Return: {r['return_qoq_pct']}%")
        else:
            print(f"  ❌ No data found")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test annual view
    print("\n[2] Annual View (mv_stock_prices_annual):")
    a_test = """
        SELECT 
            c.ticker,
            sa.fiscal_year,
            ROUND(sa.avg_price_annual::numeric, 2) as avg_price,
            ROUND(sa.return_annual::numeric * 100, 2) as return_annual_pct,
            ROUND(sa.high_price_annual::numeric, 2) as year_high,
            ROUND(sa.low_price_annual::numeric, 2) as year_low
        FROM mv_stock_prices_annual sa
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AAPL' 
        AND sa.fiscal_year = 2023
        LIMIT 1
    """
    
    try:
        result = await db_pool.execute_query(a_test)
        if result:
            r = result[0]
            print(f"  ✅ Found: {r['ticker']} {r['fiscal_year']}")
            print(f"     Avg Price: ${r['avg_price']}")
            print(f"     Annual Return: {r['return_annual_pct']}%")
            print(f"     Range: ${r['year_low']} - ${r['year_high']}")
        else:
            print(f"  ❌ No data found")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    await db_pool.close()
    
    print("\n" + "="*100)
    if success == total:
        print("✅ ALL STOCK PRICE TESTS PASSING!")
    elif success >= total * 0.75:
        print("⚠️ MOST TESTS PASSING - Some fixes needed")
    else:
        print("❌ MULTIPLE FAILURES - Investigation needed")
    print("="*100)

if __name__ == "__main__":
    asyncio.run(test_stock_prices())
