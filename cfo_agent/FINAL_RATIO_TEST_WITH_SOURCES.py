"""
FINAL COMPREHENSIVE RATIO TEST - All 9 Ratios with Data Source Verification
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def final_ratio_test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*130)
    print("FINAL COMPREHENSIVE RATIO TEST - ALL 9 RATIOS WITH DATA SOURCE VERIFICATION")
    print("="*130)
    
    test_company = "AAPL"
    test_year = 2023
    test_quarter = 2
    
    # Define all 9 ratios from the image
    ratios = [
        ("roe", "ROE", "Return on Equity"),
        ("roa", "ROA", "Return on Assets"),
        ("gross_margin", "gross margin", "Gross Margin"),
        ("operating_margin", "operating margin", "Operating Margin"),
        ("net_margin", "net margin", "Net Profit Margin"),
        ("debt_to_equity", "debt to equity ratio", "Debt-to-Equity Ratio"),
        ("debt_to_assets", "debt to assets ratio", "Debt-to-Assets Ratio"),
        ("rnd_to_revenue", "R&D intensity", "R&D Intensity"),
        ("sgna_to_revenue", "SG&A intensity", "SG&A Intensity"),
    ]
    
    results = []
    
    for code, query_term, full_name in ratios:
        print(f"\n{'='*130}")
        print(f"Testing: {full_name} ({code})")
        print("="*130)
        
        # ============== ANNUAL TEST ==============
        print(f"\n📅 ANNUAL QUERY:")
        print("-"*130)
        
        # Get actual data from database
        # Handle special column name for ROE
        if code == 'roe':
            annual_col = 'roe_annual_avg_equity'
        else:
            annual_col = f'{code}_annual'
        
        annual_db_query = f"""
            SELECT 
                c.ticker,
                r.fiscal_year,
                r.{annual_col}
            FROM mv_ratios_annual r
            JOIN dim_company c USING (company_id)
            WHERE c.ticker = '{test_company}'
            AND r.fiscal_year = {test_year}
        """
        
        annual_db_result = await db_pool.execute_query(annual_db_query)
        
        if annual_db_result:
            db_value = float(annual_db_result[0][annual_col])
            if 'margin' in code or code in ['roe', 'roa']:
                db_display = f"{db_value*100:.2f}%"
            else:
                db_display = f"{db_value:.4f}"
            print(f"  📊 Database (mv_ratios_annual): {db_display}")
        else:
            db_display = "N/A"
            print(f"  ❌ Database: No data")
        
        # Test through agent
        annual_query = f"show {test_company} {query_term} for {test_year}"
        print(f"  🤖 Agent Query: '{annual_query}'")
        
        try:
            agent_result = await cfo_agent_graph.run(annual_query)
            first_line = agent_result.split('\n')[0]
            
            if "No data" in agent_result or "No results" in agent_result:
                annual_status = "❌ FAILED"
                agent_display = "No data"
            elif query_term.lower() in agent_result.lower() or code in agent_result.lower():
                annual_status = "✅ SUCCESS"
                agent_display = first_line[:90]
            else:
                annual_status = "⚠️  PARTIAL"
                agent_display = first_line[:90]
            
            print(f"  {annual_status} Agent Response: {agent_display}")
        except Exception as e:
            annual_status = "❌ ERROR"
            agent_display = str(e)[:80]
            print(f"  {annual_status} {agent_display}")
        
        # ============== QUARTERLY TEST ==============
        print(f"\n📊 QUARTERLY QUERY:")
        print("-"*130)
        
        # Check which table has quarterly data
        # Try fact_ratios first
        quarterly_db_query = f"""
            SELECT 
                c.ticker,
                fr.fiscal_year,
                fr.fiscal_quarter,
                fr.{code}
            FROM fact_ratios fr
            JOIN dim_company c USING (company_id)
            WHERE c.ticker = '{test_company}'
            AND fr.fiscal_year = {test_year}
            AND fr.fiscal_quarter = {test_quarter}
        """
        
        quarterly_db_result = await db_pool.execute_query(quarterly_db_query)
        
        if quarterly_db_result:
            db_value = float(quarterly_db_result[0][code])
            if 'margin' in code or code in ['roe', 'roa']:
                db_display = f"{db_value*100:.2f}%"
            else:
                db_display = f"{db_value:.4f}"
            print(f"  📊 Database (fact_ratios): {db_display}")
            expected_source = "fact_ratios"
        else:
            # Try mv_ratios_ttm
            ttm_query = f"""
                SELECT 
                    c.ticker,
                    r.fiscal_year,
                    r.fiscal_quarter,
                    r.{code}_ttm
                FROM mv_ratios_ttm r
                JOIN dim_company c USING (company_id)
                WHERE c.ticker = '{test_company}'
                AND r.fiscal_year = {test_year}
                AND r.fiscal_quarter = {test_quarter}
            """
            
            ttm_result = await db_pool.execute_query(ttm_query)
            
            if ttm_result:
                db_value = float(ttm_result[0][f'{code}_ttm'])
                db_display = f"{db_value*100:.2f}%"
                print(f"  📊 Database (mv_ratios_ttm): {db_display}")
                expected_source = "mv_ratios_ttm"
            else:
                db_display = "N/A"
                print(f"  ⚠️  Database: Not available quarterly")
                expected_source = "N/A"
        
        # Test through agent
        quarterly_query = f"show {test_company} {query_term} for Q{test_quarter} {test_year}"
        print(f"  🤖 Agent Query: '{quarterly_query}'")
        
        try:
            agent_result = await cfo_agent_graph.run(quarterly_query)
            first_line = agent_result.split('\n')[0]
            
            if "No data" in agent_result or "No results" in agent_result:
                quarterly_status = "❌ FAILED"
                agent_display = "No data"
            elif query_term.lower() in agent_result.lower() or code in agent_result.lower():
                quarterly_status = "✅ SUCCESS"
                agent_display = first_line[:90]
            elif expected_source == "N/A":
                quarterly_status = "⏸️  N/A"
                agent_display = "Not available quarterly"
            else:
                quarterly_status = "⚠️  PARTIAL"
                agent_display = first_line[:90]
            
            print(f"  {quarterly_status} Agent Response: {agent_display}")
        except Exception as e:
            quarterly_status = "❌ ERROR"
            agent_display = str(e)[:80]
            print(f"  {quarterly_status} {agent_display}")
        
        results.append({
            'code': code,
            'name': full_name,
            'annual_status': annual_status,
            'quarterly_status': quarterly_status,
            'quarterly_source': expected_source
        })
    
    # ============== SUMMARY ==============
    print("\n" + "="*130)
    print("FINAL SUMMARY - ALL 9 RATIOS")
    print("="*130)
    
    print(f"\n{'#':<4} {'Ratio':<30} {'Code':<20} {'Annual':<15} {'Quarterly':<15} {'Q Source':<20}")
    print("-"*130)
    
    for i, result in enumerate(results, 1):
        print(f"{i:<4} {result['name']:<30} {result['code']:<20} {result['annual_status']:<15} "
              f"{result['quarterly_status']:<15} {result['quarterly_source']:<20}")
    
    # Count successes
    annual_success = sum(1 for r in results if "✅" in r['annual_status'])
    quarterly_success = sum(1 for r in results if "✅" in r['quarterly_status'])
    quarterly_na = sum(1 for r in results if "⏸️" in r['quarterly_status'])
    total = len(results)
    
    print("\n" + "="*130)
    print(f"RESULTS:")
    print(f"  Annual Ratios:    {annual_success}/{total} working ✅")
    print(f"  Quarterly Ratios: {quarterly_success}/{total-quarterly_na} available working ✅ ({quarterly_na} N/A)")
    print(f"  Overall Success:  {annual_success + quarterly_success}/{total + (total-quarterly_na)} queries")
    print("="*130)
    
    # Data source summary
    print("\n📊 DATA SOURCE MAPPING:")
    print("-"*130)
    print("ANNUAL RATIOS:")
    print("  Source: mv_ratios_annual")
    print("  Template: annual_metrics")
    print("  Columns: roe_annual, roa_annual, gross_margin_annual, operating_margin_annual,")
    print("           net_margin_annual, debt_to_equity_annual, debt_to_assets_annual,")
    print("           rnd_to_revenue_annual, sgna_to_revenue_annual")
    print("")
    print("QUARTERLY RATIOS:")
    print("  Source 1: mv_ratios_ttm (for margins, ROE, ROA)")
    print("    Template: ttm_snapshot or quarter_snapshot")
    print("    Columns: gross_margin_ttm, operating_margin_ttm, net_margin_ttm, roe_ttm, roa_ttm")
    print("  Source 2: fact_ratios (for debt & intensity ratios)")
    print("    Template: quarterly_ratios")
    print("    Columns: debt_to_equity, debt_to_assets, rnd_to_revenue, sgna_to_revenue")
    print("="*130)
    
    await db_pool.close()

asyncio.run(final_ratio_test())
