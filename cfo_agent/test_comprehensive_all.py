"""
Comprehensive End-to-End Test
Tests all categories: Financials, Ratios, Stock Prices, Macro Indicators, Macro Sensitivity
Both Quarterly and Annual data
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache

async def test_all_categories():
    """Test all data categories comprehensively"""
    
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*120)
    print("COMPREHENSIVE CFO AGENT TEST - ALL CATEGORIES")
    print("="*120)
    
    test_cases = [
        # ========================================================================================
        # CATEGORY 1: FINANCIALS (Quarterly & Annual)
        # ========================================================================================
        ("Financials Q", "show Apple revenue Q2 2023"),
        ("Financials Q", "show Microsoft net income Q3 2023"),
        ("Financials Q", "show Google R&D expenses Q2 2023"),
        ("Financials A", "show Apple revenue 2023"),
        ("Financials A", "show Amazon operating income 2023"),
        ("Financials A", "show Meta capex 2023"),
        
        # ========================================================================================
        # CATEGORY 2: RATIOS (Quarterly & Annual)
        # ========================================================================================
        ("Ratios Q", "show Apple gross margin Q2 2023"),
        ("Ratios Q", "show Microsoft ROE Q3 2023"),
        ("Ratios Q", "show Google debt to equity Q2 2023"),
        ("Ratios Q", "show Amazon R&D intensity Q3 2023"),
        ("Ratios A", "show Apple net margin 2023"),
        ("Ratios A", "show Microsoft ROA 2023"),
        ("Ratios A", "show Meta operating margin 2023"),
        
        # ========================================================================================
        # CATEGORY 3: STOCK PRICES (Quarterly & Annual)
        # ========================================================================================
        ("Stock Q", "show Apple stock price Q2 2023"),
        ("Stock Q", "show Microsoft stock return Q3 2023"),
        ("Stock Q", "show Google volatility Q2 2023"),
        ("Stock A", "show Apple stock price 2023"),
        ("Stock A", "show Amazon annual return 2023"),
        ("Stock A", "show Meta stock performance 2023"),
        
        # ========================================================================================
        # CATEGORY 4: MACRO INDICATORS (Quarterly & Annual)
        # ========================================================================================
        ("Macro Q", "show GDP Q2 2023"),
        ("Macro Q", "show inflation Q3 2023"),
        ("Macro Q", "show unemployment rate Q2 2023"),
        ("Macro Q", "show Fed rate Q3 2023"),
        ("Macro A", "show GDP 2023"),
        ("Macro A", "show CPI 2023"),
        ("Macro A", "show unemployment rate 2023"),
        
        # ========================================================================================
        # CATEGORY 5: MACRO SENSITIVITY (Quarterly & Annual)
        # ========================================================================================
        ("Sensitivity Q", "show Apple macro sensitivity Q2 2023"),
        ("Sensitivity Q", "show Microsoft beta to inflation Q3 2023"),
        ("Sensitivity Q", "show Google beta to Fed rate Q2 2023"),
        ("Sensitivity A", "show Apple macro sensitivity 2023"),
        ("Sensitivity A", "show Amazon beta to inflation 2023"),
        ("Sensitivity A", "show Meta sensitivity to CPI 2023"),
    ]
    
    results = []
    category_stats = {}
    
    for category, query in test_cases:
        print(f"\n{'='*120}")
        print(f"[{category}] {query}")
        print("-"*120)
        
        try:
            result = await cfo_agent_graph.run(query)
            
            # Get first line
            first_line = result.split('\n')[0] if result else "No response"
            
            # Determine success based on category
            success = False
            if category.startswith("Financials"):
                success = any(word in first_line.lower() for word in ['revenue', 'income', 'expenses', 'reported', 'billion'])
            elif category.startswith("Ratios"):
                success = any(word in first_line.lower() for word in ['margin', 'roe', 'roa', 'debt', 'intensity', 'reported'])
            elif category.startswith("Stock"):
                success = any(word in first_line.lower() for word in ['stock price', 'price of', 'return', 'volatility', 'averaged'])
            elif category.startswith("Macro"):
                success = any(word in first_line.lower() for word in ['gdp', 'cpi', 'inflation', 'unemployment', 'fed', 'macro indicator'])
            elif category.startswith("Sensitivity"):
                success = any(word in first_line.lower() for word in ['beta', 'sensitivity', 'macro sensitivity'])
            
            status = "✅ PASS" if success else "❌ FAIL"
            
            print(f"{status}")
            print(f"Response: {first_line[:100]}...")
            
            results.append({
                'category': category,
                'query': query,
                'status': status,
                'response': first_line
            })
            
            # Track category stats
            if category not in category_stats:
                category_stats[category] = {'pass': 0, 'fail': 0}
            
            if success:
                category_stats[category]['pass'] += 1
            else:
                category_stats[category]['fail'] += 1
            
        except Exception as e:
            print(f"❌ ERROR")
            print(f"Error: {str(e)[:100]}")
            results.append({
                'category': category,
                'query': query,
                'status': "❌ ERROR",
                'response': str(e)[:100]
            })
            
            if category not in category_stats:
                category_stats[category] = {'pass': 0, 'fail': 0}
            category_stats[category]['fail'] += 1
    
    # Summary by Category
    print("\n" + "="*120)
    print("SUMMARY BY CATEGORY")
    print("="*120)
    
    for category in sorted(set(r['category'] for r in results)):
        stats = category_stats.get(category, {'pass': 0, 'fail': 0})
        total = stats['pass'] + stats['fail']
        pct = (stats['pass'] / total * 100) if total > 0 else 0
        
        status_icon = "✅" if pct == 100 else "⚠️" if pct >= 75 else "❌"
        print(f"{status_icon} {category:<20} {stats['pass']}/{total} passing ({pct:.1f}%)")
    
    # Overall Summary
    print("\n" + "="*120)
    print("OVERALL SUMMARY")
    print("="*120)
    
    total_pass = sum(1 for r in results if "✅" in r['status'])
    total = len(results)
    pct = (total_pass / total * 100) if total > 0 else 0
    
    print(f"\n{'Category':<20} {'Queries':<10} {'Status':<15} {'Pass Rate':<15}")
    print("-"*60)
    
    categories = ['Financials Q', 'Financials A', 'Ratios Q', 'Ratios A', 
                  'Stock Q', 'Stock A', 'Macro Q', 'Macro A', 
                  'Sensitivity Q', 'Sensitivity A']
    
    for cat in categories:
        cat_results = [r for r in results if r['category'] == cat]
        cat_pass = sum(1 for r in cat_results if "✅" in r['status'])
        cat_total = len(cat_results)
        cat_pct = (cat_pass / cat_total * 100) if cat_total > 0 else 0
        
        status_icon = "✅" if cat_pct == 100 else "⚠️" if cat_pct >= 75 else "❌"
        print(f"{cat:<20} {cat_total:<10} {status_icon} {cat_pct:.1f}%       {cat_pass}/{cat_total}")
    
    print("\n" + "="*120)
    print(f"OVERALL: {total_pass}/{total} tests passing ({pct:.1f}%)")
    print("="*120)
    
    if pct == 100:
        print("\n🎉 ALL TESTS PASSING! CFO AGENT IS FULLY OPERATIONAL! 🎉")
    elif pct >= 90:
        print("\n✅ EXCELLENT! Most tests passing, minor fixes needed")
    elif pct >= 75:
        print("\n⚠️ GOOD PROGRESS! Some categories need attention")
    else:
        print("\n❌ NEEDS WORK! Multiple categories failing")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(test_all_categories())
