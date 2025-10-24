"""
Comprehensive Combined Views Test
Tests all layers, both periods, multiple companies, data accuracy, and response quality
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

# Comprehensive test queries covering all scenarios
TEST_QUERIES = [
    # ============================================================================
    # LAYER 1: Core Company (Financials + Ratios + Stock)
    # ============================================================================
    
    # Quarterly - Different companies
    {
        "category": "Layer 1: Core Q",
        "query": "show Apple complete picture Q2 2023",
        "expect_keywords": ["revenue", "income", "margin", "roe", "stock", "price"],
        "expect_metrics": ["revenue_b", "net_income_b", "gross_margin", "roe", "avg_price"],
        "companies": ["Apple", "AAPL"]
    },
    {
        "category": "Layer 1: Core Q",
        "query": "everything about Microsoft Q3 2023",
        "expect_keywords": ["revenue", "income", "margin", "microsoft"],
        "expect_metrics": ["revenue_b", "net_income_b", "operating_margin"],
        "companies": ["Microsoft", "MSFT"]
    },
    {
        "category": "Layer 1: Core Q",
        "query": "comprehensive view of Google Q2 2023",
        "expect_keywords": ["revenue", "income", "google"],
        "expect_metrics": ["revenue_b", "net_income_b"],
        "companies": ["Google", "GOOGL"]
    },
    {
        "category": "Layer 1: Core Q",
        "query": "show Amazon complete picture Q3 2023",
        "expect_keywords": ["revenue", "amazon"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Amazon", "AMZN"]
    },
    {
        "category": "Layer 1: Core Q",
        "query": "complete data for Meta Q2 2023",
        "expect_keywords": ["revenue", "meta"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Meta", "META"]
    },
    
    # Annual - Different companies
    {
        "category": "Layer 1: Core A",
        "query": "show Apple complete picture 2023",
        "expect_keywords": ["revenue", "income", "margin", "roe", "2023"],
        "expect_metrics": ["revenue_b", "net_income_b", "gross_margin_annual"],
        "companies": ["Apple", "AAPL"]
    },
    {
        "category": "Layer 1: Core A",
        "query": "everything about Microsoft 2023",
        "expect_keywords": ["revenue", "income", "microsoft", "2023"],
        "expect_metrics": ["revenue_b", "net_income_b"],
        "companies": ["Microsoft", "MSFT"]
    },
    {
        "category": "Layer 1: Core A",
        "query": "comprehensive annual view of Amazon 2023",
        "expect_keywords": ["revenue", "amazon", "2023"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Amazon", "AMZN"]
    },
    {
        "category": "Layer 1: Core A",
        "query": "show Meta complete view 2023",
        "expect_keywords": ["revenue", "meta", "2023"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Meta", "META"]
    },
    
    # ============================================================================
    # LAYER 2: With Macro Context (Company + Economic Data)
    # ============================================================================
    
    # Quarterly with macro
    {
        "category": "Layer 2: Macro Q",
        "query": "show Apple with macro context Q2 2023",
        "expect_keywords": ["revenue", "income", "gdp", "cpi", "inflation", "unemployment", "fed"],
        "expect_metrics": ["revenue_b", "gdp", "cpi", "unemployment_rate"],
        "companies": ["Apple", "AAPL"]
    },
    {
        "category": "Layer 2: Macro Q",
        "query": "Microsoft with economic context Q3 2023",
        "expect_keywords": ["revenue", "microsoft", "economic", "gdp", "inflation"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Microsoft", "MSFT"]
    },
    {
        "category": "Layer 2: Macro Q",
        "query": "Google complete picture with inflation Q2 2023",
        "expect_keywords": ["revenue", "google", "inflation", "cpi"],
        "expect_metrics": ["revenue_b", "cpi"],
        "companies": ["Google", "GOOGL"]
    },
    {
        "category": "Layer 2: Macro Q",
        "query": "Amazon with GDP context Q3 2023",
        "expect_keywords": ["revenue", "amazon", "gdp"],
        "expect_metrics": ["revenue_b", "gdp"],
        "companies": ["Amazon", "AMZN"]
    },
    {
        "category": "Layer 2: Macro Q",
        "query": "Meta with unemployment rate Q2 2023",
        "expect_keywords": ["revenue", "meta", "unemployment"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Meta", "META"]
    },
    
    # Annual with macro
    {
        "category": "Layer 2: Macro A",
        "query": "show Apple with macro 2023",
        "expect_keywords": ["revenue", "apple", "gdp", "cpi", "2023"],
        "expect_metrics": ["revenue_b", "gdp_annual", "cpi_annual"],
        "companies": ["Apple", "AAPL"]
    },
    {
        "category": "Layer 2: Macro A",
        "query": "Microsoft with economic context 2023",
        "expect_keywords": ["revenue", "microsoft", "economic", "2023"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Microsoft", "MSFT"]
    },
    {
        "category": "Layer 2: Macro A",
        "query": "Google annual with inflation 2023",
        "expect_keywords": ["revenue", "google", "inflation", "2023"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Google", "GOOGL"]
    },
    {
        "category": "Layer 2: Macro A",
        "query": "Amazon complete view with GDP 2023",
        "expect_keywords": ["revenue", "amazon", "gdp", "2023"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Amazon", "AMZN"]
    },
    
    # ============================================================================
    # LAYER 3: Full Picture (Company + Macro + Sensitivity)
    # ============================================================================
    
    # Quarterly with sensitivity
    {
        "category": "Layer 3: Full Q",
        "query": "show Apple full analysis Q2 2023",
        "expect_keywords": ["revenue", "income", "gdp", "cpi", "beta", "sensitivity"],
        "expect_metrics": ["revenue_b", "beta_nm_cpi_12q", "beta_nm_ffr_12q"],
        "companies": ["Apple", "AAPL"]
    },
    {
        "category": "Layer 3: Full Q",
        "query": "everything including betas for Microsoft Q3 2023",
        "expect_keywords": ["revenue", "microsoft", "beta"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Microsoft", "MSFT"]
    },
    {
        "category": "Layer 3: Full Q",
        "query": "complete picture with sensitivity for Google Q2 2023",
        "expect_keywords": ["revenue", "google", "sensitivity"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Google", "GOOGL"]
    },
    {
        "category": "Layer 3: Full Q",
        "query": "Amazon full analysis with betas Q3 2023",
        "expect_keywords": ["revenue", "amazon", "beta"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Amazon", "AMZN"]
    },
    
    # Annual with sensitivity
    {
        "category": "Layer 3: Full A",
        "query": "show Apple full analysis 2023",
        "expect_keywords": ["revenue", "apple", "gdp", "cpi", "beta", "2023"],
        "expect_metrics": ["revenue_b", "beta_nm_cpi_annual"],
        "companies": ["Apple", "AAPL"]
    },
    {
        "category": "Layer 3: Full A",
        "query": "everything including betas for Microsoft 2023",
        "expect_keywords": ["revenue", "microsoft", "beta", "2023"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Microsoft", "MSFT"]
    },
    {
        "category": "Layer 3: Full A",
        "query": "complete picture with sensitivity for Amazon 2023",
        "expect_keywords": ["revenue", "amazon", "sensitivity", "2023"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Amazon", "AMZN"]
    },
    {
        "category": "Layer 3: Full A",
        "query": "Meta full view with betas 2023",
        "expect_keywords": ["revenue", "meta", "beta", "2023"],
        "expect_metrics": ["revenue_b"],
        "companies": ["Meta", "META"]
    },
]


def check_response_quality(response: str, test: dict) -> dict:
    """
    Check response quality against expected criteria
    Returns dict with checks
    """
    response_lower = response.lower()
    
    checks = {
        "has_response": len(response) > 50,
        "natural_language": any(word in response_lower for word in ["reported", "had", "with", "was", "showed"]),
        "has_company": any(company.lower() in response_lower for company in test["companies"]),
        "has_keywords": sum(1 for kw in test["expect_keywords"] if kw.lower() in response_lower),
        "readable": not any(word in response_lower for word in ["error", "failed", "exception", "none"]),
    }
    
    checks["quality_score"] = (
        (checks["has_response"] * 20) +
        (checks["natural_language"] * 20) +
        (checks["has_company"] * 20) +
        (min(checks["has_keywords"], 3) * 10) +  # Up to 30 points for keywords
        (checks["readable"] * 10)
    )
    
    checks["passed"] = checks["quality_score"] >= 70
    
    return checks


async def test_comprehensive():
    """Run comprehensive test suite"""
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("COMPREHENSIVE COMBINED VIEWS TEST")
    print("="*120)
    print(f"Testing {len(TEST_QUERIES)} queries across all layers and periods")
    print("="*120)
    
    results = {
        "Layer 1: Core Q": {"pass": 0, "total": 0, "details": []},
        "Layer 1: Core A": {"pass": 0, "total": 0, "details": []},
        "Layer 2: Macro Q": {"pass": 0, "total": 0, "details": []},
        "Layer 2: Macro A": {"pass": 0, "total": 0, "details": []},
        "Layer 3: Full Q": {"pass": 0, "total": 0, "details": []},
        "Layer 3: Full A": {"pass": 0, "total": 0, "details": []},
    }
    
    for i, test in enumerate(TEST_QUERIES, 1):
        category = test["category"]
        query = test["query"]
        
        print(f"\n{'='*120}")
        print(f"[{i}/{len(TEST_QUERIES)}] [{category}]")
        print(f"Query: {query}")
        print("-"*120)
        
        results[category]["total"] += 1
        
        try:
            response = await cfo_agent_graph.run(query)
            
            # Check response quality
            quality = check_response_quality(response, test)
            
            if quality["passed"]:
                status = "✅ PASS"
                results[category]["pass"] += 1
            else:
                status = "❌ FAIL"
            
            print(f"{status} (Quality Score: {quality['quality_score']}/100)")
            print(f"Response: {response[:200]}...")
            
            # Quality details
            print(f"\nQuality Checks:")
            print(f"  • Natural Language: {'✅' if quality['natural_language'] else '❌'}")
            print(f"  • Company Mentioned: {'✅' if quality['has_company'] else '❌'}")
            print(f"  • Keywords Found: {quality['has_keywords']}/{len(test['expect_keywords'])}")
            print(f"  • Readable: {'✅' if quality['readable'] else '❌'}")
            
            results[category]["details"].append({
                "query": query,
                "passed": quality["passed"],
                "score": quality["quality_score"],
                "response": response[:100]
            })
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results[category]["details"].append({
                "query": query,
                "passed": False,
                "score": 0,
                "error": str(e)[:100]
            })
    
    await db_pool.close()
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    
    print("\n" + "="*120)
    print("DETAILED SUMMARY BY CATEGORY")
    print("="*120)
    
    total_pass = 0
    total_tests = 0
    
    for category, stats in results.items():
        total_pass += stats["pass"]
        total_tests += stats["total"]
        pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 60 else "❌"
        
        print(f"\n{status} {category}")
        print(f"   Pass Rate: {stats['pass']}/{stats['total']} ({pass_rate:.1f}%)")
        
        # Show failed queries
        failed = [d for d in stats["details"] if not d["passed"]]
        if failed:
            print(f"   Failed Queries:")
            for f in failed:
                print(f"     - {f['query'][:80]}...")
    
    # Overall summary
    print("\n" + "="*120)
    print("OVERALL SUMMARY")
    print("="*120)
    
    overall_rate = (total_pass / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'Category':<25} {'Tests':<10} {'Passed':<10} {'Pass Rate':<15} {'Status'}")
    print("-"*75)
    
    for category, stats in results.items():
        pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status_icon = "✅" if pass_rate >= 80 else "⚠️" if pass_rate >= 60 else "❌"
        print(f"{category:<25} {stats['total']:<10} {stats['pass']:<10} {pass_rate:>6.1f}%        {status_icon}")
    
    print("-"*75)
    print(f"{'TOTAL':<25} {total_tests:<10} {total_pass:<10} {overall_rate:>6.1f}%")
    
    print("\n" + "="*120)
    if overall_rate >= 90:
        print("🎉 EXCELLENT! Combined views are working perfectly!")
    elif overall_rate >= 75:
        print("✅ GOOD! Most combined queries working well. Minor issues to address.")
    elif overall_rate >= 60:
        print("⚠️  NEEDS WORK! Several queries failing. Review issues above.")
    else:
        print("❌ CRITICAL! Major issues with combined views. Immediate attention needed.")
    print("="*120)
    
    return results


if __name__ == "__main__":
    asyncio.run(test_comprehensive())
