"""
Pull all EPS data directly from database for 5 companies (2019-2025, all quarters)
"""
import asyncio
from db.pool import db_pool


async def pull_all_eps_data():
    """Query database directly for all EPS data"""
    
    await db_pool.initialize()
    
    print("\n" + "="*120)
    print("COMPLETE EPS DATABASE EXTRACT - ALL COMPANIES (2019-2025)")
    print("="*120)
    
    # Query to get all EPS data
    query = """
        SELECT 
            c.ticker,
            c.name,
            f.fiscal_year,
            f.fiscal_quarter,
            f.eps
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker IN ('AAPL', 'MSFT', 'GOOG', 'AMZN', 'META')
        AND f.fiscal_year BETWEEN 2019 AND 2025
        AND f.eps IS NOT NULL
        ORDER BY c.ticker, f.fiscal_year, f.fiscal_quarter
    """
    
    results = await db_pool.execute_query(query)
    
    # Organize data by company
    company_data = {}
    for row in results:
        ticker = row['ticker']
        if ticker not in company_data:
            company_data[ticker] = {
                'name': row['name'],
                'quarters': [],
                'annual_summary': {}
            }
        
        company_data[ticker]['quarters'].append({
            'year': row['fiscal_year'],
            'quarter': row['fiscal_quarter'],
            'eps': float(row['eps'])
        })
    
    # Print detailed data for each company
    for ticker in ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META']:
        if ticker not in company_data:
            continue
            
        data = company_data[ticker]
        print(f"\n{'='*120}")
        print(f"📊 {data['name']} ({ticker})")
        print(f"{'='*120}")
        
        # Organize by year
        years_data = {}
        for q in data['quarters']:
            year = q['year']
            if year not in years_data:
                years_data[year] = {}
            years_data[year][q['quarter']] = q['eps']
        
        # Print quarterly data
        print(f"\n{'Year':<8} {'Q1':<12} {'Q2':<12} {'Q3':<12} {'Q4':<12} {'Annual Avg':<12}")
        print("-"*120)
        
        for year in sorted(years_data.keys()):
            quarters = years_data[year]
            q1 = f"${quarters.get(1, 0):.2f}" if 1 in quarters else "N/A"
            q2 = f"${quarters.get(2, 0):.2f}" if 2 in quarters else "N/A"
            q3 = f"${quarters.get(3, 0):.2f}" if 3 in quarters else "N/A"
            q4 = f"${quarters.get(4, 0):.2f}" if 4 in quarters else "N/A"
            
            # Calculate annual average
            eps_values = [quarters[q] for q in quarters if q in [1, 2, 3, 4]]
            if eps_values:
                avg = sum(eps_values) / len(eps_values)
                avg_str = f"${avg:.2f}"
            else:
                avg_str = "N/A"
            
            print(f"{year:<8} {q1:<12} {q2:<12} {q3:<12} {q4:<12} {avg_str:<12}")
    
    # Create comparison table - Annual averages
    print("\n" + "="*120)
    print("ANNUAL EPS COMPARISON (Average of all quarters)")
    print("="*120)
    
    # Calculate annual averages for each company
    annual_comparison = {}
    for ticker in ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META']:
        if ticker not in company_data:
            continue
        
        years_avg = {}
        for q in company_data[ticker]['quarters']:
            year = q['year']
            if year not in years_avg:
                years_avg[year] = []
            years_avg[year].append(q['eps'])
        
        annual_comparison[ticker] = {
            'name': company_data[ticker]['name'],
            'years': {year: sum(eps_list)/len(eps_list) for year, eps_list in years_avg.items()}
        }
    
    # Print annual comparison table
    all_years = sorted(set(year for data in annual_comparison.values() for year in data['years'].keys()))
    
    header = f"{'Company':<20} "
    for year in all_years:
        header += f"{year:<12} "
    print(f"\n{header}")
    print("-"*120)
    
    for ticker in ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META']:
        if ticker not in annual_comparison:
            continue
        
        row = f"{ticker:<20} "
        for year in all_years:
            if year in annual_comparison[ticker]['years']:
                eps = annual_comparison[ticker]['years'][year]
                row += f"${eps:<11.2f} "
            else:
                row += f"{'N/A':<12} "
        print(row)
    
    # Growth analysis
    print("\n" + "="*120)
    print("YEAR-OVER-YEAR GROWTH RATES")
    print("="*120)
    
    print(f"\n{'Company':<20} ", end="")
    for i in range(len(all_years) - 1):
        print(f"{all_years[i]}→{all_years[i+1]:<10} ", end="")
    print()
    print("-"*120)
    
    for ticker in ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META']:
        if ticker not in annual_comparison:
            continue
        
        print(f"{ticker:<20} ", end="")
        years_data = annual_comparison[ticker]['years']
        
        for i in range(len(all_years) - 1):
            curr_year = all_years[i]
            next_year = all_years[i+1]
            
            if curr_year in years_data and next_year in years_data:
                curr_eps = years_data[curr_year]
                next_eps = years_data[next_year]
                
                if curr_eps != 0:
                    growth = ((next_eps - curr_eps) / abs(curr_eps)) * 100
                    print(f"{growth:+.1f}%{' ':<8} ", end="")
                else:
                    print(f"{'N/A':<13} ", end="")
            else:
                print(f"{'N/A':<13} ", end="")
        print()
    
    # Summary statistics
    print("\n" + "="*120)
    print("SUMMARY STATISTICS")
    print("="*120)
    
    print(f"\n{'Company':<20} {'Total Qtrs':<15} {'Avg EPS':<15} {'Min EPS':<15} {'Max EPS':<15}")
    print("-"*120)
    
    for ticker in ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'META']:
        if ticker not in company_data:
            continue
        
        eps_values = [q['eps'] for q in company_data[ticker]['quarters']]
        count = len(eps_values)
        avg = sum(eps_values) / count if count > 0 else 0
        min_eps = min(eps_values) if eps_values else 0
        max_eps = max(eps_values) if eps_values else 0
        
        print(f"{ticker:<20} {count:<15} ${avg:<14.2f} ${min_eps:<14.2f} ${max_eps:<14.2f}")
    
    print("\n" + "="*120)
    print(f"Total records retrieved: {len(results)}")
    print("="*120)
    
    await db_pool.close()
    
    return company_data


if __name__ == "__main__":
    asyncio.run(pull_all_eps_data())
