#!/usr/bin/env python
"""Fresh test - no imports until runtime"""

if __name__ == "__main__":
    import asyncio
    import sys
    
    async def test():
        # Import at runtime to avoid any caching
        from graph import cfo_agent_graph
        from db.pool import db_pool
        from db.whitelist import load_schema_cache
        from db.resolve import load_ticker_cache
        
        await db_pool.initialize()
        await load_schema_cache()
        await load_ticker_cache()
        
        print("\n" + "="*100)
        print("FRESH TEST - ALL 9 QUARTERLY RATIOS")
        print("="*100)
        
        tests = [
            ("Gross Margin", "show Apple gross margin for Q2 2023"),
            ("ROE", "show Apple ROE for Q2 2023"),
            ("ROA", "show Apple ROA for Q2 2023"),
            ("Debt-to-Equity", "show Apple debt to equity for Q2 2023"),
            ("Debt-to-Assets", "show Apple debt to assets for Q2 2023"),
            ("R&D Intensity", "show Apple R&D intensity for Q2 2023"),
            ("SG&A Intensity", "show Apple SG&A intensity for Q2 2023"),
        ]
        
        for name, query in tests:
            print(f"\n{name}:")
            print(f"  Query: {query}")
            result = await cfo_agent_graph.run(query)
            first_line = result.split('\n')[0] if result else "No result"
            
            if "No results" in first_line or "No data" in first_line:
                print(f"  ❌ {first_line}")
            else:
                print(f"  ✅ {first_line}")
        
        await db_pool.close()
    
    asyncio.run(test())
