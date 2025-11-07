"""
End-to-End User Output Test
Shows how answers will be displayed to users in the interface
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from graph import create_graph
from dotenv import load_dotenv

load_dotenv()

# Test queries with expected user-facing outputs
TEST_QUERIES = [
    # Basic Financial
    "Show Apple's revenue for Q2 2023",
    "What was Microsoft's net income in Q1 2023?",
    
    # Multiple Metrics
    "Show Apple's revenue, net income, and EPS for Q2 2023",
    "Get Microsoft's revenue, operating income, and gross profit Q1 2023",
    
    # Ratios
    "What is Apple's gross margin for Q2 2023?",
    "Show Microsoft's ROE for Q1 2023",
    
    # Growth
    "Show Apple's revenue growth YoY for Q2 2023",
    
    # Stock
    "What is Apple's stock price for Q2 2023?",
    
    # Macro Context
    "Show Apple's revenue with GDP for Q2 2023",
    
    # Complex
    "Show Apple's revenue, margins, and stock price for Q2 2023",
]


async def test_user_outputs():
    """Test end-to-end with user-facing outputs"""
    
    print("="*80)
    print("🎯 END-TO-END USER OUTPUT TEST")
    print("="*80)
    print("\nShowing how answers will be displayed to users in the interface\n")
    
    # Create graph
    graph = create_graph()
    
    # Output file
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"user_outputs_{timestamp}.md"
    
    results = []
    
    with open(output_file, 'w') as f:
        f.write("# 🎯 USER-FACING OUTPUT EXAMPLES\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This shows how answers will be displayed to users in the Streamlit interface.\n\n")
        f.write("---\n\n")
        
        for i, question in enumerate(TEST_QUERIES, 1):
            print(f"\n{'='*80}")
            print(f"Test {i}/{len(TEST_QUERIES)}")
            print(f"{'='*80}")
            print(f"\n💬 USER QUESTION:")
            print(f"   {question}")
            
            f.write(f"## Query {i}: {question}\n\n")
            f.write(f"### 💬 User Question:\n")
            f.write(f"> {question}\n\n")
            
            try:
                # Run the query
                print(f"\n⏳ Processing...")
                
                result = await graph.ainvoke({
                    "question": question,
                    "mode": "structured"  # SQL mode
                })
                
                # Extract answer
                answer = result.get('answer', 'No answer generated')
                sql_used = result.get('sql', 'No SQL')
                data = result.get('data', [])
                
                # Display to console
                print(f"\n✅ ANSWER:")
                print("─" * 80)
                print(answer)
                print("─" * 80)
                
                if data:
                    print(f"\n📊 DATA ({len(data)} rows):")
                    for row in data[:3]:  # Show first 3 rows
                        print(f"   {row}")
                    if len(data) > 3:
                        print(f"   ... and {len(data) - 3} more rows")
                
                # Write to file
                f.write(f"### 🤖 Assistant Answer:\n\n")
                f.write(f"{answer}\n\n")
                
                if data:
                    f.write(f"### 📊 Data Table:\n\n")
                    if data:
                        # Create markdown table
                        headers = list(data[0].keys())
                        f.write("| " + " | ".join(headers) + " |\n")
                        f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                        
                        for row in data[:10]:  # Show first 10 rows
                            values = [str(row.get(h, '')) for h in headers]
                            f.write("| " + " | ".join(values) + " |\n")
                        
                        if len(data) > 10:
                            f.write(f"\n*... and {len(data) - 10} more rows*\n")
                    f.write("\n")
                
                f.write(f"### 🔍 SQL Query Used:\n\n")
                f.write(f"```sql\n{sql_used}\n```\n\n")
                f.write("---\n\n")
                
                results.append({
                    "question": question,
                    "success": True,
                    "answer": answer,
                    "rows": len(data)
                })
                
                print(f"\n✅ SUCCESS")
                
            except Exception as e:
                print(f"\n❌ ERROR: {str(e)}")
                
                f.write(f"### ❌ Error:\n\n")
                f.write(f"```\n{str(e)}\n```\n\n")
                f.write("---\n\n")
                
                results.append({
                    "question": question,
                    "success": False,
                    "error": str(e)
                })
        
        # Summary
        f.write("\n## 📊 Summary\n\n")
        f.write(f"- **Total Queries:** {len(TEST_QUERIES)}\n")
        f.write(f"- **Successful:** {sum(1 for r in results if r['success'])}\n")
        f.write(f"- **Failed:** {sum(1 for r in results if not r['success'])}\n")
    
    print(f"\n\n{'='*80}")
    print("📊 SUMMARY")
    print(f"{'='*80}")
    print(f"\nTotal Queries: {len(TEST_QUERIES)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    
    print(f"\n✅ User-facing outputs saved to:")
    print(f"   {output_file}")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_user_outputs())
