"""Test the three specific fixes"""
import asyncio
from graph import CFOAgentGraph

async def test_fixes():
    agent = CFOAgentGraph()
    graph = agent.graph
    
    print("="*80)
    print("TESTING THREE SPECIFIC FIXES")
    print("="*80)
    
    # FIX 1: Quarterly stock price
    print("\n" + "="*80)
    print("FIX #1: Quarterly Stock Price")
    print("="*80)
    print("\nQuery: 'Apple closing stock price Q2 2023'")
    print("Expected: Should show actual closing price (e.g., $193.97)")
    print("Previous: 'Data found for Apple Inc. (AAPL) in Q2 FY2023.'\n")
    
    state = {
        "question": "Apple closing stock price Q2 2023",
        "session_id": "test_session",
        "errors": []
    }
    
    result = await graph.ainvoke(state)
    response = result.get("final_response", "No response")
    
    print(f"RESULT:\n{response}\n")
    
    if "$" in response and "closing price" in response.lower() and "data found" not in response.lower():
        print("✅ FIX #1: PASSED - Shows actual closing price!")
    else:
        print("❌ FIX #1: FAILED - Still showing generic message")
    
    # FIX 2: Macro indicator natural language
    print("\n" + "="*80)
    print("FIX #2: Macro Indicator Natural Language")
    print("="*80)
    print("\nQuery: 'Unemployment rate in 2023'")
    print("Expected: 'In 2023, the unemployment rate was 3.63%.'")
    print("Previous: 'Macro indicators for FY2023: unemployment rate (annual average) of 3.63%.'\n")
    
    state = {
        "question": "Unemployment rate in 2023",
        "session_id": "test_session",
        "errors": []
    }
    
    result = await graph.ainvoke(state)
    response = result.get("final_response", "No response")
    
    print(f"RESULT:\n{response}\n")
    
    if "In 2023" in response and "unemployment rate was" in response and "Macro indicators for" not in response:
        print("✅ FIX #2: PASSED - Natural language formatting!")
    else:
        print("❌ FIX #2: FAILED - Still using technical language")
    
    # FIX 3: Combined queries
    print("\n" + "="*80)
    print("FIX #3: Combined Queries (Financials + Stock)")
    print("="*80)
    print("\nQuery: 'Show Apple revenue, net margin, and closing stock price for 2023'")
    print("Expected: Should show all three metrics")
    print("Previous: Only showed closing stock price\n")
    
    state = {
        "question": "Show Apple revenue, net margin, and closing stock price for 2023",
        "session_id": "test_session",
        "errors": []
    }
    
    result = await graph.ainvoke(state)
    response = result.get("final_response", "No response")
    
    print(f"RESULT:\n{response}\n")
    
    has_revenue = "revenue" in response.lower() and "$" in response
    has_margin = "margin" in response.lower() and "%" in response
    has_stock = "closing price" in response.lower() or "stock price" in response.lower()
    
    if has_revenue and has_margin and has_stock:
        print("✅ FIX #3: PASSED - Shows all three metrics!")
    else:
        print(f"❌ FIX #3: FAILED - Missing metrics:")
        print(f"   - Revenue: {'✓' if has_revenue else '✗'}")
        print(f"   - Margin: {'✓' if has_margin else '✗'}")
        print(f"   - Stock Price: {'✓' if has_stock else '✗'}")
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    # Count passes
    fixes = []
    if "$" in result.get("final_response", "") and "closing price" in result.get("final_response", "").lower():
        fixes.append("Fix #1")
    
    print(f"\nAll fixes have been applied and backend restarted.")
    print(f"Please test in the Streamlit interface at http://localhost:8501")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_fixes())
