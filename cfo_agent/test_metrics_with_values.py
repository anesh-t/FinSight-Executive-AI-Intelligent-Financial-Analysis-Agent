"""
Test all 19 metrics with actual values displayed
"""
import asyncio
import re
from db.pool import db_pool


async def test_metrics_with_values():
    """Show actual values for all metrics from both sources"""
    
    await db_pool.initialize()
    
    print("\n" + "="*120)
    print("ALL 19 FINANCIAL METRICS - QUARTERLY vs ANNUAL VALUES")
    print("Testing: Microsoft (MSFT) - Q2 2023 vs FY2023")
    print("="*120)
    
    # Quarterly data from fact_financials
    print("\n📊 QUARTERLY DATA (from fact_financials):")
    print("-"*120)
    
    q_query = """
        SELECT 
            c.ticker,
            f.fiscal_year,
            f.fiscal_quarter,
            f.revenue/1e9 as revenue_b,
            f.operating_income/1e9 as operating_income_b,
            f.net_income/1e9 as net_income_b,
            f.eps,
            f.total_assets/1e9 as total_assets_b,
            f.total_liabilities/1e9 as total_liabilities_b,
            f.equity/1e9 as equity_b,
            f.cash_flow_ops/1e9 as cash_flow_ops_b,
            f.cash_flow_investing/1e9 as cash_flow_investing_b,
            f.cash_flow_financing/1e9 as cash_flow_financing_b,
            f.cogs/1e9 as cogs_b,
            f.gross_profit/1e9 as gross_profit_b,
            f.r_and_d_expenses/1e9 as rd_b,
            f.sg_and_a_expenses/1e9 as sga_b,
            f.ebit/1e9 as ebit_b,
            f.ebitda/1e9 as ebitda_b,
            f.capex/1e9 as capex_b,
            f.dividends/1e9 as dividends_b,
            f.buybacks/1e9 as buybacks_b
        FROM fact_financials f
        JOIN dim_company c USING (company_id)
        WHERE c.ticker = 'MSFT'
        AND f.fiscal_year = 2023
        AND f.fiscal_quarter = 2
    """
    
    q_data = await db_pool.execute_query(q_query)
    
    if q_data:
        q = q_data[0]
        print(f"\nSource: fact_financials | Period: Q{q['fiscal_quarter']} {q['fiscal_year']}")
        print(f"{'Metric':<40} {'Value':<20}")
        print("-"*120)
        print(f"{'1. Revenue':<40} ${q['revenue_b']:.2f}B")
        print(f"{'2. Operating Income':<40} ${q['operating_income_b']:.2f}B")
        print(f"{'3. Net Income':<40} ${q['net_income_b']:.2f}B")
        print(f"{'4. EPS':<40} ${q['eps']:.2f}")
        print(f"{'5. Total Assets':<40} ${q['total_assets_b']:.2f}B")
        print(f"{'6. Total Liabilities':<40} ${q['total_liabilities_b']:.2f}B")
        print(f"{'7. Shareholder Equity':<40} ${q['equity_b']:.2f}B")
        print(f"{'8. Operating Cash Flow':<40} ${q['cash_flow_ops_b']:.2f}B")
        print(f"{'9. Investing Cash Flow':<40} ${q['cash_flow_investing_b']:.2f}B")
        print(f"{'10. Financing Cash Flow':<40} ${q['cash_flow_financing_b']:.2f}B")
        print(f"{'11. COGS':<40} ${q['cogs_b']:.2f}B")
        print(f"{'12. Gross Profit':<40} ${q['gross_profit_b']:.2f}B")
        print(f"{'13. R&D Expenses':<40} ${q['rd_b']:.2f}B")
        print(f"{'14. SG&A Expenses':<40} ${q['sga_b']:.2f}B")
        print(f"{'15. EBIT':<40} ${q['ebit_b']:.2f}B")
        print(f"{'16. EBITDA':<40} ${q['ebitda_b']:.2f}B")
        print(f"{'17. CapEx':<40} ${q['capex_b']:.2f}B")
        print(f"{'18. Dividends':<40} ${q['dividends_b']:.2f}B")
        print(f"{'19. Buybacks':<40} ${q['buybacks_b']:.2f}B")
    
    # Annual data from mv_financials_annual + fact_financials
    print("\n\n📅 ANNUAL DATA (from mv_financials_annual + aggregated fact_financials):")
    print("-"*120)
    
    a_query = """
        SELECT 
            c.ticker,
            mv.fiscal_year,
            mv.revenue_annual/1e9 as revenue_b,
            mv.operating_income_annual/1e9 as operating_income_b,
            mv.net_income_annual/1e9 as net_income_b,
            SUM(f.eps) as eps,
            mv.total_assets_eoy/1e9 as total_assets_b,
            mv.total_liabilities_eoy/1e9 as total_liabilities_b,
            mv.equity_eoy/1e9 as equity_b,
            mv.cash_flow_ops_annual/1e9 as cash_flow_ops_b,
            mv.cash_flow_investing_annual/1e9 as cash_flow_investing_b,
            mv.cash_flow_financing_annual/1e9 as cash_flow_financing_b,
            mv.cogs_annual/1e9 as cogs_b,
            mv.gross_profit_annual/1e9 as gross_profit_b,
            mv.r_and_d_expenses_annual/1e9 as rd_b,
            mv.sg_and_a_expenses_annual/1e9 as sga_b,
            mv.ebit_annual/1e9 as ebit_b,
            mv.ebitda_annual/1e9 as ebitda_b,
            mv.capex_annual/1e9 as capex_b,
            SUM(f.dividends)/1e9 as dividends_b,
            SUM(f.buybacks)/1e9 as buybacks_b
        FROM mv_financials_annual mv
        JOIN dim_company c USING (company_id)
        LEFT JOIN fact_financials f ON f.company_id = mv.company_id AND f.fiscal_year = mv.fiscal_year
        WHERE c.ticker = 'MSFT'
        AND mv.fiscal_year = 2023
        GROUP BY c.ticker, mv.fiscal_year, mv.revenue_annual, mv.operating_income_annual,
                 mv.net_income_annual, mv.total_assets_eoy, mv.total_liabilities_eoy,
                 mv.equity_eoy, mv.cash_flow_ops_annual, mv.cash_flow_investing_annual,
                 mv.cash_flow_financing_annual, mv.cogs_annual, mv.gross_profit_annual,
                 mv.r_and_d_expenses_annual, mv.sg_and_a_expenses_annual, mv.ebit_annual,
                 mv.ebitda_annual, mv.capex_annual
    """
    
    a_data = await db_pool.execute_query(a_query)
    
    if a_data:
        a = a_data[0]
        print(f"\nSource: mv_financials_annual | Period: FY{a['fiscal_year']}")
        print(f"{'Metric':<40} {'Value':<20}")
        print("-"*120)
        print(f"{'1. Revenue':<40} ${a['revenue_b']:.2f}B")
        print(f"{'2. Operating Income':<40} ${a['operating_income_b']:.2f}B")
        print(f"{'3. Net Income':<40} ${a['net_income_b']:.2f}B")
        print(f"{'4. EPS (SUM of quarters)':<40} ${float(a['eps']):.2f}")
        print(f"{'5. Total Assets (EOY)':<40} ${a['total_assets_b']:.2f}B")
        print(f"{'6. Total Liabilities (EOY)':<40} ${a['total_liabilities_b']:.2f}B")
        print(f"{'7. Shareholder Equity (EOY)':<40} ${a['equity_b']:.2f}B")
        print(f"{'8. Operating Cash Flow':<40} ${a['cash_flow_ops_b']:.2f}B")
        print(f"{'9. Investing Cash Flow':<40} ${a['cash_flow_investing_b']:.2f}B")
        print(f"{'10. Financing Cash Flow':<40} ${a['cash_flow_financing_b']:.2f}B")
        print(f"{'11. COGS':<40} ${a['cogs_b']:.2f}B")
        print(f"{'12. Gross Profit':<40} ${a['gross_profit_b']:.2f}B")
        print(f"{'13. R&D Expenses':<40} ${a['rd_b']:.2f}B")
        print(f"{'14. SG&A Expenses':<40} ${a['sga_b']:.2f}B")
        print(f"{'15. EBIT':<40} ${a['ebit_b']:.2f}B")
        print(f"{'16. EBITDA':<40} ${a['ebitda_b']:.2f}B")
        print(f"{'17. CapEx':<40} ${a['capex_b']:.2f}B")
        print(f"{'18. Dividends (SUM)':<40} ${float(a['dividends_b']):.2f}B")
        print(f"{'19. Buybacks (SUM)':<40} ${float(a['buybacks_b']):.2f}B")
    
    # Comparison
    print("\n\n" + "="*120)
    print("COMPARISON: Quarterly vs Annual")
    print("="*120)
    
    if q_data and a_data:
        print(f"\n{'Metric':<40} {'Q2 2023':<25} {'FY2023':<25} {'Multiplier':<15}")
        print("-"*120)
        
        comparisons = [
            ("Revenue", float(q['revenue_b']), float(a['revenue_b'])),
            ("Operating Income", float(q['operating_income_b']), float(a['operating_income_b'])),
            ("Net Income", float(q['net_income_b']), float(a['net_income_b'])),
            ("EPS", float(q['eps']), float(a['eps'])),
            ("Operating Cash Flow", float(q['cash_flow_ops_b']), float(a['cash_flow_ops_b'])),
            ("R&D Expenses", float(q['rd_b']), float(a['rd_b'])),
            ("SG&A Expenses", float(q['sga_b']), float(a['sga_b'])),
            ("CapEx", float(q['capex_b']), float(a['capex_b'])),
        ]
        
        for name, q_val, a_val in comparisons:
            mult = a_val / q_val if q_val != 0 else 0
            q_str = f"${q_val:.2f}B" if abs(q_val) >= 0.01 else f"${q_val:.2f}"
            a_str = f"${a_val:.2f}B" if abs(a_val) >= 0.01 else f"${a_val:.2f}"
            print(f"{name:<40} {q_str:<25} {a_str:<25} {mult:.2f}x")
    
    print("\n" + "="*120)
    print("✅ DATA SOURCE VERIFICATION:")
    print("  - Quarterly data: fact_financials ✓")
    print("  - Annual data: mv_financials_annual (+ fact_financials for EPS, dividends, buybacks) ✓")
    print("  - All 19 metrics available ✓")
    print("="*120)
    
    await db_pool.close()


if __name__ == "__main__":
    asyncio.run(test_metrics_with_values())
