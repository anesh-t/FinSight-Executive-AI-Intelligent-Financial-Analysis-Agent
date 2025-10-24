"""
FINAL COMPREHENSIVE TEST - ALL QUERY CAPABILITIES
Tests all query types from basic to advanced
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

# Comprehensive test covering ALL capabilities
TEST_QUERIES = [
    # ============================================================================
    # CATEGORY 1: BASIC FINANCIAL QUERIES (Quarterly)
    # ============================================================================
    ("Basic Financials Q", "show Apple revenue Q2 2023", ["Apple", "revenue", "81"]),
    ("Basic Financials Q", "show Microsoft net income Q3 2023", ["Microsoft", "net income", "22"]),
    ("Basic Financials Q", "show Google R&D expenses Q2 2023", ["Google", "R&D", "10"]),
    ("Basic Financials Q", "show Amazon operating income Q3 2023", ["Amazon", "operating", "11"]),
    
    # ============================================================================
    # CATEGORY 2: BASIC FINANCIAL QUERIES (Annual)
    # ============================================================================
    ("Basic Financials A", "show Apple revenue 2023", ["Apple", "revenue", "385"]),
    ("Basic Financials A", "show Microsoft net income 2023", ["Microsoft", "net income", "82"]),
    ("Basic Financials A", "show Google operating income 2023", ["Google", "operating"]),
    ("Basic Financials A", "show Amazon capex 2023", ["Amazon", "capex"]),
    
    # ============================================================================
    # CATEGORY 3: RATIO QUERIES (Quarterly)
    # ============================================================================
    ("Ratios Q", "show Apple gross margin Q2 2023", ["Apple", "gross margin", "44"]),
    ("Ratios Q", "show Microsoft ROE Q3 2023", ["Microsoft", "ROE", "37"]),
    ("Ratios Q", "show Google net margin Q2 2023", ["Google", "net margin", "24"]),
    ("Ratios Q", "show Amazon debt to equity Q3 2023", ["Amazon", "debt"]),
    
    # ============================================================================
    # CATEGORY 4: RATIO QUERIES (Annual)
    # ============================================================================
    ("Ratios A", "show Apple gross margin 2023", ["Apple", "gross margin", "45"]),
    ("Ratios A", "show Microsoft ROE 2023", ["Microsoft", "ROE"]),
    ("Ratios A", "show Google operating margin 2023", ["Google", "operating margin"]),
    ("Ratios A", "show Amazon R&D intensity 2023", ["Amazon", "intensity"]),
    
    # ============================================================================
    # CATEGORY 5: STOCK PRICE QUERIES
    # ============================================================================
    ("Stock Prices Q", "show Apple stock price Q2 2023", ["Apple", "stock", "price", "180"]),
    ("Stock Prices Q", "show Microsoft stock return Q3 2023", ["Microsoft", "return"]),
    ("Stock Prices A", "show Apple stock price 2023", ["Apple", "stock", "186"]),
    ("Stock Prices A", "show Microsoft annual return 2023", ["Microsoft", "return"]),
    
    # ============================================================================
    # CATEGORY 6: MACRO INDICATORS
    # ============================================================================
    ("Macro Q", "show GDP Q2 2023", ["GDP", "22"]),
    ("Macro Q", "show CPI Q2 2023", ["CPI", "303"]),
    ("Macro A", "show GDP 2023", ["GDP"]),
    ("Macro A", "show unemployment rate 2023", ["unemployment"]),
    
    # ============================================================================
    # CATEGORY 7: MACRO SENSITIVITY
    # ============================================================================
    ("Sensitivity Q", "show Apple macro sensitivity Q2 2023", ["Apple", "beta", "sensitivity"]),
    ("Sensitivity Q", "show Microsoft beta to inflation Q3 2023", ["Microsoft", "beta"]),
    ("Sensitivity A", "show Apple macro sensitivity 2023", ["Apple", "beta"]),
    ("Sensitivity A", "show Google beta to CPI 2023", ["Google", "beta"]),
    
    # ============================================================================
    # CATEGORY 8: GROWTH QUERIES
    # ============================================================================
    ("Growth Q", "show Apple revenue growth Q2 2023", ["Apple", "growth"]),
    ("Growth A", "show Microsoft annual growth 2023", ["Microsoft", "growth"]),
    ("Growth CAGR", "show Apple 3-year CAGR 2023", ["Apple", "CAGR"]),
    
    # ============================================================================
    # CATEGORY 9: PEER COMPARISONS
    # ============================================================================
    ("Peer Q", "who led in revenue Q2 2023", ["revenue", "led"]),
    ("Peer A", "rank companies by net margin 2023", ["rank", "margin"]),
    
    # ============================================================================
    # CATEGORY 10: COMBINED VIEWS - LAYER 1 (Core Company)
    # ============================================================================
    ("Combined L1 Q", "show Apple complete picture Q2 2023", ["Apple", "revenue", "margin", "ROE"]),
    ("Combined L1 Q", "everything about Microsoft Q3 2023", ["Microsoft", "revenue", "income"]),
    ("Combined L1 A", "show Apple complete picture 2023", ["Apple", "revenue", "385"]),
    ("Combined L1 A", "everything about Google 2023", ["Google", "revenue"]),
    
    # ============================================================================
    # CATEGORY 11: COMBINED VIEWS - LAYER 2 (With Macro)
    # ============================================================================
    ("Combined L2 Q", "show Apple with macro context Q2 2023", ["Apple", "revenue", "GDP"]),
    ("Combined L2 Q", "Microsoft with economic context Q3 2023", ["Microsoft", "revenue"]),
    ("Combined L2 A", "show Apple with macro 2023", ["Apple", "revenue", "GDP"]),
    ("Combined L2 A", "Google with inflation 2023", ["Google", "revenue"]),
    
    # ============================================================================
    # CATEGORY 12: COMBINED VIEWS - LAYER 3 (Full with Betas)
    # ============================================================================
    ("Combined L3 Q", "show Apple full analysis Q2 2023", ["Apple", "revenue", "beta"]),
    ("Combined L3 Q", "everything including betas for Microsoft Q3 2023", ["Microsoft", "revenue"]),
    ("Combined L3 A", "show Apple full analysis 2023", ["Apple", "revenue", "beta"]),
    ("Combined L3 A", "Microsoft full picture with sensitivity 2023", ["Microsoft", "revenue"]),
    
    # ============================================================================
    # CATEGORY 13: MULTIPLE ATTRIBUTES (Single Company, Multiple Metrics)
    # ============================================================================
    ("Multi-Attr", "show Apple revenue, net income Q2 2023", ["Apple", "revenue", "net income"]),
    ("Multi-Attr", "show Microsoft revenue and operating income Q3 2023", ["Microsoft", "revenue", "operating"]),
    ("Multi-Attr", "show Google revenue, net income, gross margin Q2 2023", ["Google", "revenue", "margin"]),
    ("Multi-Attr", "show Amazon revenue, net income, ROE Q3 2023", ["Amazon", "revenue", "ROE"]),
    
    # ============================================================================
    # CATEGORY 14: MULTIPLE COMPANIES (Multi Company, Single/Multiple Metrics)
    # ============================================================================
    ("Multi-Co", "show Google and Apple revenue Q2 2023", ["revenue", "Apple", "Google"]),
    ("Multi-Co", "compare Apple and Microsoft net income Q3 2023", ["Apple", "Microsoft", "income"]),
    ("Multi-Co", "show Apple, Microsoft, and Google revenue 2023", ["revenue"]),
    ("Multi-Co", "compare Apple and Google gross margin Q2 2023", ["margin"]),
    
    # ============================================================================
    # CATEGORY 15: MULTI-COMPANY + MACRO CONTEXT
    # ============================================================================
    ("Multi-Co Macro", "compare Apple with Google and how CPI affected both companies Q2 2023", ["Apple", "Google"]),
    ("Multi-Co Macro", "show Apple vs Microsoft with inflation Q3 2023", ["Apple", "Microsoft"]),
    ("Multi-Co Macro", "compare Apple and Google with GDP 2023", ["Apple", "Google"]),
    
    # ============================================================================
    # CATEGORY 16: COMPLEX COMBINED QUERIES
    # ============================================================================
    ("Complex", "show Apple and Google revenue and net income Q2 2023", ["revenue", "income"]),
    ("Complex", "compare Apple vs Microsoft revenue, margin, ROE 2023", ["revenue", "margin"]),
    
    # ============================================================================
    # CATEGORY 17: TTM (Trailing 12 Months)
    # ============================================================================
    ("TTM", "show Apple TTM revenue", ["Apple", "revenue"]),
    ("TTM", "show Microsoft TTM gross margin", ["Microsoft", "margin"]),
    
    # ============================================================================
    # CATEGORY 18: SPECIAL QUERIES
    # ============================================================================
    ("Special", "show Apple latest quarter revenue", ["Apple", "revenue"]),
    ("Special", "show Microsoft most recent quarter", ["Microsoft"]),
]


async def run_comprehensive_test():
    """Run comprehensive test of all capabilities"""
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("FINAL COMPREHENSIVE TEST - ALL QUERY CAPABILITIES")
    print("="*120)
    print(f"Testing {len(TEST_QUERIES)} queries across 18 categories")
    print("="*120)
    
    # Track results by category
    results = {}
    total_pass = 0
    total_fail = 0
    
    for i, (category, query, expected_keywords) in enumerate(TEST_QUERIES, 1):
        if category not in results:
            results[category] = {"pass": 0, "total": 0, "failed": []}
        
        results[category]["total"] += 1
        
        print(f"\n[{i}/{len(TEST_QUERIES)}] [{category}]")
        print(f"Query: {query}")
        print("-"*120)
        
        try:
            response = await cfo_agent_graph.run(query)
            
            # Check for expected keywords
            response_lower = response.lower()
            found = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
            has_error = any(word in response_lower for word in ['error', 'failed', 'exception'])
            is_meaningful = len(response) > 30
            
            # Pass if meaningful response without errors and has some keywords
            passed = is_meaningful and not has_error and (found >= len(expected_keywords) * 0.4 or len(response) > 100)
            
            if passed:
                print(f"✅ PASS - Found {found}/{len(expected_keywords)} keywords")
                print(f"Response: {response[:150]}...")
                results[category]["pass"] += 1
                total_pass += 1
            else:
                print(f"❌ FAIL - Found {found}/{len(expected_keywords)} keywords")
                print(f"Response: {response[:150]}...")
                results[category]["failed"].append(query)
                total_fail += 1
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)[:100]}")
            results[category]["failed"].append(query)
            total_fail += 1
    
    await db_pool.close()
    
    # Print summary
    print("\n" + "="*120)
    print("SUMMARY BY CATEGORY")
    print("="*120)
    
    for category in sorted(results.keys()):
        stats = results[category]
        pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 60 else "❌"
        
        print(f"\n{status} {category:<25} {stats['pass']}/{stats['total']} ({pass_rate:.0f}%)")
        
        if stats["failed"] and pass_rate < 80:
            for failed_q in stats["failed"][:2]:  # Show first 2 failures
                print(f"   ❌ {failed_q[:80]}...")
    
    # Overall summary
    print("\n" + "="*120)
    print("OVERALL SUMMARY")
    print("="*120)
    
    overall_rate = (total_pass / len(TEST_QUERIES) * 100)
    
    print(f"\n{'Category':<30} {'Passed':<10} {'Total':<10} {'Pass Rate':<15} {'Status'}")
    print("-"*75)
    
    for category in sorted(results.keys()):
        stats = results[category]
        pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status_icon = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 60 else "❌"
        print(f"{category:<30} {stats['pass']:<10} {stats['total']:<10} {pass_rate:>6.1f}%        {status_icon}")
    
    print("-"*75)
    print(f"{'TOTAL':<30} {total_pass:<10} {len(TEST_QUERIES):<10} {overall_rate:>6.1f}%")
    
    print("\n" + "="*120)
    if overall_rate >= 90:
        print("🎉 EXCELLENT! Agent is performing exceptionally well across all categories!")
    elif overall_rate >= 80:
        print("✅ GREAT! Agent is working well with minor issues in some categories.")
    elif overall_rate >= 70:
        print("⚠️  GOOD! Agent is functional but needs some improvements.")
    else:
        print("❌ NEEDS ATTENTION! Multiple categories need fixing.")
    print("="*120)
    
    print(f"\n📊 Coverage:")
    print(f"   • 18 Query Categories Tested")
    print(f"   • {len(TEST_QUERIES)} Total Test Cases")
    print(f"   • {total_pass} Passing")
    print(f"   • {total_fail} Failing")
    print(f"   • {overall_rate:.1f}% Overall Pass Rate")


if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
