"""
Quick test to validate the fixes
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
from citations import CitationFetcher
from dotenv import load_dotenv

load_dotenv()


async def test_macro_queries():
    """Test macro context queries that were failing"""
    
    test_queries = [
        "Show Apple's revenue with CPI for Q2 2023",
        "Get Microsoft's performance with GDP context Q1 2023",
        "Show Google's revenue with unemployment rate Q3 2023",
        "Who had the highest net margin Q2 2023?",
    ]
    
    print("="*80)
    print("TESTING FIXES")
    print("="*80)
    print()
    
    decomposer = QueryDecomposer()
    router = IntentRouter()
    planner = TaskPlanner()
    executor = SQLExecutor()
    citation_fetcher = CitationFetcher()
    formatter = ResponseFormatter()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {query}")
        print(f"{'='*80}")
        
        try:
            # Decompose
            decomposed = await decomposer.decompose(query)
            if not decomposed.get('tasks'):
                print("❌ No tasks generated")
                continue
            
            task = decomposed['tasks'][0]
            intent = task.get('intent')
            print(f"✓ Intent: {intent}")
            
            # Route
            routed = router.route_task(task)
            template = routed.get('template_name')
            print(f"✓ Template: {template}")
            
            # Plan
            plan = await planner.plan_task(routed)
            sql = plan.get('sql')
            params = plan.get('params')
            print(f"✓ SQL generated ({len(sql)} chars)")
            print(f"✓ Params: {params}")
            
            # Execute
            results = await executor.execute(sql, params)
            print(f"✓ Results: {len(results)} rows")
            
            if results:
                # Check if macro columns are present
                row = results[0]
                has_macro = any(col in row for col in ['gdp', 'gdp_t', 'cpi', 'unemployment_rate', 'fed_funds_rate'])
                print(f"✓ Has macro columns: {has_macro}")
                
                # Format
                citations = await citation_fetcher.fetch_citations(results, plan)
                context = {
                    'question': query,
                    'intent': plan['intent'],
                    'citation_line': citations.get('citation_line', '')
                }
                response = await formatter.format_response(results, context, {})
                
                # Check if macro is in response
                has_macro_in_response = any(word in response.lower() for word in ['cpi', 'gdp', 'unemployment', 'fed rate', 'macro context'])
                print(f"✓ Has macro in response: {has_macro_in_response}")
                
                print(f"\nResponse preview:")
                print(response[:200] + "..." if len(response) > 200 else response)
                
                if intent and 'macro' in intent and has_macro and has_macro_in_response:
                    print("\n✅ PASS - Macro context working!")
                elif intent and 'macro' in intent and has_macro and not has_macro_in_response:
                    print("\n⚠️  PARTIAL - Macro data retrieved but not displayed")
                elif intent and 'macro' in intent:
                    print("\n❌ FAIL - Macro intent but no macro data")
                else:
                    print("\n✅ PASS - Query executed successfully")
            else:
                print("❌ No results returned")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(test_macro_queries())
