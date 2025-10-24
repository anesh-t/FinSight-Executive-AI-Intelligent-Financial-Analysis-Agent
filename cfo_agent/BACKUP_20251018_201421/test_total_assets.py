"""
Test total assets query for Amazon
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_total_assets():
    """Test total assets query"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("TESTING: Total Assets Query")
    print("="*100)
    
    # Check what's in the database
    print("\n[1] Checking database for Amazon total_assets:")
    print("-"*100)
    
    db_query = """
        SELECT 
            c.ticker,
            c.name,
            f.fiscal_year,
            f.fiscal_quarter,
            f.total_assets/1e9 as total_assets_b
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AMZN'
        AND f.fiscal_year = 2023
        ORDER BY f.fiscal_quarter
    """
    
    db_results = await db_pool.execute_query(db_query)
    
    if db_results:
        print(f"Found {len(db_results)} quarters:")
        for row in db_results:
            print(f"  Q{row['fiscal_quarter']} 2023: ${float(row['total_assets_b']):.2f}B")
    else:
        print("❌ No data found in database!")
    
    # Check annual view
    print("\n[2] Checking mv_financials_annual:")
    print("-"*100)
    
    annual_query = """
        SELECT 
            c.ticker,
            mv.fiscal_year,
            mv.total_assets_eoy/1e9 as total_assets_b
        FROM mv_financials_annual mv
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'AMZN'
        AND mv.fiscal_year = 2023
    """
    
    annual_results = await db_pool.execute_query(annual_query)
    
    if annual_results:
        print(f"FY2023: ${float(annual_results[0]['total_assets_b']):.2f}B")
    else:
        print("❌ No data in mv_financials_annual!")
    
    # Test through the agent
    print("\n[3] Testing through CFO Agent:")
    print("-"*100)
    
    test_queries = [
        "show amazon total assets for 2023",
        "show AMZN total assets for 2023",
        "what are amazon total assets in 2023",
        "amazon total assets 2023",
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            result = await cfo_agent_graph.run(query)
            if result:
                lines = result.split('\n')
                print(f"Response: {lines[0]}")
                if "No data" in result or "No results" in result:
                    print("  ❌ No data returned")
                else:
                    print("  ✅ Success")
            else:
                print("  ❌ Empty response")
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
    
    # Check the formatter
    print("\n[4] Checking if 'total_assets' or 'assets' is recognized:")
    print("-"*100)
    
    from formatter import Formatter
    formatter = Formatter()
    
    test_questions = [
        "show amazon total assets for 2023",
        "show amazon assets for 2023",
        "what are total assets",
    ]
    
    for question in test_questions:
        metrics = formatter._extract_requested_metrics(question)
        print(f"Question: '{question}'")
        print(f"  Extracted metrics: {metrics}")
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(test_total_assets())
