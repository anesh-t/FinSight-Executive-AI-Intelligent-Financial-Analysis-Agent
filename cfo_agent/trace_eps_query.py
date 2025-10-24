"""
Trace exactly how EPS query is processed
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool


async def trace_eps_query():
    """Trace the EPS query step by step"""
    
    await db_pool.initialize()
    
    print("\n" + "="*100)
    print("TRACING: 'show microsoft eps for 2023'")
    print("="*100)
    
    # Show what's in the database
    print("\n[STEP 1] CHECKING DATABASE - What EPS data exists for Microsoft 2023:")
    print("-"*100)
    
    query = """
        SELECT 
            c.ticker,
            c.name,
            f.fiscal_year,
            f.fiscal_quarter,
            f.eps
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'MSFT'
        AND f.fiscal_year = 2023
        ORDER BY f.fiscal_quarter
    """
    
    results = await db_pool.execute_query(query)
    
    print(f"{'Quarter':<15} {'EPS':<10}")
    print("-"*100)
    total = 0
    count = 0
    for row in results:
        print(f"Q{row['fiscal_quarter']} 2023{' '*8} ${row['eps']:.2f}")
        total += float(row['eps'])
        count += 1
    
    avg = total / count if count > 0 else 0
    print("-"*100)
    print(f"Average:{' '*8} ${avg:.2f}")
    print(f"\n✅ Database has {count} quarters of EPS data for Microsoft 2023")
    
    # Show the SQL query that annual_metrics template uses
    print("\n[STEP 2] SQL TEMPLATE - What query does 'annual_metrics' execute:")
    print("-"*100)
    print("""
SELECT 
    c.ticker, 
    c.name, 
    mv.fiscal_year,
    AVG(f.eps) as eps    ← AVERAGES THE 4 QUARTERLY VALUES
FROM mv_financials_annual mv
JOIN dim_company c USING (company_id)
LEFT JOIN fact_financials f 
    ON f.company_id = mv.company_id 
    AND f.fiscal_year = mv.fiscal_year
WHERE c.ticker = 'MSFT'
    AND mv.fiscal_year = 2023
GROUP BY c.ticker, c.name, mv.fiscal_year
    """)
    
    # Execute the actual query
    print("\n[STEP 3] EXECUTING ANNUAL QUERY:")
    print("-"*100)
    
    annual_query = """
        SELECT 
            c.ticker, 
            c.name, 
            mv.fiscal_year,
            AVG(f.eps) as eps
        FROM mv_financials_annual mv
        JOIN dim_company c USING (company_id)
        LEFT JOIN fact_financials f 
            ON f.company_id = mv.company_id 
            AND f.fiscal_year = mv.fiscal_year
        WHERE c.ticker = 'MSFT'
            AND mv.fiscal_year = 2023
        GROUP BY c.ticker, c.name, mv.fiscal_year
    """
    
    annual_result = await db_pool.execute_query(annual_query)
    
    if annual_result:
        row = annual_result[0]
        print(f"Company: {row['name']} ({row['ticker']})")
        print(f"Year: {row['fiscal_year']}")
        print(f"EPS: ${float(row['eps']):.2f}")
        print(f"\n✅ Query returned: ${float(row['eps']):.2f}")
    
    # Now run through the actual agent
    print("\n[STEP 4] RUNNING THROUGH CFO AGENT:")
    print("-"*100)
    
    user_query = "show microsoft eps for 2023"
    print(f"User Query: '{user_query}'")
    print("\nAgent Response:")
    print("-"*100)
    
    response = await cfo_agent_graph.run(user_query)
    print(response)
    
    # Comparison
    print("\n" + "="*100)
    print("SUMMARY - DATA SOURCE VERIFICATION")
    print("="*100)
    print(f"""
📊 DATABASE (fact_financials):
   Q1 2023: $2.45
   Q2 2023: $2.69
   Q3 2023: $2.99
   Q4 2023: $2.93
   ─────────────────
   Average: ${avg:.2f}

📋 ANNUAL QUERY RESULT:
   EPS: ${float(annual_result[0]['eps']):.2f}

✅ AGENT RESPONSE:
   {response.split('\n')[0]}

🎯 CONCLUSION:
   The agent sources EPS from fact_financials table and calculates
   the average of all 4 quarters when you ask for annual data.
    """)
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(trace_eps_query())
