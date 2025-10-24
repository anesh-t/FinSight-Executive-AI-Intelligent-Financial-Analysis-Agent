"""
Test all 19 financial metrics from dim_financial_metric table
- Quarterly: should fetch from fact_financials
- Annual: should fetch from mv_financials_annual
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_all_metrics():
    """Test all 19 metrics for both quarterly and annual queries"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("TESTING ALL 19 FINANCIAL METRICS - QUARTERLY vs ANNUAL")
    print("="*120)
    
    # All 19 metrics from the image
    metrics = [
        ("revenue", "Revenue", "revenue"),
        ("operating_income", "Operating Income", "operating income"),
        ("net_income", "Net Income", "net income"),
        ("eps", "Earnings Per Share", "EPS"),
        ("total_assets", "Total Assets", "total assets"),
        ("total_liabilities", "Total Liabilities", "total liabilities"),
        ("equity", "Shareholder Equity", "equity"),
        ("cash_flow_ops", "Operating Cash Flow", "operating cash flow"),
        ("cash_flow_investing", "Investing Cash Flow", "investing cash flow"),
        ("cash_flow_financing", "Financing Cash Flow", "financing cash flow"),
        ("cogs", "Cost of Goods Sold", "COGS"),
        ("gross_profit", "Gross Profit", "gross profit"),
        ("r_and_d_expenses", "R&D Expenses", "R&D expenses"),
        ("sg_and_a_expenses", "SG&A Expenses", "SG&A expenses"),
        ("ebit", "EBIT", "EBIT"),
        ("ebitda", "EBITDA", "EBITDA"),
        ("capex", "Capital Expenditures", "capex"),
        ("dividends", "Dividends Paid", "dividends"),
        ("buybacks", "Share Buybacks", "buybacks"),
    ]
    
    test_company = "MSFT"
    test_year = 2023
    test_quarter = 2
    
    results = []
    
    for metric_code, metric_name, query_term in metrics:
        print(f"\n{'='*120}")
        print(f"Testing: {metric_name} ({metric_code})")
        print(f"{'='*120}")
        
        # Test Quarterly
        quarterly_query = f"show {test_company} {query_term} for Q{test_quarter} {test_year}"
        print(f"\n📊 QUARTERLY: {quarterly_query}")
        
        try:
            q_result = await cfo_agent_graph.run(quarterly_query)
            q_lines = q_result.split('\n')
            q_value = q_lines[0] if q_lines else "No response"
            
            # Check if data was returned
            if "No data" in q_result or "No results" in q_result:
                q_status = "❌ NO DATA"
                q_display = "N/A"
            else:
                q_status = "✅"
                q_display = q_value[:80]
            
            print(f"  {q_status} {q_display}")
        except Exception as e:
            q_status = "❌ ERROR"
            q_display = str(e)[:50]
            print(f"  {q_status} {q_display}")
        
        # Test Annual
        annual_query = f"show {test_company} {query_term} for {test_year}"
        print(f"\n📅 ANNUAL: {annual_query}")
        
        try:
            a_result = await cfo_agent_graph.run(annual_query)
            a_lines = a_result.split('\n')
            a_value = a_lines[0] if a_lines else "No response"
            
            # Check if data was returned
            if "No data" in a_result or "No results" in a_result:
                a_status = "❌ NO DATA"
                a_display = "N/A"
            else:
                a_status = "✅"
                a_display = a_value[:80]
            
            print(f"  {a_status} {a_display}")
        except Exception as e:
            a_status = "❌ ERROR"
            a_display = str(e)[:50]
            print(f"  {a_status} {a_display}")
        
        results.append({
            'metric': metric_name,
            'code': metric_code,
            'quarterly': q_status,
            'annual': a_status
        })
    
    # Summary Table
    print("\n" + "="*120)
    print("SUMMARY: ALL 19 METRICS TEST RESULTS")
    print("="*120)
    print(f"\n{'#':<4} {'Metric':<35} {'Code':<25} {'Quarterly':<12} {'Annual':<12}")
    print("-"*120)
    
    for i, result in enumerate(results, 1):
        print(f"{i:<4} {result['metric']:<35} {result['code']:<25} {result['quarterly']:<12} {result['annual']:<12}")
    
    # Count successes
    q_success = sum(1 for r in results if "✅" in r['quarterly'])
    a_success = sum(1 for r in results if "✅" in r['annual'])
    total = len(results)
    
    print("\n" + "="*120)
    print(f"RESULTS: Quarterly {q_success}/{total} | Annual {a_success}/{total} | Total {q_success + a_success}/{total*2}")
    print("="*120)
    
    # Check data sources
    print("\n" + "="*120)
    print("DATA SOURCE VERIFICATION")
    print("="*120)
    
    print("\n📊 QUARTERLY DATA SOURCE (fact_financials):")
    q_check = """
        SELECT 'fact_financials' as source, COUNT(*) as count
        FROM fact_financials
        WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'MSFT')
        AND fiscal_year = 2023 AND fiscal_quarter = 2
    """
    q_source = await db_pool.execute_query(q_check)
    print(f"  Found {q_source[0]['count']} records in fact_financials for MSFT Q2 2023")
    
    print("\n📅 ANNUAL DATA SOURCE (mv_financials_annual):")
    a_check = """
        SELECT 'mv_financials_annual' as source, COUNT(*) as count
        FROM mv_financials_annual
        WHERE company_id = (SELECT company_id FROM dim_company WHERE ticker = 'MSFT')
        AND fiscal_year = 2023
    """
    a_source = await db_pool.execute_query(a_check)
    print(f"  Found {a_source[0]['count']} records in mv_financials_annual for MSFT 2023")
    
    await db_pool.close()
    
    return results


if __name__ == "__main__":
    asyncio.run(test_all_metrics())
