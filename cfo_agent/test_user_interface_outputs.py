"""
User Interface Output Test
Shows how answers will be displayed to users
Simulates the complete flow with formatted outputs
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

from generative_sql import GenerativeSQLBuilder
from db.whitelist import validate_sql, load_schema_cache
from db.pool import db_pool
from formatter import ResponseFormatter
from dotenv import load_dotenv

load_dotenv()

# Test queries
TEST_QUERIES = [
    {"q": "Show Apple's revenue for Q2 2023", "cat": "Basic Financial"},
    {"q": "What was Microsoft's net income in Q1 2023?", "cat": "Basic Financial"},
    {"q": "Show Apple's revenue, net income, and EPS for Q2 2023", "cat": "Multiple Metrics"},
    {"q": "What is Apple's gross margin for Q2 2023?", "cat": "Ratios"},
    {"q": "Show Apple's revenue growth YoY for Q2 2023", "cat": "Growth"},
    {"q": "What is Apple's stock price for Q2 2023?", "cat": "Stock"},
    {"q": "Show Apple's revenue with GDP for Q2 2023", "cat": "Macro Context"},
    {"q": "Show Apple's revenue, margins, and stock price for Q2 2023", "cat": "Complex"},
    {"q": "Compare Apple and Microsoft revenue Q2 2023", "cat": "Peer Comparison"},
    {"q": "Show Apple's revenue for the last 4 quarters", "cat": "Time Series"},
]


async def execute_query(sql: str, params: dict):
    """Execute SQL and return results"""
    try:
        results = await db_pool.execute_query(sql, params)
        return results
    except Exception as e:
        return {"error": str(e)}


def format_user_answer(question: str, data: list, category: str) -> str:
    """Format data into user-friendly answer"""
    if not data:
        return "No data found for this query."
    
    # Extract key information
    row = data[0]
    
    # Build answer based on category
    if category == "Basic Financial":
        # Single metric answer
        metric_keys = [k for k in row.keys() if k not in ['ticker', 'fiscal_year', 'fiscal_quarter', 'name', 'company_id']]
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
                    formatted_val = f"{value*100:.2f}%" if 'margin' in metric or 'pct' in metric else f"{value:.4f}"
            else:
                formatted_val = str(value)
            
            return f"**{ticker}** - Q{fq} {fy}\n\n{metric.replace('_', ' ').title()}: **{formatted_val}**"
    
    elif category == "Multiple Metrics":
        # Multiple metrics answer
        ticker = row.get('ticker', 'Company')
        fy = row.get('fiscal_year', '')
        fq = row.get('fiscal_quarter', '')
        
        answer = f"**{ticker}** - Q{fq} {fy}\n\n"
        
        metric_keys = [k for k in row.keys() if k not in ['ticker', 'fiscal_year', 'fiscal_quarter', 'name', 'company_id']]
        for metric in metric_keys:
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
    
    elif category == "Time Series":
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
                
                answer += f"- Q{fq} {fy}: **{formatted_val}**\n"
        
        if len(data) > 5:
            answer += f"\n*... and {len(data) - 5} more periods*"
        
        return answer
    
    elif category == "Peer Comparison":
        # Peer comparison answer
        answer = "**Company Comparison**\n\n"
        
        for row in data:
            ticker = row.get('ticker', 'Company')
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
                
                answer += f"- **{ticker}**: {formatted_val}\n"
        
        return answer
    
    else:
        # Generic answer
        ticker = row.get('ticker', 'Company')
        fy = row.get('fiscal_year', '')
        fq = row.get('fiscal_quarter', '')
        
        answer = f"**{ticker}**"
        if fq:
            answer += f" - Q{fq} {fy}"
        answer += "\n\n"
        
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


async def test_user_interface():
    """Test with user-facing outputs"""
    
    print("="*80)
    print("🎯 USER INTERFACE OUTPUT TEST")
    print("="*80)
    print("\nShowing how answers will be displayed in the Streamlit interface\n")
    
    # Load schema
    try:
        await load_schema_cache()
    except:
        pass
    
    builder = GenerativeSQLBuilder()
    formatter = ResponseFormatter()
    
    # Output file
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"user_interface_outputs_{timestamp}.md"
    
    with open(output_file, 'w') as f:
        f.write("# 🎯 USER INTERFACE OUTPUT EXAMPLES\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This shows exactly how answers will appear to users in the Streamlit interface.\n\n")
        f.write("---\n\n")
        
        for i, test in enumerate(TEST_QUERIES, 1):
            question = test['q']
            category = test['cat']
            
            print(f"\n{'='*80}")
            print(f"Test {i}/{len(TEST_QUERIES)}: {category}")
            print(f"{'='*80}")
            print(f"\n💬 USER ASKS:")
            print(f"   \"{question}\"")
            
            f.write(f"## Example {i}: {category}\n\n")
            f.write(f"### 💬 User Question:\n")
            f.write(f"> {question}\n\n")
            
            try:
                # Generate SQL
                context = {
                    "intent": question,
                    "surfaces": ["vw_company_complete_quarter"],
                    "entities_resolved": {},
                    "params": {"limit": 10}
                }
                
                candidates = await builder.generate_sql(context)
                
                if not candidates:
                    print("   ❌ No SQL generated")
                    continue
                
                sql, params = candidates[0]
                is_valid, error = validate_sql(sql, params)
                
                if not is_valid:
                    print(f"   ❌ Invalid SQL: {error}")
                    continue
                
                # Execute SQL
                print(f"\n⏳ Executing query...")
                data = await execute_query(sql, params)
                
                if isinstance(data, dict) and 'error' in data:
                    print(f"   ❌ Execution error: {data['error']}")
                    f.write(f"### ❌ Error:\n```\n{data['error']}\n```\n\n")
                    continue
                
                # Format response
                print(f"\n✅ Got {len(data)} rows")
                
                # Create user-facing answer (simple formatting)
                answer = format_user_answer(question, data, category)
                
                # Display to console
                print(f"\n🤖 ASSISTANT ANSWER:")
                print("─" * 80)
                print(answer)
                print("─" * 80)
                
                # Write to file - User-facing format
                f.write(f"### 🤖 Assistant Response:\n\n")
                f.write(f"{answer}\n\n")
                
                # Data table
                if data and len(data) > 0:
                    f.write(f"### 📊 Data Table ({len(data)} rows):\n\n")
                    
                    # Create markdown table
                    headers = list(data[0].keys())
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                    
                    for row in data[:10]:  # Show first 10
                        values = []
                        for h in headers:
                            val = row.get(h, '')
                            # Format numbers nicely
                            if isinstance(val, (int, float)):
                                if abs(val) >= 1:
                                    values.append(f"{val:,.2f}")
                                else:
                                    values.append(f"{val:.4f}")
                            else:
                                values.append(str(val))
                        f.write("| " + " | ".join(values) + " |\n")
                    
                    if len(data) > 10:
                        f.write(f"\n*... and {len(data) - 10} more rows*\n")
                    f.write("\n")
                
                # Technical details (collapsible)
                f.write(f"<details>\n")
                f.write(f"<summary>🔍 Technical Details (SQL Query)</summary>\n\n")
                f.write(f"```sql\n{sql}\n```\n\n")
                f.write(f"**Parameters:** `{params}`\n\n")
                f.write(f"</details>\n\n")
                f.write("---\n\n")
                
                print(f"✅ SUCCESS\n")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}\n")
                f.write(f"### ❌ Error:\n```\n{str(e)}\n```\n\n---\n\n")
    
    print(f"\n{'='*80}")
    print(f"✅ User interface outputs saved to:")
    print(f"   {output_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(test_user_interface())
