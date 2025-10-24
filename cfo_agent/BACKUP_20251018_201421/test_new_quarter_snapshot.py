"""Test the new quarter_snapshot SQL with vw_ratios_quarter"""
import asyncio
from db.pool import db_pool

async def test():
    await db_pool.initialize()
    
    # Test the exact SQL from quarter_snapshot template
    query = """
        SELECT 
            c.ticker, 
            c.name, 
            f.fiscal_year, 
            f.fiscal_quarter,
            f.revenue/1e9 as revenue_b,
            r.gross_margin,
            r.operating_margin,
            r.net_margin,
            r.roe,
            r.roa,
            r.debt_to_equity,
            r.debt_to_assets,
            r.rnd_to_revenue,
            r.sgna_to_revenue
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        LEFT JOIN vw_ratios_quarter r ON r.company_id = f.company_id 
            AND r.fiscal_year = f.fiscal_year 
            AND r.fiscal_quarter = f.fiscal_quarter
        WHERE c.ticker = 'AAPL'
        AND f.fiscal_year = 2023
        AND f.fiscal_quarter = 2
    """
    
    result = await db_pool.execute_query(query)
    
    if result:
        row = result[0]
        print("\n✅ SQL Query Works! Results:")
        print("-"*100)
        for key, val in row.items():
            if val is not None:
                if isinstance(val, float) and key != 'revenue_b':
                    if 'debt' in key or key in ['roe', 'roa']:
                        print(f"  {key:<30} {val:.4f}")
                    else:
                        print(f"  {key:<30} {val*100:.2f}%")
                else:
                    print(f"  {key:<30} {val}")
    else:
        print("\n❌ No results - SQL query failed")
    
    # Now test what the agent returns
    print("\n" + "="*100)
    print("Testing Agent Query:")
    print("="*100)
    
    from graph import cfo_agent_graph
    from db.whitelist import load_schema_cache
    from db.resolve import load_ticker_cache
    
    await load_schema_cache()
    await load_ticker_cache()
    
    test_queries = [
        "show Apple gross margin for Q2 2023",
        "show Apple debt to equity for Q2 2023",
        "show Apple R&D intensity for Q2 2023",
    ]
    
    for q in test_queries:
        print(f"\nQuery: {q}")
        result = await cfo_agent_graph.run(q)
        print(f"Result: {result.split(chr(10))[0]}")
    
    await db_pool.close()

asyncio.run(test())
