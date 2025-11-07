"""
Comprehensive NL-to-SQL Test Suite
Tests all possible query types and saves outputs to files
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from generative_sql import GenerativeSQLBuilder
from db.whitelist import validate_sql, load_schema_cache
from dotenv import load_dotenv

load_dotenv()

# Comprehensive test queries (50+ queries covering all scenarios)
TEST_QUERIES = [
    # CATEGORY 1: BASIC FINANCIAL METRICS
    {"q": "Show Apple's revenue for Q2 2023", "cat": "Basic Financial"},
    {"q": "What was Microsoft's net income in Q1 2023?", "cat": "Basic Financial"},
    {"q": "Get Google's operating income for Q3 2023", "cat": "Basic Financial"},
    {"q": "Show Amazon's gross profit Q4 2023", "cat": "Basic Financial"},
    {"q": "What is Meta's EPS for Q2 2023?", "cat": "Basic Financial"},
    
    # CATEGORY 2: MULTIPLE METRICS
    {"q": "Show Apple's revenue, net income, and EPS for Q2 2023", "cat": "Multiple Metrics"},
    {"q": "Get Microsoft's revenue, operating income, and gross profit Q1 2023", "cat": "Multiple Metrics"},
    {"q": "Show Google's revenue, margins, and stock price Q3 2023", "cat": "Multiple Metrics"},
    
    # CATEGORY 3: FINANCIAL RATIOS
    {"q": "What is Apple's gross margin for Q2 2023?", "cat": "Ratios"},
    {"q": "Show Microsoft's operating margin Q1 2023", "cat": "Ratios"},
    {"q": "Get Google's net margin for Q3 2023", "cat": "Ratios"},
    {"q": "What is Amazon's ROE in Q4 2023?", "cat": "Ratios"},
    {"q": "Show Meta's ROA for Q2 2023", "cat": "Ratios"},
    {"q": "Get Apple's debt-to-equity ratio Q2 2023", "cat": "Ratios"},
    
    # CATEGORY 4: GROWTH METRICS
    {"q": "Show Apple's revenue growth YoY for Q2 2023", "cat": "Growth"},
    {"q": "What is Microsoft's QoQ revenue growth in Q1 2023?", "cat": "Growth"},
    {"q": "Get Google's margin growth YoY Q3 2023", "cat": "Growth"},
    {"q": "Show Apple's revenue growth for the last 4 quarters", "cat": "Growth"},
    
    # CATEGORY 5: STOCK MARKET DATA
    {"q": "What is Apple's stock price for Q2 2023?", "cat": "Stock"},
    {"q": "Show Microsoft's stock returns Q1 2023", "cat": "Stock"},
    {"q": "Get Google's stock volatility for Q3 2023", "cat": "Stock"},
    {"q": "What is Amazon's dividend yield Q4 2023?", "cat": "Stock"},
    
    # CATEGORY 6: MACRO ECONOMIC CONTEXT
    {"q": "Show Apple's revenue with GDP for Q2 2023", "cat": "Macro"},
    {"q": "Get Microsoft's margins with CPI context Q1 2023", "cat": "Macro"},
    {"q": "Show Google's performance with unemployment rate Q3 2023", "cat": "Macro"},
    {"q": "What is Amazon's revenue with interest rates Q4 2023?", "cat": "Macro"},
    
    # CATEGORY 7: SENSITIVITY ANALYSIS
    {"q": "How sensitive is Apple's margin to CPI?", "cat": "Sensitivity"},
    {"q": "Show Microsoft's margin correlation with GDP", "cat": "Sensitivity"},
    {"q": "Get Google's sensitivity to interest rates", "cat": "Sensitivity"},
    
    # CATEGORY 8: PEER COMPARISONS
    {"q": "Compare Apple and Microsoft revenue Q2 2023", "cat": "Peer Comparison"},
    {"q": "Compare gross margins for Apple, Microsoft, and Google Q2 2023", "cat": "Peer Comparison"},
    {"q": "Rank companies by ROE in Q2 2023", "cat": "Peer Comparison"},
    
    # CATEGORY 9: TIME SERIES
    {"q": "Show Apple's revenue for the last 8 quarters", "cat": "Time Series"},
    {"q": "Get Microsoft's margins over the last 2 years", "cat": "Time Series"},
    {"q": "Show Google's stock price trend for 2023", "cat": "Time Series"},
    
    # CATEGORY 10: ANNUAL DATA
    {"q": "Show Apple's annual revenue for 2023", "cat": "Annual"},
    {"q": "Get Microsoft's annual margins for 2023", "cat": "Annual"},
    {"q": "What is Google's annual ROE for 2023?", "cat": "Annual"},
    
    # CATEGORY 11: LATEST PERIOD
    {"q": "Show Apple's latest quarter results", "cat": "Latest"},
    {"q": "Get Microsoft's most recent financial data", "cat": "Latest"},
    {"q": "What is Google's current quarter performance?", "cat": "Latest"},
    
    # CATEGORY 12: SPECIFIC EXPENSES
    {"q": "Show Apple's R&D expenses for Q2 2023", "cat": "Expenses"},
    {"q": "Get Microsoft's SG&A expenses Q1 2023", "cat": "Expenses"},
    {"q": "What is Google's COGS for Q3 2023?", "cat": "Expenses"},
    {"q": "Show Amazon's R&D and SG&A expenses Q4 2023", "cat": "Expenses"},
    
    # CATEGORY 13: CASH FLOW
    {"q": "Show Apple's operating cash flow Q2 2023", "cat": "Cash Flow"},
    {"q": "Get Microsoft's capex for Q1 2023", "cat": "Cash Flow"},
    {"q": "What is Google's free cash flow Q3 2023?", "cat": "Cash Flow"},
    
    # CATEGORY 14: BALANCE SHEET
    {"q": "Show Apple's total assets Q2 2023", "cat": "Balance Sheet"},
    {"q": "Get Microsoft's total liabilities Q1 2023", "cat": "Balance Sheet"},
    {"q": "What is Google's equity for Q3 2023?", "cat": "Balance Sheet"},
    
    # CATEGORY 15: COMPLEX MULTI-METRIC
    {"q": "Show Apple's revenue, operating income, R&D, stock price, and volatility Q2 2023", "cat": "Complex"},
    {"q": "Get Microsoft's complete financial snapshot Q1 2023", "cat": "Complex"},
]


async def run_comprehensive_tests():
    """Run all tests and save outputs"""
    
    print("="*80)
    print("🧪 COMPREHENSIVE NL-TO-SQL TEST SUITE")
    print("="*80)
    
    # Load schema
    print("\n📋 Loading schema cache...")
    try:
        await load_schema_cache()
        print("✅ Schema loaded")
    except Exception as e:
        print(f"⚠️  Warning: {e}")
    
    builder = GenerativeSQLBuilder()
    
    # Results storage
    results = []
    by_category = {}
    
    print(f"\n🚀 Running {len(TEST_QUERIES)} queries...\n")
    
    for i, test in enumerate(TEST_QUERIES, 1):
        question = test['q']
        category = test['cat']
        
        print(f"[{i}/{len(TEST_QUERIES)}] {category}: {question}")
        
        # Create context from question
        context = {
            "intent": question,
            "surfaces": ["vw_company_complete_quarter"],
            "entities_resolved": {},
            "params": {"limit": 10}
        }
        
        try:
            candidates = await builder.generate_sql(context)
            
            if candidates:
                sql, params = candidates[0]
                is_valid, error = validate_sql(sql, params)
                
                result = {
                    "question": question,
                    "category": category,
                    "sql": sql,
                    "params": params,
                    "valid": is_valid,
                    "error": error if not is_valid else None
                }
                
                results.append(result)
                
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(result)
                
                status = "✅" if is_valid else "❌"
                print(f"   {status}")
            else:
                print(f"   ❌ No SQL generated")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Save results
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = output_dir / f"nl_to_sql_results_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save markdown report
    md_file = output_dir / f"nl_to_sql_report_{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write("# NL-TO-SQL COMPREHENSIVE TEST REPORT\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Queries:** {len(results)}\n")
        f.write(f"**Valid SQL:** {sum(1 for r in results if r['valid'])}\n\n")
        
        for cat, items in by_category.items():
            f.write(f"\n## {cat}\n\n")
            for item in items:
                f.write(f"### Q: {item['question']}\n\n")
                f.write(f"**Status:** {'✅ VALID' if item['valid'] else '❌ INVALID'}\n\n")
                f.write("**Generated SQL:**\n```sql\n")
                f.write(item['sql'])
                f.write("\n```\n\n")
                if item['params']:
                    f.write(f"**Parameters:** {item['params']}\n\n")
                if item['error']:
                    f.write(f"**Error:** {item['error']}\n\n")
                f.write("---\n\n")
    
    print(f"\n✅ Results saved to:")
    print(f"   - {json_file}")
    print(f"   - {md_file}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
