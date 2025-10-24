"""
Comprehensive test for all financial attributes - Annual and Quarterly
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_all_attributes():
    """Test all financial attributes for both annual and quarterly queries"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("COMPREHENSIVE ATTRIBUTE TEST - ANNUAL & QUARTERLY")
    print("="*100)
    
    # Define all attributes from the image
    attributes = [
        ("revenue", "apple revenue for 2023", "apple revenue for Q2 2023"),
        ("operating_income", "apple operating income for 2023", "apple operating income for Q2 2023"),
        ("net_income", "apple net income for 2023", "apple net income for Q2 2023"),
        ("eps", "apple EPS for 2023", "apple EPS for Q2 2023"),
        ("total_assets", "apple total assets for 2023", "apple total assets for Q2 2023"),
        ("total_liabilities", "apple total liabilities for 2023", "apple total liabilities for Q2 2023"),
        ("equity", "apple equity for 2023", "apple equity for Q2 2023"),
        ("cash_flow_ops", "apple operating cash flow for 2023", "apple operating cash flow for Q2 2023"),
        ("cash_flow_investing", "apple investing cash flow for 2023", "apple investing cash flow for Q2 2023"),
        ("cash_flow_financing", "apple financing cash flow for 2023", "apple financing cash flow for Q2 2023"),
        ("cogs", "apple COGS for 2023", "apple COGS for Q2 2023"),
        ("gross_profit", "apple gross profit for 2023", "apple gross profit for Q2 2023"),
        ("r_and_d_expenses", "apple R&D expenses for 2023", "apple R&D expenses for Q2 2023"),
        ("sg_and_a_expenses", "apple SG&A expenses for 2023", "apple SG&A expenses for Q2 2023"),
        ("ebit", "apple EBIT for 2023", "apple EBIT for Q2 2023"),
        ("ebitda", "apple EBITDA for 2023", "apple EBITDA for Q2 2023"),
        ("capex", "apple capex for 2023", "apple capex for Q2 2023"),
        ("dividends", "apple dividends for 2023", "apple dividends for Q2 2023"),
        ("buybacks", "apple buybacks for 2023", "apple buybacks for Q2 2023"),
    ]
    
    results = []
    
    for attr_name, annual_query, quarterly_query in attributes:
        print(f"\n{'='*100}")
        print(f"TESTING: {attr_name.upper()}")
        print(f"{'='*100}")
        
        # Test Annual
        print(f"\n📅 ANNUAL TEST:")
        print(f"Query: '{annual_query}'")
        print("-"*100)
        try:
            annual_result = await cfo_agent_graph.run(annual_query)
            
            # Check if it's a single metric response (not showing everything)
            metric_count = sum([
                'revenue' in annual_result.lower() and 'revenue' in attr_name.lower(),
                'operating income' in annual_result.lower() and 'operating' in attr_name.lower(),
                'net income' in annual_result.lower() and 'net' in attr_name.lower(),
                'R&D' in annual_result and 'r_and_d' in attr_name,
                'SG&A' in annual_result and 'sg_and_a' in attr_name,
                'COGS' in annual_result and 'cogs' in attr_name,
            ])
            
            if "No data" in annual_result or "No results" in annual_result:
                annual_status = "❌ NO DATA"
                print(f"{annual_status}")
            else:
                annual_status = "✅ SUCCESS"
                # Show first 150 chars
                preview = annual_result.split('\n')[0][:150]
                print(f"{annual_status}")
                print(f"Response: {preview}...")
        except Exception as e:
            annual_status = f"❌ ERROR: {str(e)[:50]}"
            print(f"{annual_status}")
        
        # Test Quarterly
        print(f"\n📊 QUARTERLY TEST:")
        print(f"Query: '{quarterly_query}'")
        print("-"*100)
        try:
            quarterly_result = await cfo_agent_graph.run(quarterly_query)
            
            if "No data" in quarterly_result or "No results" in quarterly_result:
                quarterly_status = "❌ NO DATA"
                print(f"{quarterly_status}")
            else:
                quarterly_status = "✅ SUCCESS"
                # Show first 150 chars
                preview = quarterly_result.split('\n')[0][:150]
                print(f"{quarterly_status}")
                print(f"Response: {preview}...")
        except Exception as e:
            quarterly_status = f"❌ ERROR: {str(e)[:50]}"
            print(f"{quarterly_status}")
        
        # Store results
        results.append({
            'attribute': attr_name,
            'annual': annual_status,
            'quarterly': quarterly_status
        })
    
    # Summary Report
    print("\n" + "="*100)
    print("SUMMARY REPORT")
    print("="*100)
    print(f"\n{'Attribute':<25} {'Annual':<20} {'Quarterly':<20}")
    print("-"*100)
    
    annual_success = 0
    quarterly_success = 0
    
    for r in results:
        annual_icon = "✅" if "SUCCESS" in r['annual'] else "❌"
        quarterly_icon = "✅" if "SUCCESS" in r['quarterly'] else "❌"
        
        print(f"{r['attribute']:<25} {annual_icon} {r['annual'][:15]:<18} {quarterly_icon} {r['quarterly'][:15]:<18}")
        
        if "SUCCESS" in r['annual']:
            annual_success += 1
        if "SUCCESS" in r['quarterly']:
            quarterly_success += 1
    
    print("\n" + "="*100)
    print(f"ANNUAL QUERIES:    {annual_success}/{len(results)} passed ({annual_success/len(results)*100:.1f}%)")
    print(f"QUARTERLY QUERIES: {quarterly_success}/{len(results)} passed ({quarterly_success/len(results)*100:.1f}%)")
    print(f"TOTAL:             {annual_success + quarterly_success}/{len(results)*2} passed ({(annual_success + quarterly_success)/(len(results)*2)*100:.1f}%)")
    print("="*100)
    
    await db_pool.close()
    
    return results


if __name__ == "__main__":
    results = asyncio.run(test_all_attributes())
