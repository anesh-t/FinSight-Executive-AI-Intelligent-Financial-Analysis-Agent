"""Debug the execution flow to see what's failing"""
import asyncio
from db.pool import db_pool
from sql_exec import SQLExecutor
import json

async def debug():
    await db_pool.initialize()
    
    # Load template
    with open('catalog/templates.json', 'r') as f:
        templates = json.load(f)['templates']
    
    quarter_snapshot = templates['quarter_snapshot']
    
    print("\n" + "="*100)
    print("DEBUGGING QUARTER_SNAPSHOT EXECUTION")
    print("="*100)
    
    print(f"\nTemplate Surface: {quarter_snapshot['surface']}")
    print(f"SQL Length: {len(quarter_snapshot['sql'])} characters")
    
    # Test the SQL directly
    sql = quarter_snapshot['sql']
    params = {'ticker': 'AAPL', 'fy': 2023, 'fq': 2, 'limit': 1}
    
    print(f"\nParameters: {params}")
    print(f"\nSQL (first 300 chars):")
    print(sql[:300])
    
    # Try executing via SQLExecutor
    executor = SQLExecutor()
    
    try:
        print(f"\n\nAttempting execution via SQLExecutor...")
        results = await executor.execute(sql, params)
        
        if results:
            print(f"✅ SUCCESS! Got {len(results)} rows")
            print(f"\nColumns in result:")
            if results:
                for key in results[0].keys():
                    print(f"  {key}")
                
                # Check for ratio columns
                ratio_cols = ['gross_margin', 'roe', 'roa', 'debt_to_equity', 'debt_to_assets', 'rnd_to_revenue', 'sgna_to_revenue']
                print(f"\nRatio columns status:")
                for col in ratio_cols:
                    if col in results[0]:
                        val = results[0][col]
                        if val is not None:
                            print(f"  ✅ {col:<25} {val}")
                        else:
                            print(f"  ⚠️  {col:<25} NULL")
                    else:
                        print(f"  ❌ {col:<25} MISSING")
        else:
            print(f"⚠️  Query succeeded but returned 0 rows")
            
    except Exception as e:
        print(f"❌ EXECUTION FAILED")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"\nFull traceback:")
        traceback.print_exc()
    
    await db_pool.close()

asyncio.run(debug())
