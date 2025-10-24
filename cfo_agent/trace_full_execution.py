"""Trace full agent execution to find where it's failing"""
import asyncio
from decomposer import QueryDecomposer
from router import IntentRouter  
from planner import TaskPlanner
from sql_builder import SQLBuilder
from sql_exec import SQLExecutor
from formatter import ResponseFormatter
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def trace():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    query = "show Apple gross margin for Q2 2023"
    
    print("\n" + "="*100)
    print(f"TRACING: {query}")
    print("="*100)
    
    # Step 1: Decompose
    print("\n[STEP 1] DECOMPOSITION")
    print("-"*100)
    decomposer = QueryDecomposer()
    decomposed = await decomposer.decompose(query)
    
    print(f"Tasks: {len(decomposed.get('tasks', []))}")
    for i, task in enumerate(decomposed.get('tasks', []), 1):
        print(f"\nTask {i}:")
        print(f"  Intent: {task.get('intent')}")
        print(f"  Entities: {task.get('entities')}")
        print(f"  Measures: {task.get('measures')}")
        print(f"  Period: {task.get('period')}")
    
    # Step 2: Route
    print("\n\n[STEP 2] ROUTING")
    print("-"*100)
    router = IntentRouter()
    routed_tasks = [router.route_task(task) for task in decomposed.get('tasks', [])]
    
    for i, routed in enumerate(routed_tasks, 1):
        print(f"\nRouted Task {i}:")
        print(f"  Template: {routed.get('template_name')}")
        print(f"  Surfaces: {routed.get('surfaces')}")
    
    # Step 3: Plan
    print("\n\n[STEP 3] PLANNING")
    print("-"*100)
    planner = TaskPlanner()
    plans = []
    for routed in routed_tasks:
        plan = await planner.plan_task(routed)
        plans.append(plan)
    
    for i, plan in enumerate(plans, 1):
        print(f"\nPlan {i}:")
        print(f"  Template: {plan.get('template_name')}")
        print(f"  SQL Length: {len(plan.get('sql', ''))}")
        print(f"  Params: {plan.get('params')}")
    
    # Step 4: Build SQL
    print("\n\n[STEP 4] SQL BUILDING")
    print("-"*100)
    sql_builder = SQLBuilder()
    sqls_and_params = []
    
    for i, plan in enumerate(plans, 1):
        sql, params = await sql_builder.build_sql(plan)
        sqls_and_params.append((sql, params))
        print(f"\nSQL {i}:")
        print(f"  Params: {params}")
        print(f"  SQL: {sql[:200]}...")
    
    # Step 5: Execute
    print("\n\n[STEP 5] EXECUTION")
    print("-"*100)
    executor = SQLExecutor()
    
    results = []
    for i, (sql, params) in enumerate(sqls_and_params, 1):
        print(f"\nExecuting SQL {i}...")
        try:
            result = await executor.execute(sql, params)
            results.append(result)
            print(f"  ✅ Success! {len(result)} rows")
            if result:
                print(f"  Columns: {list(result[0].keys())[:10]}...")
                # Check for ratios
                if 'gross_margin' in result[0]:
                    print(f"  ✅ gross_margin: {result[0]['gross_margin']}")
        except Exception as e:
            results.append([])
            print(f"  ❌ Failed: {e}")
    
    # Step 6: Format
    print("\n\n[STEP 6] FORMATTING")
    print("-"*100)
    formatter = ResponseFormatter()
    
    if results and results[0]:
        context = {
            'intent': plans[0].get('intent'),
            'params': plans[0].get('params', {}),
            'question': query,
            'citation_line': ''
        }
        
        try:
            formatted = await formatter.format_response(results[0], context, [])
            print(f"\nFormatted Response:")
            print(formatted)
        except Exception as e:
            print(f"❌ Formatting failed: {e}")
    else:
        print("❌ No results to format")
    
    await db_pool.close()

asyncio.run(trace())
