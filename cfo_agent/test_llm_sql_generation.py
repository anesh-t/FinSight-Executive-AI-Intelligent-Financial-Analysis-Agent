"""
Test LLM-Based SQL Generation (GPT-4o)
Tests the system with use_generative=True
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from generative_sql import GenerativeSQLBuilder
from db.whitelist import validate_sql, load_schema_cache
from db.pool import db_pool
from dotenv import load_dotenv

load_dotenv()

# Diverse test queries
TEST_QUERIES = [
    # Basic queries
    {"q": "Show Apple's revenue for Q2 2023", "cat": "Basic"},
    {"q": "What is Microsoft's net income in Q1 2023?", "cat": "Basic"},
    
    # Multiple metrics
    {"q": "Show Apple's revenue, net income, and gross margin for Q2 2023", "cat": "Multiple Metrics"},
    
    # Complex queries
    {"q": "Show me Apple's revenue, operating income, R&D expenses, stock price, and volatility for Q2 2023", "cat": "Complex"},
    
    # Time series
    {"q": "Show Apple's revenue for the last 4 quarters", "cat": "Time Series"},
    
    # With macro context
    {"q": "Show Apple's revenue with GDP and CPI for Q2 2023", "cat": "Macro Context"},
    
    # Growth
    {"q": "Show Apple's revenue growth YoY for Q2 2023", "cat": "Growth"},
    
    # Comparison
    {"q": "Compare Apple and Microsoft revenue for Q2 2023", "cat": "Comparison"},
    
    # Annual
    {"q": "Show Apple's annual revenue for 2023", "cat": "Annual"},
    
    # Latest
    {"q": "Show Apple's latest quarter results", "cat": "Latest"},
]


async def test_llm_generation():
    """Test LLM-based SQL generation"""
    
    print("="*80)
    print("🤖 TESTING LLM-BASED SQL GENERATION (GPT-4o)")
    print("="*80)
    print("\nuse_generative = True (ENABLED)\n")
    
    # Load schema
    try:
        await load_schema_cache()
        print("✅ Schema cache loaded\n")
    except Exception as e:
        print(f"⚠️  Warning: {e}\n")
    
    builder = GenerativeSQLBuilder()
    
    # Output file
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"llm_sql_generation_{timestamp}.md"
    
    results = []
    
    with open(output_file, 'w') as f:
        f.write("# 🤖 LLM-BASED SQL GENERATION TEST RESULTS\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Method:** GPT-4o with 549-line prompt\n")
        f.write(f"**Setting:** use_generative = True\n\n")
        f.write("---\n\n")
        
        for i, test in enumerate(TEST_QUERIES, 1):
            question = test['q']
            category = test['cat']
            
            print(f"\n{'='*80}")
            print(f"Test {i}/{len(TEST_QUERIES)}: {category}")
            print(f"{'='*80}")
            print(f"\n💬 USER ASKS:")
            print(f"   \"{question}\"")
            
            f.write(f"## Test {i}: {category}\n\n")
            f.write(f"### 💬 User Question:\n")
            f.write(f"> {question}\n\n")
            
            try:
                # Build context
                context = {
                    "intent": question,
                    "surfaces": ["vw_company_complete_quarter"],
                    "entities_resolved": {},
                    "params": {"limit": 10}
                }
                
                # Generate SQL with GPT-4o
                print(f"\n⏳ Calling GPT-4o to generate SQL...")
                start_time = datetime.now()
                
                candidates = await builder.generate_sql(context)
                
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"✅ Generated in {elapsed:.2f}s")
                
                if not candidates:
                    print("   ❌ No SQL generated")
                    f.write("### ❌ Error:\nNo SQL candidates generated\n\n---\n\n")
                    continue
                
                sql, params = candidates[0]
                
                # Validate
                is_valid, error = validate_sql(sql, params)
                
                if not is_valid:
                    print(f"   ❌ Invalid SQL: {error}")
                    f.write(f"### ❌ Validation Error:\n```\n{error}\n```\n\n")
                    f.write(f"### Generated SQL:\n```sql\n{sql}\n```\n\n---\n\n")
                    results.append({"test": question, "status": "INVALID", "error": error})
                    continue
                
                print(f"   ✅ SQL validated")
                
                # Execute
                print(f"\n⏳ Executing query...")
                data = await db_pool.execute_query(sql, params)
                
                print(f"✅ Got {len(data)} rows")
                
                # Write to file
                f.write(f"### ✅ Success\n\n")
                f.write(f"**Generation Time:** {elapsed:.2f}s\n\n")
                f.write(f"### 🤖 GPT-4o Generated SQL:\n\n")
                f.write(f"```sql\n{sql}\n```\n\n")
                f.write(f"**Parameters:** `{params}`\n\n")
                
                if data and len(data) > 0:
                    f.write(f"### 📊 Results ({len(data)} rows):\n\n")
                    
                    # Show first row
                    headers = list(data[0].keys())
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                    
                    for row in data[:5]:
                        values = []
                        for h in headers:
                            val = row.get(h, '')
                            if isinstance(val, (int, float)):
                                if abs(val) >= 1:
                                    values.append(f"{val:,.2f}")
                                else:
                                    values.append(f"{val:.4f}")
                            else:
                                values.append(str(val))
                        f.write("| " + " | ".join(values) + " |\n")
                    
                    if len(data) > 5:
                        f.write(f"\n*... and {len(data) - 5} more rows*\n")
                    f.write("\n")
                
                f.write("---\n\n")
                
                results.append({
                    "test": question,
                    "status": "SUCCESS",
                    "time": elapsed,
                    "rows": len(data)
                })
                
                print(f"✅ TEST PASSED\n")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}\n")
                f.write(f"### ❌ Error:\n```\n{str(e)}\n```\n\n---\n\n")
                results.append({"test": question, "status": "ERROR", "error": str(e)})
        
        # Summary
        success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
        total = len(results)
        
        f.write(f"\n## 📊 Summary\n\n")
        f.write(f"- **Total Tests:** {total}\n")
        f.write(f"- **Successful:** {success_count} ({success_count/total*100:.1f}%)\n")
        f.write(f"- **Failed:** {total - success_count}\n\n")
        
        if success_count > 0:
            avg_time = sum(r.get('time', 0) for r in results if r['status'] == 'SUCCESS') / success_count
            f.write(f"- **Average Generation Time:** {avg_time:.2f}s\n")
    
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"\nTotal Tests: {total}")
    print(f"✅ Successful: {success_count} ({success_count/total*100:.1f}%)")
    print(f"❌ Failed: {total - success_count}")
    
    if success_count > 0:
        avg_time = sum(r.get('time', 0) for r in results if r['status'] == 'SUCCESS') / success_count
        print(f"⏱️  Average Time: {avg_time:.2f}s")
    
    print(f"\n✅ Results saved to:")
    print(f"   {output_file}")
    print(f"{'='*80}\n")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_llm_generation())
