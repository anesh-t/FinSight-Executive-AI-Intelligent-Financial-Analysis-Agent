"""
Verify that multi-company + macro queries return data for BOTH companies
"""
import asyncio
from decomposer import QueryDecomposer
from router import IntentRouter
from planner import TaskPlanner
from sql_builder import SQLBuilder
from sql_exec import SQLExecutor
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def verify():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    decomposer = QueryDecomposer()
    router = IntentRouter()
    planner = TaskPlanner()
    sql_builder = SQLBuilder()
    sql_executor = SQLExecutor()
    
    query = "compare Apple with Google and how CPI affected both companies Q2 2023"
    print(f"Query: {query}")
    print("="*100)
    
    # Execute pipeline
    decomposed = await decomposer.decompose(query)
    print(f"\n1. Decomposed entities: {decomposed['tasks'][0]['entities']}")
    
    routed = router.route_task(decomposed['tasks'][0])
    print(f"2. Intent: {routed['intent']}")
    
    plan = await planner.plan_task(routed)
    print(f"3. Params: {plan['params']}")
    print(f"4. SQL: {plan['sql'][:150]}...")
    
    sql, params, _ = await sql_builder.build_sql(plan)
    
    # Execute SQL
    results = await sql_executor.execute(sql, params)
    print(f"\n5. Results returned: {len(results)} rows")
    
    if results:
        print(f"\nFirst 3 rows:")
        for i, row in enumerate(results[:3]):
            print(f"  Row {i+1}: ticker={row.get('ticker')}, name={row.get('name')}, revenue_b={row.get('revenue_b')}")
    
    # Check unique tickers in results
    tickers_in_results = set(row.get('ticker') for row in results if row.get('ticker'))
    print(f"\n✅ Unique tickers in results: {tickers_in_results}")
    
    if len(tickers_in_results) >= 2:
        print("✅ SUCCESS! Both companies' data returned!")
    else:
        print("❌ ISSUE! Only one company's data returned")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(verify())
