"""Test the formatter directly with actual stock data"""
import asyncio
import pandas as pd
from formatter import ResponseFormatter
from db.pool import db_pool

async def test_formatter():
    await db_pool.initialize()
    
    # Get actual stock data for Apple 2023
    query = """
    SELECT c.ticker, c.name, sa.fiscal_year, sa.avg_open_price_annual, sa.avg_close_price_annual,
           sa.high_price_annual, sa.low_price_annual, sa.avg_price_annual
    FROM mv_stock_prices_annual sa
    JOIN dim_company c USING (company_id)
    WHERE c.ticker = 'AAPL' AND sa.fiscal_year = 2023
    """
    
    result = await db_pool.execute_one(query)
    
    if result:
        print("=== DATA FROM DATABASE ===")
        print(f"Columns: {list(result.keys())}")
        print(f"Values: {dict(result)}")
        
        # Convert to list of dicts (like real execution)
        results = [dict(result)]
        
        # Test different questions
        questions = [
            "show apple opening price for 2023",
            "show apple opening and closing price for 2023",
            "show high and low price for apple 2023"
        ]
        
        formatter = ResponseFormatter()
        
        for question in questions:
            print(f"\n=== TESTING: {question} ===")
            
            # Extract metrics
            metrics = formatter._extract_requested_metrics(question)
            print(f"Detected metrics: {metrics}")
            
            # Create context
            context = {
                'question': question,
                'intent': 'stock_price_annual',
                'citation_line': 'Sources: Test'
            }
            
            # Format response
            response = await formatter.format_response(results, context, {})
            print(f"Response: {response}")
    
    await db_pool.close()

if __name__ == "__main__":
    asyncio.run(test_formatter())
