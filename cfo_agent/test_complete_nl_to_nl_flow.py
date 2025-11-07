"""
Complete NL-to-NL Flow Test
Tests the entire pipeline: Natural Language → SQL → Execute → Format → Natural Language
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from generative_sql import GenerativeSQLBuilder
from db.whitelist import validate_sql, load_schema_cache
from db.pool import db_pool
from formatter import ResponseFormatter
from dotenv import load_dotenv

load_dotenv()

# Comprehensive test queries covering all combinations
TEST_QUERIES = [
    # CATEGORY 1: BASIC SINGLE METRICS
    {"q": "Show Apple's revenue for Q2 2023", "cat": "Basic - Revenue"},
    {"q": "What was Microsoft's net income in Q1 2023?", "cat": "Basic - Net Income"},
    {"q": "Get Google's operating income for Q3 2023", "cat": "Basic - Operating Income"},
    {"q": "Show Amazon's gross profit Q4 2023", "cat": "Basic - Gross Profit"},
    {"q": "What is Meta's EPS for Q2 2023?", "cat": "Basic - EPS"},
    
    # CATEGORY 2: MULTIPLE METRICS
    {"q": "Show Apple's revenue and net income for Q2 2023", "cat": "Multi - 2 Metrics"},
    {"q": "Get Microsoft's revenue, operating income, and gross profit Q1 2023", "cat": "Multi - 3 Metrics"},
    {"q": "Show Google's revenue, net income, and EPS Q3 2023", "cat": "Multi - 3 Metrics"},
    {"q": "Show Apple's revenue, net income, gross margin, and stock price Q2 2023", "cat": "Multi - 4 Metrics"},
    
    # CATEGORY 3: FINANCIAL RATIOS
    {"q": "What is Apple's gross margin for Q2 2023?", "cat": "Ratio - Gross Margin"},
    {"q": "Show Microsoft's operating margin Q1 2023", "cat": "Ratio - Operating Margin"},
    {"q": "Get Google's net margin for Q3 2023", "cat": "Ratio - Net Margin"},
    {"q": "What is Amazon's ROE in Q4 2023?", "cat": "Ratio - ROE"},
    {"q": "Show Meta's ROA for Q2 2023", "cat": "Ratio - ROA"},
    {"q": "Get Apple's debt-to-equity ratio Q2 2023", "cat": "Ratio - Debt Ratio"},
    
    # CATEGORY 4: GROWTH METRICS
    {"q": "Show Apple's revenue growth YoY for Q2 2023", "cat": "Growth - YoY"},
    {"q": "What is Microsoft's QoQ revenue growth in Q1 2023?", "cat": "Growth - QoQ"},
    {"q": "Get Google's margin growth YoY Q3 2023", "cat": "Growth - Margin YoY"},
    
    # CATEGORY 5: STOCK MARKET DATA
    {"q": "What is Apple's stock price for Q2 2023?", "cat": "Stock - Price"},
    {"q": "Show Microsoft's stock returns Q1 2023", "cat": "Stock - Returns"},
    {"q": "Get Google's stock volatility for Q3 2023", "cat": "Stock - Volatility"},
    
    # CATEGORY 6: MACRO ECONOMIC CONTEXT
    {"q": "Show Apple's revenue with GDP for Q2 2023", "cat": "Macro - GDP"},
    {"q": "Get Microsoft's margins with CPI context Q1 2023", "cat": "Macro - CPI"},
    {"q": "Show Google's performance with unemployment rate Q3 2023", "cat": "Macro - Unemployment"},
    
    # CATEGORY 7: TIME SERIES
    {"q": "Show Apple's revenue for the last 4 quarters", "cat": "Time Series - 4Q"},
    {"q": "Get Microsoft's margins over the last 2 years", "cat": "Time Series - 2Y"},
    {"q": "Show Google's stock price trend for 2023", "cat": "Time Series - Year"},
    
    # CATEGORY 8: ANNUAL DATA
    {"q": "Show Apple's annual revenue for 2023", "cat": "Annual - Revenue"},
    {"q": "Get Microsoft's annual margins for 2023", "cat": "Annual - Margins"},
    {"q": "What is Google's annual ROE for 2023?", "cat": "Annual - ROE"},
    
    # CATEGORY 9: LATEST PERIOD
    {"q": "Show Apple's latest quarter results", "cat": "Latest - All Metrics"},
    {"q": "Get Microsoft's most recent financial data", "cat": "Latest - Financials"},
    {"q": "What is Google's current quarter performance?", "cat": "Latest - Performance"},
    
    # CATEGORY 10: SPECIFIC EXPENSES
    {"q": "Show Apple's R&D expenses for Q2 2023", "cat": "Expenses - R&D"},
    {"q": "Get Microsoft's SG&A expenses Q1 2023", "cat": "Expenses - SG&A"},
    {"q": "Show Amazon's R&D and SG&A expenses Q4 2023", "cat": "Expenses - Multiple"},
    
    # CATEGORY 11: CASH FLOW
    {"q": "Show Apple's operating cash flow Q2 2023", "cat": "Cash Flow - Operating"},
    {"q": "Get Microsoft's capex for Q1 2023", "cat": "Cash Flow - Capex"},
    
    # CATEGORY 12: BALANCE SHEET
    {"q": "Show Apple's total assets Q2 2023", "cat": "Balance Sheet - Assets"},
    {"q": "Get Microsoft's total liabilities Q1 2023", "cat": "Balance Sheet - Liabilities"},
    {"q": "What is Google's equity for Q3 2023?", "cat": "Balance Sheet - Equity"},
    
    # CATEGORY 13: COMPLEX MULTI-METRIC
    {"q": "Show Apple's revenue, operating income, R&D, stock price, and volatility Q2 2023", "cat": "Complex - 5 Metrics"},
    {"q": "Get Microsoft's complete financial snapshot Q1 2023", "cat": "Complex - Snapshot"},
    
    # CATEGORY 14: PEER COMPARISON
    {"q": "Compare Apple and Microsoft revenue Q2 2023", "cat": "Comparison - 2 Companies"},
    {"q": "Compare gross margins for Apple, Microsoft, and Google Q2 2023", "cat": "Comparison - 3 Companies"},
    
    # CATEGORY 15: DIFFERENT TIME PERIODS
    {"q": "Show Apple's revenue for Q1 2024", "cat": "Period - Q1 2024"},
    {"q": "Show Apple's revenue for Q3 2024", "cat": "Period - Q3 2024"},
    {"q": "Show Apple's revenue for Q4 2024", "cat": "Period - Q4 2024"},
]


def format_user_answer(question: str, data: list, category: str) -> str:
    """Format data into user-friendly answer"""
    if not data:
        return "No data found for this query."
    
    # Extract key information
    row = data[0]
    
    # Build answer based on category
    if "Basic" in category or "Ratio" in category or "Stock" in category:
        # Single metric answer
        metric_keys = [k for k in row.keys() if k not in ['ticker', 'fiscal_year', 'fiscal_quarter', 'name', 'company_id', 'peer_group_id']]
        if metric_keys:
            metric = metric_keys[0]
            value = row[metric]
            ticker = row.get('ticker', 'Company')
            fy = row.get('fiscal_year', '')
            fq = row.get('fiscal_quarter', '')
            
            if isinstance(value, (int, float)):
                if abs(value) >= 1:
                    formatted_val = f"${value:,.2f}B" if 'b' in metric.lower() else f"{value:,.2f}"
                else:
                    formatted_val = f"{value*100:.2f}%" if 'margin' in metric or 'pct' in metric or 'roe' in metric or 'roa' in metric else f"{value:.4f}"
            else:
                formatted_val = str(value)
            
            period = f"Q{fq} {fy}" if fq else f"{fy}"
            return f"**{ticker}** - {period}\n\n{metric.replace('_', ' ').title()}: **{formatted_val}**"
    
    elif "Multi" in category or "Complex" in category:
        # Multiple metrics answer
        ticker = row.get('ticker', 'Company')
        fy = row.get('fiscal_year', '')
        fq = row.get('fiscal_quarter', '')
        
        period = f"Q{fq} {fy}" if fq else f"{fy}"
        answer = f"**{ticker}** - {period}\n\n"
        
        metric_keys = [k for k in row.keys() if k not in ['ticker', 'fiscal_year', 'fiscal_quarter', 'name', 'company_id', 'peer_group_id']]
        for metric in metric_keys[:10]:  # Show first 10 metrics
            value = row[metric]
            if isinstance(value, (int, float)):
                if abs(value) >= 1:
                    formatted_val = f"${value:,.2f}B" if 'b' in metric.lower() else f"{value:,.2f}"
                else:
                    formatted_val = f"{value*100:.2f}%" if 'margin' in metric or 'pct' in metric or 'roe' in metric or 'roa' in metric else f"{value:.4f}"
            else:
                formatted_val = str(value)
            
            answer += f"- {metric.replace('_', ' ').title()}: **{formatted_val}**\n"
        
        return answer
    
    elif "Time Series" in category or "Latest" in category:
        # Time series answer
        ticker = data[0].get('ticker', 'Company')
        answer = f"**{ticker}** - Historical Data ({len(data)} periods)\n\n"
        
        for row in data[:5]:  # Show first 5
            fy = row.get('fiscal_year', '')
            fq = row.get('fiscal_quarter', '')
            metric_keys = [k for k in row.keys() if k not in ['ticker', 'fiscal_year', 'fiscal_quarter', 'name', 'company_id']]
            
            if metric_keys:
                metric = metric_keys[0]
                value = row[metric]
                if isinstance(value, (int, float)):
                    if abs(value) >= 1:
                        formatted_val = f"${value:,.2f}B" if 'b' in metric.lower() else f"{value:,.2f}"
                    else:
                        formatted_val = f"{value*100:.2f}%" if 'margin' in metric or 'pct' in metric else f"{value:.4f}"
                else:
                    formatted_val = str(value)
                
                period = f"Q{fq} {fy}" if fq else f"{fy}"
                answer += f"- {period}: **{formatted_val}**\n"
        
        if len(data) > 5:
            answer += f"\n*... and {len(data) - 5} more periods*"
        
        return answer
    
    elif "Comparison" in category:
        # Peer comparison answer
        answer = "**Company Comparison**\n\n"
        
        for row in data:
            ticker = row.get('ticker', 'Company')
            metric_keys = [k for k in row.keys() if k not in ['ticker', 'fiscal_year', 'fiscal_quarter', 'name', 'company_id', 'peer_group_id']]
            
            if metric_keys:
                metric = metric_keys[0]
                value = row[metric]
                if isinstance(value, (int, float)):
                    if abs(value) >= 1:
                        formatted_val = f"${value:,.2f}B" if 'b' in metric.lower() else f"{value:,.2f}"
                    else:
                        formatted_val = f"{value*100:.2f}%" if 'margin' in metric or 'pct' in metric else f"{value:.4f}"
                else:
                    formatted_val = str(value)
                
                answer += f"- **{ticker}**: {formatted_val}\n"
        
        return answer
    
    else:
        # Generic answer
        ticker = row.get('ticker', 'Company')
        fy = row.get('fiscal_year', '')
        fq = row.get('fiscal_quarter', '')
        
        period = f"Q{fq} {fy}" if fq else f"{fy}"
        answer = f"**{ticker}** - {period}\n\n"
        
        metric_keys = [k for k in row.keys() if k not in ['ticker', 'fiscal_year', 'fiscal_quarter', 'name', 'company_id']]
        for metric in metric_keys[:5]:  # Show first 5 metrics
            value = row[metric]
            if isinstance(value, (int, float)):
                if abs(value) >= 1:
                    formatted_val = f"${value:,.2f}B" if 'b' in metric.lower() else f"{value:,.2f}"
                else:
                    formatted_val = f"{value*100:.2f}%" if 'margin' in metric or 'pct' in metric else f"{value:.4f}"
            else:
                formatted_val = str(value)
            
            answer += f"- {metric.replace('_', ' ').title()}: **{formatted_val}**\n"
        
        return answer


async def test_complete_flow():
    """Test complete NL-to-NL flow"""
    
    print("="*80)
    print("🔄 COMPLETE NL-TO-NL FLOW TEST")
    print("="*80)
    print("\nTesting: Natural Language → SQL → Execute → Format → Natural Language\n")
    
    # Load schema
    try:
        await load_schema_cache()
        print("✅ Schema loaded\n")
    except Exception as e:
        print(f"⚠️  Warning: {e}\n")
    
    builder = GenerativeSQLBuilder()
    
    # Output file
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"complete_nl_to_nl_{timestamp}.md"
    
    results = []
    success_count = 0
    
    with open(output_file, 'w') as f:
        f.write("# 🔄 COMPLETE NL-TO-NL FLOW TEST RESULTS\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Queries:** {len(TEST_QUERIES)}\n")
        f.write(f"**Flow:** Natural Language → SQL → Execute → Format → Natural Language\n\n")
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
                # STEP 1: Generate SQL
                context = {
                    "intent": question,
                    "surfaces": ["vw_company_complete_quarter"],
                    "entities_resolved": {},
                    "params": {"limit": 10}
                }
                
                print(f"\n⏳ Step 1: Generating SQL with GPT-4o...")
                candidates = await builder.generate_sql(context)
                
                if not candidates:
                    print("   ❌ No SQL generated")
                    f.write("### ❌ Error:\nNo SQL generated\n\n---\n\n")
                    continue
                
                sql, params = candidates[0]
                print(f"   ✅ SQL generated")
                
                # STEP 2: Validate SQL
                is_valid, error = validate_sql(sql, params)
                if not is_valid:
                    print(f"   ❌ Invalid SQL: {error}")
                    f.write(f"### ❌ Validation Error:\n```\n{error}\n```\n\n---\n\n")
                    continue
                
                print(f"   ✅ SQL validated")
                
                # STEP 3: Execute SQL
                print(f"\n⏳ Step 2: Executing SQL query...")
                data = await db_pool.execute_query(sql, params)
                print(f"   ✅ Got {len(data)} rows")
                
                # STEP 4: Format to Natural Language
                print(f"\n⏳ Step 3: Formatting to natural language...")
                answer = format_user_answer(question, data, category)
                print(f"   ✅ Answer formatted")
                
                # Display result
                print(f"\n🤖 FINAL ANSWER:")
                print("─" * 80)
                print(answer)
                print("─" * 80)
                
                # Write to file
                f.write(f"### ✅ Success\n\n")
                f.write(f"#### 🤖 Assistant Answer:\n\n")
                f.write(f"{answer}\n\n")
                
                # Data table
                if data and len(data) > 0:
                    f.write(f"#### 📊 Raw Data ({len(data)} rows):\n\n")
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
                
                # SQL used
                f.write(f"<details>\n")
                f.write(f"<summary>🔍 Technical Details (SQL Query)</summary>\n\n")
                f.write(f"```sql\n{sql}\n```\n\n")
                f.write(f"**Parameters:** `{params}`\n\n")
                f.write(f"</details>\n\n")
                f.write("---\n\n")
                
                success_count += 1
                results.append({"question": question, "category": category, "status": "SUCCESS"})
                
                print(f"\n✅ TEST PASSED\n")
                
            except Exception as e:
                print(f"\n❌ ERROR: {str(e)}\n")
                f.write(f"### ❌ Error:\n```\n{str(e)}\n```\n\n---\n\n")
                results.append({"question": question, "category": category, "status": "FAILED", "error": str(e)})
        
        # Summary
        f.write(f"\n## 📊 Summary\n\n")
        f.write(f"- **Total Tests:** {len(TEST_QUERIES)}\n")
        f.write(f"- **Successful:** {success_count} ({success_count/len(TEST_QUERIES)*100:.1f}%)\n")
        f.write(f"- **Failed:** {len(TEST_QUERIES) - success_count}\n")
    
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"\nTotal Tests: {len(TEST_QUERIES)}")
    print(f"✅ Successful: {success_count} ({success_count/len(TEST_QUERIES)*100:.1f}%)")
    print(f"❌ Failed: {len(TEST_QUERIES) - success_count}")
    
    print(f"\n✅ Results saved to:")
    print(f"   {output_file}")
    print(f"{'='*80}\n")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_complete_flow())
