"""
Test macro context flow end-to-end
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from decomposer import QueryDecomposer
from router import IntentRouter
from planner import TaskPlanner
from sql_exec import SQLExecutor
from formatter import ResponseFormatter
from dotenv import load_dotenv

load_dotenv()


async def test_macro_query():
    """Test the complete flow for a macro context query"""
    
    question = "Show Apple's revenue with CPI for Q2 2023"
    
    print("="*80)
    print(f"TESTING: {question}")
    print("="*80)
    
    # Step 1: Decompose
    print("\n[STEP 1] DECOMPOSER")
    print("-"*80)
    decomposer = QueryDecomposer()
    decomposed = await decomposer.decompose(question)
    
    print(f"Tasks: {len(decomposed['tasks'])}")
    if decomposed['tasks']:
        task = decomposed['tasks'][0]
        print(f"Intent: {task['intent']}")
        print(f"Entities: {task['entities']}")
        print(f"Period: {task['period']}")
    
    # Step 2: Route
    print("\n[STEP 2] ROUTER")
    print("-"*80)
    router = IntentRouter()
    routed = router.route_task(decomposed['tasks'][0])
    
    print(f"Intent: {routed['intent']}")
    print(f"Template: {routed['template_name']}")
    print(f"Surfaces: {routed['surfaces']}")
    
    # Step 3: Plan
    print("\n[STEP 3] PLANNER")
    print("-"*80)
    planner = TaskPlanner()
    plan = await planner.plan_task(routed)
    
    print(f"Intent: {plan['intent']}")
    print(f"Template: {plan['template_name']}")
    print(f"SQL (first 300 chars):")
    print(plan['sql'][:300])
    print(f"Params: {plan['params']}")
    
    # Step 4: Execute
    print("\n[STEP 4] EXECUTOR")
    print("-"*80)
    executor = SQLExecutor()
    results = await executor.execute(plan['sql'], plan['params'])
    
    print(f"Rows returned: {len(results)}")
    if results:
        print(f"Columns: {list(results[0].keys())}")
        print(f"\nFirst row data:")
        for key, value in results[0].items():
            if value is not None:
                print(f"  {key}: {value}")
    
    # Step 5: Format
    print("\n[STEP 5] FORMATTER")
    print("-"*80)
    formatter = ResponseFormatter()
    context = {
        'question': question,
        'intent': plan['intent'],
        'citation_line': 'Sources: Test'
    }
    response = await formatter.format_response(results, context, {})
    
    print(f"Final Response:")
    print("-"*80)
    print(response)
    print("-"*80)
    
    # Check if macro indicators are in response
    print("\n[VERIFICATION]")
    print("-"*80)
    has_cpi = 'CPI' in response or 'cpi' in response
    has_gdp = 'GDP' in response or 'gdp' in response
    has_macro = 'Macro context' in response or 'macro' in response.lower()
    
    print(f"✅ Has CPI: {has_cpi}")
    print(f"✅ Has GDP: {has_gdp}")
    print(f"✅ Has 'Macro context': {has_macro}")
    
    if has_cpi and (has_gdp or has_macro):
        print("\n🎉 SUCCESS! Macro context is being displayed!")
    else:
        print("\n❌ FAILED! Macro context is missing!")
        print("\nDEBUG: Check if these columns were in results:")
        if results:
            print(f"  gdp_t: {'gdp_t' in results[0]}")
            print(f"  cpi: {'cpi' in results[0]}")
            print(f"  unemployment_rate: {'unemployment_rate' in results[0]}")


if __name__ == "__main__":
    asyncio.run(test_macro_query())
