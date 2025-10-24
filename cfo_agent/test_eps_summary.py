"""
Comprehensive EPS summary for all companies
"""
import asyncio
from graph import cfo_agent_graph
from db.pool import db_pool
from db.whitelist import load_schema_cache
from db.resolve import load_ticker_cache


async def test_eps_summary():
    """Get EPS data for all major companies"""
    
    # Initialize
    await db_pool.initialize()
    await load_schema_cache()
    await load_ticker_cache()
    
    print("\n" + "="*100)
    print("EARNINGS PER SHARE (EPS) SUMMARY - ALL COMPANIES")
    print("="*100)
    
    # Test companies
    companies = [
        ("Apple", "AAPL"),
        ("Microsoft", "MSFT"),
        ("Google/Alphabet", "GOOG"),
        ("Amazon", "AMZN"),
        ("Meta/Facebook", "META"),
        ("Tesla", "TSLA"),
        ("Nvidia", "NVDA"),
        ("Netflix", "NFLX")
    ]
    
    # Years to test
    years = [2023, 2022, 2021]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    
    eps_data = {}
    
    for company_name, ticker in companies:
        print(f"\n{'='*100}")
        print(f"📊 {company_name.upper()} ({ticker})")
        print(f"{'='*100}")
        
        company_eps = {
            'annual': {},
            'quarterly': {}
        }
        
        # Get Annual EPS
        print(f"\n📅 ANNUAL EPS:")
        print("-"*100)
        for year in years:
            query = f"show {ticker} EPS for {year}"
            try:
                result = await cfo_agent_graph.run(query)
                
                # Extract EPS value from response
                if "EPS of $" in result:
                    eps_str = result.split("EPS of $")[1].split()[0]
                    eps_value = float(eps_str)
                    company_eps['annual'][year] = eps_value
                    print(f"  {year}: ${eps_value:.2f}")
                elif "No data" in result or "No results" in result:
                    company_eps['annual'][year] = None
                    print(f"  {year}: No data")
                else:
                    company_eps['annual'][year] = "Error"
                    print(f"  {year}: Data not parsed")
            except Exception as e:
                company_eps['annual'][year] = None
                print(f"  {year}: Error - {str(e)[:50]}")
        
        # Get Quarterly EPS for 2023
        print(f"\n📊 QUARTERLY EPS (2023):")
        print("-"*100)
        for quarter in quarters:
            query = f"show {ticker} EPS for {quarter} 2023"
            try:
                result = await cfo_agent_graph.run(query)
                
                # Extract EPS value from response
                if "EPS of $" in result:
                    eps_str = result.split("EPS of $")[1].split()[0]
                    eps_value = float(eps_str)
                    company_eps['quarterly'][quarter] = eps_value
                    print(f"  {quarter}: ${eps_value:.2f}")
                elif "No data" in result or "No results" in result:
                    company_eps['quarterly'][quarter] = None
                    print(f"  {quarter}: No data")
                else:
                    company_eps['quarterly'][quarter] = "Error"
                    print(f"  {quarter}: Data not parsed")
            except Exception as e:
                company_eps['quarterly'][quarter] = None
                print(f"  {quarter}: Error - {str(e)[:50]}")
        
        eps_data[company_name] = company_eps
    
    # Summary Tables
    print("\n" + "="*100)
    print("SUMMARY TABLE - ANNUAL EPS")
    print("="*100)
    print(f"\n{'Company':<20} {'2023':<15} {'2022':<15} {'2021':<15}")
    print("-"*100)
    
    for company_name, data in eps_data.items():
        eps_2023 = f"${data['annual'].get(2023, 'N/A'):.2f}" if isinstance(data['annual'].get(2023), (int, float)) else "N/A"
        eps_2022 = f"${data['annual'].get(2022, 'N/A'):.2f}" if isinstance(data['annual'].get(2022), (int, float)) else "N/A"
        eps_2021 = f"${data['annual'].get(2021, 'N/A'):.2f}" if isinstance(data['annual'].get(2021), (int, float)) else "N/A"
        print(f"{company_name:<20} {eps_2023:<15} {eps_2022:<15} {eps_2021:<15}")
    
    print("\n" + "="*100)
    print("SUMMARY TABLE - QUARTERLY EPS (2023)")
    print("="*100)
    print(f"\n{'Company':<20} {'Q1':<12} {'Q2':<12} {'Q3':<12} {'Q4':<12}")
    print("-"*100)
    
    for company_name, data in eps_data.items():
        q1 = f"${data['quarterly'].get('Q1', 'N/A'):.2f}" if isinstance(data['quarterly'].get('Q1'), (int, float)) else "N/A"
        q2 = f"${data['quarterly'].get('Q2', 'N/A'):.2f}" if isinstance(data['quarterly'].get('Q2'), (int, float)) else "N/A"
        q3 = f"${data['quarterly'].get('Q3', 'N/A'):.2f}" if isinstance(data['quarterly'].get('Q3'), (int, float)) else "N/A"
        q4 = f"${data['quarterly'].get('Q4', 'N/A'):.2f}" if isinstance(data['quarterly'].get('Q4'), (int, float)) else "N/A"
        print(f"{company_name:<20} {q1:<12} {q2:<12} {q3:<12} {q4:<12}")
    
    # Growth Analysis
    print("\n" + "="*100)
    print("EPS GROWTH ANALYSIS (Year-over-Year)")
    print("="*100)
    print(f"\n{'Company':<20} {'2023 vs 2022':<20} {'2022 vs 2021':<20}")
    print("-"*100)
    
    for company_name, data in eps_data.items():
        eps_2023 = data['annual'].get(2023)
        eps_2022 = data['annual'].get(2022)
        eps_2021 = data['annual'].get(2021)
        
        if isinstance(eps_2023, (int, float)) and isinstance(eps_2022, (int, float)) and eps_2022 != 0:
            growth_23_22 = ((eps_2023 - eps_2022) / eps_2022) * 100
            growth_str_23_22 = f"{growth_23_22:+.1f}%"
        else:
            growth_str_23_22 = "N/A"
        
        if isinstance(eps_2022, (int, float)) and isinstance(eps_2021, (int, float)) and eps_2021 != 0:
            growth_22_21 = ((eps_2022 - eps_2021) / eps_2021) * 100
            growth_str_22_21 = f"{growth_22_21:+.1f}%"
        else:
            growth_str_22_21 = "N/A"
        
        print(f"{company_name:<20} {growth_str_23_22:<20} {growth_str_22_21:<20}")
    
    print("\n" + "="*100)
    
    await db_pool.close()
    
    return eps_data


if __name__ == "__main__":
    eps_data = asyncio.run(test_eps_summary())
