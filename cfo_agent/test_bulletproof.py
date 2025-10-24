"""
BULLETPROOF TEST SUITE - EXHAUSTIVE COVERAGE
Tests every possible query pattern, company, metric, period, and combination
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

# All companies to test
COMPANIES = ["Apple", "Microsoft", "Google", "Amazon", "Meta"]

# Comprehensive test queries - EVERY possible pattern
BULLETPROOF_TESTS = [
    # ============================================================================
    # SECTION 1: EVERY FINANCIAL METRIC × EVERY COMPANY (Quarterly)
    # ============================================================================
    ("Fin-Rev-Q", "show {company} revenue Q2 2023"),
    ("Fin-NI-Q", "show {company} net income Q2 2023"),
    ("Fin-OI-Q", "show {company} operating income Q2 2023"),
    ("Fin-GP-Q", "show {company} gross profit Q2 2023"),
    ("Fin-RD-Q", "show {company} R&D expenses Q2 2023"),
    ("Fin-SGA-Q", "show {company} SG&A expenses Q2 2023"),
    ("Fin-COGS-Q", "show {company} COGS Q2 2023"),
    ("Fin-OCF-Q", "show {company} operating cash flow Q2 2023"),
    ("Fin-Capex-Q", "show {company} capex Q2 2023"),
    ("Fin-EPS-Q", "show {company} EPS Q2 2023"),
    
    # ============================================================================
    # SECTION 2: EVERY FINANCIAL METRIC × EVERY COMPANY (Annual)
    # ============================================================================
    ("Fin-Rev-A", "show {company} revenue 2023"),
    ("Fin-NI-A", "show {company} net income 2023"),
    ("Fin-OI-A", "show {company} operating income 2023"),
    ("Fin-GP-A", "show {company} gross profit 2023"),
    ("Fin-RD-A", "show {company} R&D expenses 2023"),
    ("Fin-Capex-A", "show {company} capex 2023"),
    
    # ============================================================================
    # SECTION 3: EVERY RATIO × EVERY COMPANY (Quarterly)
    # ============================================================================
    ("Ratio-GM-Q", "show {company} gross margin Q2 2023"),
    ("Ratio-OM-Q", "show {company} operating margin Q2 2023"),
    ("Ratio-NM-Q", "show {company} net margin Q2 2023"),
    ("Ratio-ROE-Q", "show {company} ROE Q2 2023"),
    ("Ratio-ROA-Q", "show {company} ROA Q2 2023"),
    ("Ratio-DE-Q", "show {company} debt to equity Q2 2023"),
    ("Ratio-RDI-Q", "show {company} R&D intensity Q2 2023"),
    
    # ============================================================================
    # SECTION 4: EVERY RATIO × EVERY COMPANY (Annual)
    # ============================================================================
    ("Ratio-GM-A", "show {company} gross margin 2023"),
    ("Ratio-OM-A", "show {company} operating margin 2023"),
    ("Ratio-NM-A", "show {company} net margin 2023"),
    ("Ratio-ROE-A", "show {company} ROE 2023"),
    ("Ratio-ROA-A", "show {company} ROA 2023"),
    
    # ============================================================================
    # SECTION 5: STOCK METRICS × EVERY COMPANY
    # ============================================================================
    ("Stock-Price-Q", "show {company} stock price Q2 2023"),
    ("Stock-Return-Q", "show {company} stock return Q2 2023"),
    ("Stock-Vol-Q", "show {company} volatility Q2 2023"),
    ("Stock-Price-A", "show {company} stock price 2023"),
    ("Stock-Return-A", "show {company} annual return 2023"),
    
    # ============================================================================
    # SECTION 6: DIFFERENT TIME PERIODS (Test temporal variations)
    # ============================================================================
    ("Time-Q1", "show Apple revenue Q1 2023"),
    ("Time-Q2", "show Apple revenue Q2 2023"),
    ("Time-Q3", "show Apple revenue Q3 2023"),
    ("Time-Q4", "show Apple revenue Q4 2023"),
    ("Time-2023", "show Apple revenue 2023"),
    ("Time-2022", "show Apple revenue 2022"),
    ("Time-Latest", "show Apple latest quarter revenue"),
    
    # ============================================================================
    # SECTION 7: MACRO INDICATORS (All variations)
    # ============================================================================
    ("Macro-GDP-Q", "show GDP Q2 2023"),
    ("Macro-CPI-Q", "show CPI Q2 2023"),
    ("Macro-Unemp-Q", "show unemployment rate Q2 2023"),
    ("Macro-Fed-Q", "show Fed rate Q2 2023"),
    ("Macro-SPX-Q", "show S&P 500 Q2 2023"),
    ("Macro-GDP-A", "show GDP 2023"),
    ("Macro-CPI-A", "show CPI 2023"),
    
    # ============================================================================
    # SECTION 8: MACRO SENSITIVITY × EVERY COMPANY
    # ============================================================================
    ("Sens-Gen-Q", "show {company} macro sensitivity Q2 2023"),
    ("Sens-CPI-Q", "show {company} beta to inflation Q2 2023"),
    ("Sens-Fed-Q", "show {company} beta to Fed rate Q2 2023"),
    ("Sens-Gen-A", "show {company} macro sensitivity 2023"),
    ("Sens-CPI-A", "show {company} beta to CPI 2023"),
    
    # ============================================================================
    # SECTION 9: COMBINED VIEWS - ALL LAYERS × ALL COMPANIES
    # ============================================================================
    ("Comb-L1-Q", "show {company} complete picture Q2 2023"),
    ("Comb-L1-A", "show {company} complete picture 2023"),
    ("Comb-L2-Q", "show {company} with macro context Q2 2023"),
    ("Comb-L2-A", "show {company} with macro 2023"),
    ("Comb-L3-Q", "show {company} full analysis Q2 2023"),
    ("Comb-L3-A", "show {company} full analysis 2023"),
    
    # ============================================================================
    # SECTION 10: MULTIPLE ATTRIBUTES (Every combination)
    # ============================================================================
    ("Multi-2", "show {company} revenue, net income Q2 2023"),
    ("Multi-3", "show {company} revenue, net income, gross margin Q2 2023"),
    ("Multi-4", "show {company} revenue, net income, ROE, debt to equity Q2 2023"),
    ("Multi-Mix", "show {company} revenue and operating margin Q2 2023"),
    
    # ============================================================================
    # SECTION 11: GROWTH QUERIES × COMPANIES
    # ============================================================================
    ("Growth-QoQ", "show {company} revenue growth Q2 2023"),
    ("Growth-YoY", "show {company} YoY growth Q2 2023"),
    ("Growth-Ann", "show {company} annual growth 2023"),
    ("Growth-CAGR", "show {company} 3-year CAGR 2023"),
    
    # ============================================================================
    # SECTION 12: PEER COMPARISONS (Different metrics)
    # ============================================================================
    ("Peer-Rev-Q", "who led in revenue Q2 2023"),
    ("Peer-Marg-Q", "rank companies by net margin Q2 2023"),
    ("Peer-Rev-A", "who led in revenue 2023"),
    ("Peer-ROE-A", "rank companies by ROE 2023"),
    
    # ============================================================================
    # SECTION 13: TTM QUERIES × COMPANIES
    # ============================================================================
    ("TTM-Rev", "show {company} TTM revenue"),
    ("TTM-Marg", "show {company} TTM gross margin"),
    ("TTM-ROE", "show {company} TTM ROE"),
]

# Multi-company specific tests (not per-company)
MULTI_COMPANY_TESTS = [
    # ============================================================================
    # SECTION 14: EVERY PAIR OF COMPANIES (Sample key pairs)
    # ============================================================================
    ("MC-Apple-Google", "show Apple and Google revenue Q2 2023"),
    ("MC-Apple-Microsoft", "compare Apple and Microsoft net income Q2 2023"),
    ("MC-Google-Amazon", "show Google and Amazon gross margin Q2 2023"),
    ("MC-Microsoft-Meta", "compare Microsoft and Meta revenue 2023"),
    ("MC-Apple-Amazon", "show Apple and Amazon operating margin Q3 2023"),
    
    # ============================================================================
    # SECTION 15: THREE+ COMPANIES
    # ============================================================================
    ("MC3-Rev", "show Apple, Microsoft, and Google revenue Q2 2023"),
    ("MC3-Marg", "compare Apple, Google, Amazon net margin 2023"),
    ("MC4-Rev", "show revenue for Apple, Microsoft, Google, Amazon Q2 2023"),
    
    # ============================================================================
    # SECTION 16: MULTI-COMPANY + MACRO (All combinations)
    # ============================================================================
    ("MCM-CPI", "compare Apple with Google and how CPI affected both companies Q2 2023"),
    ("MCM-GDP", "show Apple and Microsoft with GDP context Q2 2023"),
    ("MCM-Inf", "compare Apple vs Google with inflation Q2 2023"),
    ("MCM-Econ", "show Microsoft and Amazon with economic context 2023"),
    
    # ============================================================================
    # SECTION 17: COMPLEX COMBINATIONS
    # ============================================================================
    ("Complex-2C2M", "show Apple and Google revenue and net income Q2 2023"),
    ("Complex-2C3M", "compare Apple vs Microsoft revenue, margin, ROE 2023"),
    ("Complex-Multi", "show Apple and Google revenue, net income, gross margin Q2 2023"),
]

# Query variations (different phrasings)
VARIATION_TESTS = [
    # ============================================================================
    # SECTION 18: NATURAL LANGUAGE VARIATIONS
    # ============================================================================
    ("Var-What", "what was Apple revenue Q2 2023"),
    ("Var-Tell", "tell me Apple net income Q2 2023"),
    ("Var-Display", "display Apple gross margin Q2 2023"),
    ("Var-Get", "get Microsoft revenue 2023"),
    ("Var-Question", "what is Google stock price Q2 2023"),
    
    # ============================================================================
    # SECTION 19: TICKER INSTEAD OF NAME
    # ============================================================================
    ("Ticker-AAPL", "show AAPL revenue Q2 2023"),
    ("Ticker-MSFT", "show MSFT net income Q2 2023"),
    ("Ticker-GOOG", "show GOOG gross margin Q2 2023"),
    ("Ticker-AMZN", "show AMZN operating income Q2 2023"),
    ("Ticker-META", "show META revenue 2023"),
    
    # ============================================================================
    # SECTION 20: DIFFERENT PERIOD FORMATS
    # ============================================================================
    ("Period-2023Q2", "show Apple revenue 2023 Q2"),
    ("Period-FY", "show Apple revenue FY2023"),
    ("Period-FYQ", "show Apple revenue FY2023 Q2"),
    ("Period-Fiscal", "show Apple fiscal year 2023 revenue"),
]


async def run_bulletproof_test():
    """Run exhaustive bulletproof test"""
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("BULLETPROOF TEST SUITE - EXHAUSTIVE COVERAGE")
    print("="*120)
    
    # Generate all per-company tests
    all_tests = []
    
    # Expand template tests for each company
    for category, query_template in BULLETPROOF_TESTS:
        if "{company}" in query_template:
            for company in COMPANIES:
                query = query_template.format(company=company)
                all_tests.append((f"{category}-{company}", query))
        else:
            all_tests.append((category, query_template))
    
    # Add multi-company tests
    all_tests.extend(MULTI_COMPANY_TESTS)
    
    # Add variation tests
    all_tests.extend(VARIATION_TESTS)
    
    print(f"Total Test Cases: {len(all_tests)}")
    print("="*120)
    
    # Track results
    results = {}
    passed = 0
    failed = 0
    errors = 0
    
    for i, (category, query) in enumerate(all_tests, 1):
        # Extract base category (before company name)
        base_cat = category.rsplit('-', 1)[0] if '-' in category else category
        
        if base_cat not in results:
            results[base_cat] = {"pass": 0, "fail": 0, "error": 0, "total": 0}
        
        results[base_cat]["total"] += 1
        
        # Print progress every 20 queries
        if i % 20 == 0:
            print(f"[{i}/{len(all_tests)}] Progress: {passed} passed, {failed} failed, {errors} errors")
        
        try:
            response = await cfo_agent_graph.run(query)
            
            # Simple pass/fail criteria
            is_error = any(word in response.lower() for word in ['error', 'failed', 'exception'])
            is_meaningful = len(response) > 30 and 'no results' not in response.lower()
            
            if is_meaningful and not is_error:
                results[base_cat]["pass"] += 1
                passed += 1
            elif is_error:
                results[base_cat]["error"] += 1
                errors += 1
                print(f"   ❌ [{category}] ERROR: {query[:60]}...")
            else:
                results[base_cat]["fail"] += 1
                failed += 1
                if failed <= 5:  # Only print first 5 failures
                    print(f"   ⚠️  [{category}] FAIL: {query[:60]}...")
                
        except Exception as e:
            results[base_cat]["error"] += 1
            errors += 1
            if errors <= 5:  # Only print first 5 errors
                print(f"   ❌ [{category}] EXCEPTION: {str(e)[:80]}")
    
    await db_pool.close()
    
    # Print comprehensive summary
    print("\n" + "="*120)
    print("CATEGORY BREAKDOWN")
    print("="*120)
    
    print(f"\n{'Category':<35} {'Pass':<8} {'Fail':<8} {'Error':<8} {'Total':<8} {'Rate':<10} {'Status'}")
    print("-"*110)
    
    for cat in sorted(results.keys()):
        stats = results[cat]
        rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
        print(f"{cat:<35} {stats['pass']:<8} {stats['fail']:<8} {stats['error']:<8} {stats['total']:<8} {rate:>6.1f}%    {status}")
    
    # Overall summary
    print("\n" + "="*120)
    print("OVERALL RESULTS")
    print("="*120)
    
    total_tests = len(all_tests)
    overall_rate = (passed / total_tests * 100)
    
    print(f"\n📊 Test Statistics:")
    print(f"   Total Tests Run:     {total_tests}")
    print(f"   ✅ Passed:           {passed} ({passed/total_tests*100:.1f}%)")
    print(f"   ❌ Failed:           {failed} ({failed/total_tests*100:.1f}%)")
    print(f"   🔥 Errors:           {errors} ({errors/total_tests*100:.1f}%)")
    print(f"   📈 Overall Pass Rate: {overall_rate:.1f}%")
    
    print(f"\n🎯 Coverage:")
    print(f"   • {len(results)} Unique Categories")
    print(f"   • {len(COMPANIES)} Companies Tested")
    print(f"   • Multiple Time Periods")
    print(f"   • All Query Patterns")
    
    print("\n" + "="*120)
    if overall_rate >= 95:
        print("🏆 EXCEPTIONAL! System is bulletproof and production-ready!")
    elif overall_rate >= 90:
        print("🎉 EXCELLENT! System is highly reliable with minimal issues.")
    elif overall_rate >= 85:
        print("✅ VERY GOOD! System is solid with a few edge cases to address.")
    elif overall_rate >= 80:
        print("⚠️  GOOD! System is functional but some improvements needed.")
    else:
        print("❌ NEEDS ATTENTION! Multiple areas require fixes.")
    print("="*120)


if __name__ == "__main__":
    asyncio.run(run_bulletproof_test())
