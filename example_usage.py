"""
Example usage of the CFO Assistant Agent.
Demonstrates various query types and capabilities.
"""

from cfo_assistant import CFOAssistant
from database import SupabaseConnector
import pandas as pd

def main():
    print("=" * 80)
    print("CFO ASSISTANT AGENT - Example Usage")
    print("=" * 80)
    print()
    
    # Initialize the CFO Assistant
    print("🚀 Initializing CFO Assistant...")
    try:
        cfo = CFOAssistant(verbose=False)
        print("✅ CFO Assistant initialized successfully!")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test database connection
    print("🔌 Testing database connection...")
    if cfo.db_connector.test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        return
    print()
    
    # Example queries to demonstrate capabilities
    example_queries = [
        {
            "name": "Revenue Comparison",
            "query": "Compare Apple's revenue growth and stock return since 2020"
        },
        {
            "name": "Macro Analysis",
            "query": "Show GDP and CPI trends alongside Meta's operating margin"
        },
        {
            "name": "Event Impact",
            "query": "Which quarters were most impacted by COVID-19 for Amazon?"
        },
        {
            "name": "Ratio Analysis",
            "query": "Visualize debt-to-equity ratios across all companies for 2023"
        },
        {
            "name": "Correlation Analysis",
            "query": "Plot Apple's ROE vs. Fed Funds rate over time"
        }
    ]
    
    # Run first example query
    example = example_queries[0]
    print(f"\n{'=' * 80}")
    print(f"EXAMPLE: {example['name']}")
    print(f"{'=' * 80}")
    print(f"Query: {example['query']}")
    print()
    
    try:
        # Analyze the query
        result = cfo.analyze(example['query'])
        
        if result['status'] == 'success':
            print("✅ Analysis completed successfully!")
            print()
            
            # Display executive summary
            print("📋 EXECUTIVE SUMMARY:")
            print("-" * 80)
            print(result['summary'])
            print()
            
            # Display data info
            if result['data'] is not None and not result['data'].empty:
                print("📊 DATA:")
                print("-" * 80)
                print(f"Rows: {len(result['data'])}")
                print(f"Columns: {', '.join(result['data'].columns.tolist())}")
                print()
                print("Sample data:")
                print(result['data'].head())
                print()
            
            # Display CFO narrative
            print("💼 CFO NARRATIVE:")
            print("-" * 80)
            print(result['narrative'])
            print()
            
            # Visualization info
            if result['visualization']:
                print("📈 VISUALIZATION: Chart generated successfully")
                # In a real scenario, you would save or display the chart
                # result['visualization'].write_html(f"chart.html")
            else:
                print("⚠️  No visualization generated")
        
        else:
            print(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    
    # Demonstrate direct database queries
    print(f"\n{'=' * 80}")
    print("DIRECT DATABASE QUERIES")
    print(f"{'=' * 80}")
    print()
    
    # List available metrics
    print("📚 Available Metrics (first 10):")
    print("-" * 80)
    metrics = cfo.list_available_metrics()
    if not metrics.empty:
        print(metrics.head(10))
    print()
    
    # Get company summary
    print("🏢 Company Summary Example (Apple, 2023):")
    print("-" * 80)
    apple_data = cfo.get_company_summary('Apple', 2023, 1, 2023, 4)
    if not apple_data.empty:
        print(apple_data.head())
    else:
        print("No data available")
    print()
    
    print("=" * 80)
    print("✅ Example completed!")
    print("=" * 80)
    print()
    print("To try more examples, run the Streamlit dashboard:")
    print("  streamlit run app.py")


if __name__ == "__main__":
    main()
