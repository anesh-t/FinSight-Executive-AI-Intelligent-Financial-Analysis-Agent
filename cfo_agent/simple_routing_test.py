"""
Simple test to see what templates are available and test routing
"""
import asyncio
import json
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test():
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    # Load templates to see what's available
    with open('catalog/templates.json', 'r') as f:
        templates = json.load(f)
    
    print("\n" + "="*100)
    print("AVAILABLE TEMPLATES FOR QUARTERLY QUERIES")
    print("="*100)
    
    quarterly_templates = []
    for name, template in templates.items():
        if 'fq' in template.get('params', []) or 'quarter' in template.get('description', '').lower():
            quarterly_templates.append((name, template.get('description', '')))
    
    print("\nTemplates with quarterly support:")
    for name, desc in quarterly_templates:
        print(f"\n  {name}:")
        print(f"    {desc[:150]}...")
    
    # Test which template should match debt/intensity queries
    print("\n" + "="*100)
    print("KEYWORD ANALYSIS FOR DEBT/INTENSITY QUERIES")
    print("="*100)
    
    test_keywords = [
        ("debt to equity", "Should match quarterly_ratios or quarter_snapshot?"),
        ("debt to assets", "Should match quarterly_ratios or quarter_snapshot?"),
        ("R&D intensity", "Should match quarterly_ratios?"),
        ("SG&A intensity", "Should match quarterly_ratios?"),
    ]
    
    for keyword, question in test_keywords:
        print(f"\n  '{keyword}': {question}")
        
        # Check which template descriptions contain relevant keywords
        matches = []
        for name, template in templates.items():
            desc = template.get('description', '').lower()
            if any(k in desc for k in keyword.lower().split()):
                matches.append(name)
        
        if matches:
            print(f"    Potential matches: {', '.join(matches)}")
        else:
            print(f"    ⚠️  No template descriptions contain '{keyword}' keywords!")
    
    # Check quarter_snapshot vs quarterly_ratios
    print("\n" + "="*100)
    print("COMPARISON: quarter_snapshot vs quarterly_ratios")
    print("="*100)
    
    if 'quarter_snapshot' in templates:
        print("\n  quarter_snapshot:")
        print(f"    Description: {templates['quarter_snapshot']['description']}")
        print(f"    Surface: {templates['quarter_snapshot']['surface']}")
    
    if 'quarterly_ratios' in templates:
        print("\n  quarterly_ratios:")
        print(f"    Description: {templates['quarterly_ratios']['description']}")
        print(f"    Surface: {templates['quarterly_ratios']['surface']}")
    
    print("\n" + "="*100)
    print("RECOMMENDATION:")
    print("="*100)
    print("\nThe issue is likely that:")
    print("  1. 'quarter_snapshot' is more generic and gets selected first")
    print("  2. 'quarterly_ratios' needs stronger keyword signals (debt, intensity, ratio)")
    print("  3. OR 'quarter_snapshot' needs to be updated to fetch from fact_ratios")
    print("\nBest solution: Update quarter_snapshot to JOIN with fact_ratios for complete data")
    
    await db_pool.close()

asyncio.run(test())
