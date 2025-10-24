"""
Response formatter: table + insights + provenance
"""
from typing import List, Dict
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()


class ResponseFormatter:
    """Formats query results into CFO-grade responses"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
    
    async def format_response(self, results: List[Dict], context: Dict, citations: Dict) -> str:
        """
        Format results into simple factual response
        
        Args:
            results: Query results as list of dicts
            context: Execution context with intent, params, etc.
            citations: Citation information
            
        Returns:
            Formatted response string
        """
        if not results:
            return "No data found for the specified query."
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(results)
        
        # Generate simple factual summary
        summary = self._generate_simple_summary(df, context)
        
        # Format table if multiple results
        if len(results) > 1:
            table = self._format_table(df)
            response = f"{summary}\n\n{table}"
        else:
            response = summary
        
        # Add citations
        citation_line = context.get('citation_line', '')
        if citation_line:
            response += f"\n\n{citation_line}"
        
        return response
    
    def _format_table(self, df: pd.DataFrame) -> str:
        """Format DataFrame as compact table"""
        # Limit columns if too many
        if len(df.columns) > 10:
            # Keep first 10 columns
            df = df.iloc[:, :10]
        
        # Format numbers
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32']:
                # Round to 2 decimal places
                df[col] = df[col].round(2)
        
        # Convert to string table
        table_str = df.to_string(index=False, max_rows=50)
        
        return f"```\n{table_str}\n```"
    
    def _extract_requested_metrics(self, question: str) -> set:
        """Extract which metrics were specifically requested in the question"""
        question_upper = question.upper()
        requested = set()
        
        # Revenue keywords (but NOT if asking for intensity ratios like "R&D to revenue")
        if any(word in question_upper for word in ['REVENUE', 'SALES', 'TOP LINE', 'TOPLINE']):
            # Don't add revenue if asking for intensity ratios
            if not any(pattern in question_upper for pattern in ['TO REVENUE', 'TO SALES', 'INTENSITY']):
                requested.add('revenue')
        
        # Operating income (check first to avoid conflict with generic "income")
        if any(word in question_upper for word in ['OPERATING INCOME', 'OPERATING_INCOME', 'EBIT', 'OPERATING PROFIT']):
            requested.add('operating_income')
        
        # Gross profit (check early too)
        if any(word in question_upper for word in ['GROSS PROFIT', 'GROSS_PROFIT', 'GROSS INCOME']):
            requested.add('gross_profit')
        
        # Net income keywords (be specific to avoid conflicts)
        if any(word in question_upper for word in ['NET INCOME', 'NET_INCOME', 'NET PROFIT', 'EARNINGS', 'BOTTOM LINE', 'BOTTOMLINE']):
            requested.add('net_income')
        # Catch generic "income" only if not "operating income" or "gross income"
        elif 'INCOME' in question_upper and 'OPERATING' not in question_upper and 'GROSS' not in question_upper:
            requested.add('net_income')
        # Catch generic "profit" only if not "gross profit" or "operating profit"
        elif 'PROFIT' in question_upper and 'GROSS' not in question_upper and 'OPERATING' not in question_upper:
            requested.add('net_income')
        
        # Expense keywords (but NOT if asking for intensity ratios)
        if any(word in question_upper for word in ['R&D', 'R AND D', 'R_AND_D', 'RESEARCH', 'DEVELOPMENT', 'R & D']):
            # Don't add 'rd' if asking for intensity/ratio
            if not any(pattern in question_upper for pattern in ['TO REVENUE', 'TO SALES', 'INTENSITY']):
                requested.add('rd')
        
        if any(word in question_upper for word in ['SG&A', 'SGA', 'SG_AND_A', 'SELLING', 'ADMINISTRATIVE', 'S&GA', 'SGNA', 'SG & A']):
            # Don't add 'sga' if asking for intensity/ratio
            if not any(pattern in question_upper for pattern in ['TO REVENUE', 'TO SALES', 'INTENSITY']):
                requested.add('sga')
        
        if any(word in question_upper for word in ['COGS', 'COST OF GOODS', 'COST OF REVENUE', 'COST OF SALES']):
            requested.add('cogs')
        
        # Intensity keywords
        if 'R&D INTENSITY' in question_upper:
            requested.add('rnd_to_revenue')
        
        if 'SG&A INTENSITY' in question_upper or 'SGNA INTENSITY' in question_upper or 'SGA INTENSITY' in question_upper:
            requested.add('sgna_to_revenue')
        
        # Detect ratio patterns like "R&D to revenue ratio"
        if 'R&D TO REVENUE' in question_upper or 'R AND D TO REVENUE' in question_upper:
            requested.add('rnd_to_revenue')
        
        if 'SG&A TO REVENUE' in question_upper or 'SGA TO REVENUE' in question_upper or 'SGNA TO REVENUE' in question_upper:
            requested.add('sgna_to_revenue')
        
        # Generic "intensity" for when both might be shown
        if 'INTENSITY' in question_upper and 'R&D' not in question_upper and 'SG&A' not in question_upper and 'SGA' not in question_upper:
            requested.add('intensity')
        
        # Margin keywords
        if any(word in question_upper for word in ['GROSS MARGIN', 'GROSS PROFIT MARGIN']):
            requested.add('gross_margin')
        
        if any(word in question_upper for word in ['OPERATING MARGIN', 'EBIT MARGIN']):
            requested.add('operating_margin')
        
        if any(word in question_upper for word in ['NET MARGIN', 'PROFIT MARGIN', 'NET PROFIT MARGIN']):
            requested.add('net_margin')
        
        # Balance sheet items (but NOT if asking for ratios)
        # Only add 'assets' if NOT asking for debt-to-assets ratio
        if any(word in question_upper for word in ['TOTAL ASSETS', 'TOTAL_ASSETS']) and 'DEBT TO ASSETS' not in question_upper and 'DEBT-TO-ASSETS' not in question_upper:
            requested.add('assets')
        elif 'ASSETS' in question_upper and 'DEBT' not in question_upper:
            requested.add('assets')
        
        if any(word in question_upper for word in ['TOTAL LIABILITIES', 'TOTAL_LIABILITIES', 'LIABILITIES']):
            requested.add('liabilities')
        
        # Only add 'equity' if NOT asking for debt-to-equity ratio
        if 'EQUITY' in question_upper and 'DEBT TO EQUITY' not in question_upper and 'DEBT-TO-EQUITY' not in question_upper:
            requested.add('equity')
        
        if any(word in question_upper for word in ['DEBT', 'TOTAL DEBT']) and 'DEBT TO' not in question_upper and 'DEBT-TO-' not in question_upper:
            requested.add('debt')
        
        # Cash flow items (check these before generic keywords)
        if any(word in question_upper for word in ['OPERATING CASH FLOW', 'OCF', 'CASH FROM OPERATIONS', 'CASH FLOW OPS', 'CASH_FLOW_OPS', 'CASH FLOW FROM OPERATIONS']):
            requested.add('operating_cash_flow')
        
        if any(word in question_upper for word in ['INVESTING CASH FLOW', 'CASH FLOW INVESTING', 'CASH_FLOW_INVESTING', 'CASH FROM INVESTING', 'CASH FLOW FROM INVESTING']):
            requested.add('investing_cash_flow')
        
        if any(word in question_upper for word in ['FINANCING CASH FLOW', 'CASH FLOW FINANCING', 'CASH_FLOW_FINANCING', 'CASH FROM FINANCING', 'CASH FLOW FROM FINANCING']):
            requested.add('financing_cash_flow')
        
        if any(word in question_upper for word in ['FREE CASH FLOW', 'FCF']):
            requested.add('fcf')
        
        if any(word in question_upper for word in ['CAPEX', 'CAPITAL EXPENDITURE', 'CAPITAL SPENDING']):
            requested.add('capex')
        
        # Shareholder actions
        if any(word in question_upper for word in ['DIVIDEND', 'DIVIDENDS', 'DIVIDEND PAYMENT']):
            requested.add('dividends')
        
        if any(word in question_upper for word in ['BUYBACK', 'BUYBACKS', 'SHARE REPURCHASE', 'STOCK REPURCHASE']):
            requested.add('buybacks')
        
        # Ratios
        if any(word in question_upper for word in ['ROE', 'RETURN ON EQUITY']):
            requested.add('roe')
        
        if any(word in question_upper for word in ['ROA', 'RETURN ON ASSETS']):
            requested.add('roa')
        
        if any(word in question_upper for word in ['DEBT TO EQUITY', 'DEBT-TO-EQUITY', 'D/E RATIO']):
            requested.add('debt_to_equity')
        
        if any(word in question_upper for word in ['DEBT TO ASSETS', 'DEBT-TO-ASSETS']):
            requested.add('debt_to_assets')
        
        if any(word in question_upper for word in ['CURRENT RATIO']):
            requested.add('current_ratio')
        
        if any(word in question_upper for word in ['QUICK RATIO', 'ACID TEST']):
            requested.add('quick_ratio')
        
        # Growth metrics
        if any(word in question_upper for word in ['YOY', 'YEAR OVER YEAR', 'YEAR-OVER-YEAR', 'Y-O-Y']):
            requested.add('yoy')
        
        if any(word in question_upper for word in ['QOQ', 'QUARTER OVER QUARTER', 'QUARTER-OVER-QUARTER', 'Q-O-Q']):
            requested.add('qoq')
        
        if any(word in question_upper for word in ['CAGR', 'COMPOUND ANNUAL GROWTH']):
            requested.add('cagr')
        
        # Market metrics
        if any(word in question_upper for word in ['EPS', 'EARNINGS PER SHARE']):
            requested.add('eps')
        
        if any(word in question_upper for word in ['P/E', 'PE RATIO', 'PRICE TO EARNINGS', 'PRICE-TO-EARNINGS']):
            requested.add('pe_ratio')
        
        if any(word in question_upper for word in ['MARKET CAP', 'MARKET CAPITALIZATION']):
            requested.add('market_cap')
        
        # Stock price - check for specific types first
        # Check for opening price (both phrase and standalone word)
        if any(word in question_upper for word in ['OPENING PRICE', 'OPEN PRICE', 'OPENING STOCK', 'OPEN STOCK']) or \
           ('OPENING' in question_upper and 'PRICE' in question_upper):
            requested.add('opening_price')
        
        # Check for closing price (both phrase and standalone word)
        if any(word in question_upper for word in ['CLOSING PRICE', 'CLOSE PRICE', 'CLOSING STOCK', 'CLOSE STOCK', 'EOD PRICE', 'END OF DAY PRICE']) or \
           (('CLOSING' in question_upper or 'CLOSE' in question_upper) and 'PRICE' in question_upper):
            requested.add('closing_price')
        
        # Check for high price (both phrase and standalone word)
        if any(word in question_upper for word in ['HIGH PRICE', 'HIGHEST PRICE', 'YEAR HIGH', 'PEAK PRICE']) or \
           ('HIGH' in question_upper and 'PRICE' in question_upper):
            requested.add('high_price')
        
        # Check for low price (both phrase and standalone word)
        if any(word in question_upper for word in ['LOW PRICE', 'LOWEST PRICE', 'YEAR LOW', 'BOTTOM PRICE']) or \
           ('LOW' in question_upper and 'PRICE' in question_upper):
            requested.add('low_price')
        
        # Check for average price
        if any(word in question_upper for word in ['AVERAGE PRICE', 'AVG PRICE', 'MEAN PRICE']) or \
           (('AVERAGE' in question_upper or 'AVG' in question_upper) and 'PRICE' in question_upper):
            requested.add('average_price')
        
        # Generic price - only if no specific price type was mentioned
        if 'price' not in requested and 'opening_price' not in requested and 'closing_price' not in requested and 'high_price' not in requested and 'low_price' not in requested and 'average_price' not in requested:
            if any(word in question_upper for word in ['SHARE PRICE', 'STOCK PRICE', 'STOCK', 'PRICE', 'TRADING PRICE']):
                requested.add('price')
        
        if any(word in question_upper for word in ['RETURN', 'STOCK RETURN', 'PRICE RETURN']):
            requested.add('return')
        
        if any(word in question_upper for word in ['VOLATILITY', 'VOL', 'PRICE VOLATILITY']):
            requested.add('volatility')
        
        if any(word in question_upper for word in ['DIVIDEND', 'DIVIDEND YIELD', 'DIV YIELD']):
            requested.add('dividend')
        
        # If no specific metrics found, check if it's a generic query
        if not requested:
            # Generic queries should show all available data
            generic_keywords = ['METRICS', 'DATA', 'INFORMATION', 'DETAILS', 'FINANCIAL', 'PERFORMANCE', 'NUMBERS', 'STATS', 'STATISTICS']
            if any(word in question_upper for word in generic_keywords):
                requested.add('all')
            # If just asking to "show" a company with a year/quarter, show relevant metrics
            elif 'SHOW' in question_upper and not any(word in question_upper for word in ['GROWTH', 'COMPARE', 'VS', 'VERSUS']):
                requested.add('all')
        
        return requested
    
    def _generate_simple_summary(self, df: pd.DataFrame, context: Dict) -> str:
        """Generate simple factual summary from results"""
        if len(df) == 0:
            return "No data found."
        
        # Check if this is a multi-company query (multiple distinct tickers)
        if 'ticker' in df.columns and len(df['ticker'].unique()) > 1:
            return self._generate_multi_company_summary(df, context)
        
        # Get first row
        row = df.iloc[0]
        
        # DEBUG: Log what we're working with
        print(f"[DEBUG FORMATTER] Columns in row: {list(row.index)}")
        print(f"[DEBUG FORMATTER] Question: {context.get('question', 'NO QUESTION')}")
        print(f"[DEBUG FORMATTER] Intent: {context.get('intent', 'NO INTENT')}")
        
        # Check if this is a combined/complete query (many columns from different sources)
        intent = context.get('intent', '')
        is_complete_query = intent.startswith('complete_')
        
        # Check if this is a macro sensitivity query (has ticker + beta columns)
        is_sensitivity = 'ticker' in row and any(
            col in row for col in [
                'beta_gm_cpi_12q', 'beta_nm_cpi_12q', 'beta_gm_cpi_annual', 'beta_nm_cpi_annual'
            ]
        )
        
        if is_sensitivity and not is_complete_query:
            return self._generate_sensitivity_summary(df, context)
        
        # Check if this is a macro indicator query (no company info)
        is_macro = 'ticker' not in row and any(
            col in row for col in [
                'gdp', 'gdp_annual', 'cpi', 'cpi_annual', 
                'unemployment_rate', 'unemployment_rate_annual',
                'fed_funds_rate', 'fed_funds_rate_annual',
                'sp500_index', 'sp500_index_annual'
            ]
        )
        
        if is_macro:
            return self._generate_macro_summary(df, context)
        
        # Extract company info
        ticker = row.get('ticker', 'Unknown')
        name = row.get('name', ticker)
        year = row.get('fiscal_year')
        quarter = row.get('fiscal_quarter')
        
        # Build period string
        if quarter:
            period_str = f"Q{quarter} FY{year}"
        elif year:
            period_str = f"FY{year}"
        else:
            period_str = "the period"
        
        # Determine which metrics were requested
        question = context.get('question', '')
        requested_metrics = self._extract_requested_metrics(question) if question else {'all'}
        show_all = 'all' in requested_metrics or len(requested_metrics) == 0
        
        # DEBUG: Log metric detection
        print(f"[DEBUG FORMATTER] Requested metrics: {requested_metrics}")
        print(f"[DEBUG FORMATTER] Show all: {show_all}")
        
        # Build response based on available metrics AND what was requested
        parts = []
        
        # Revenue
        if (show_all or 'revenue' in requested_metrics) and 'revenue_b' in row and row['revenue_b'] is not None:
            parts.append(f"revenue of ${row['revenue_b']:.2f}B")
        
        # Net income  
        if (show_all or 'net_income' in requested_metrics) and 'net_income_b' in row and row['net_income_b'] is not None:
            parts.append(f"net income of ${row['net_income_b']:.2f}B")
        
        # Operating income
        if (show_all or 'operating_income' in requested_metrics) and 'op_income_b' in row and row['op_income_b'] is not None:
            parts.append(f"operating income of ${row['op_income_b']:.2f}B")
        
        # Gross profit
        if (show_all or 'gross_profit' in requested_metrics):
            if 'gross_profit_b' in row and row['gross_profit_b'] is not None:
                parts.append(f"gross profit of ${row['gross_profit_b']:.2f}B")
            elif 'gross_profit_annual_b' in row and row['gross_profit_annual_b'] is not None:
                parts.append(f"gross profit of ${row['gross_profit_annual_b']:.2f}B")
            elif 'gross_profit_annual' in row and row['gross_profit_annual'] is not None:
                parts.append(f"gross profit of ${row['gross_profit_annual']/1e9:.2f}B")
        
        # R&D Expenses (quarterly) - but NOT if asking for intensity
        if ((show_all and 'intensity' not in requested_metrics) or ('rd' in requested_metrics and 'intensity' not in requested_metrics)) and 'rd_b' in row and row['rd_b'] is not None:
            parts.append(f"R&D expenses of ${row['rd_b']:.2f}B")
        
        # R&D Expenses (annual) - but NOT if asking for intensity
        if ((show_all and 'intensity' not in requested_metrics) or ('rd' in requested_metrics and 'intensity' not in requested_metrics)) and 'rd_annual_b' in row and row['rd_annual_b'] is not None:
            parts.append(f"R&D expenses of ${row['rd_annual_b']:.2f}B")
        
        # SG&A Expenses (quarterly) - but NOT if asking for intensity
        if ((show_all and 'intensity' not in requested_metrics) or ('sga' in requested_metrics and 'intensity' not in requested_metrics)) and 'sga_b' in row and row['sga_b'] is not None:
            parts.append(f"SG&A expenses of ${row['sga_b']:.2f}B")
        
        # SG&A Expenses (annual) - but NOT if asking for intensity
        if ((show_all and 'intensity' not in requested_metrics) or ('sga' in requested_metrics and 'intensity' not in requested_metrics)) and 'sga_annual_b' in row and row['sga_annual_b'] is not None:
            parts.append(f"SG&A expenses of ${row['sga_annual_b']:.2f}B")
        
        # COGS (quarterly)
        if (show_all or 'cogs' in requested_metrics) and 'cogs_b' in row and row['cogs_b'] is not None:
            parts.append(f"COGS of ${row['cogs_b']:.2f}B")
        
        # COGS (annual)
        if (show_all or 'cogs' in requested_metrics) and 'cogs_annual_b' in row and row['cogs_annual_b'] is not None:
            parts.append(f"COGS of ${row['cogs_annual_b']:.2f}B")
        
        # Margins (check both quarterly and annual column names)
        if (show_all or 'gross_margin' in requested_metrics):
            if 'gross_margin' in row and row['gross_margin'] is not None:
                parts.append(f"gross margin of {row['gross_margin']*100:.1f}%")
            elif 'gross_margin_annual' in row and row['gross_margin_annual'] is not None:
                parts.append(f"gross margin of {row['gross_margin_annual']*100:.1f}%")
            elif 'gross_margin_ttm' in row and row['gross_margin_ttm'] is not None:
                parts.append(f"gross margin of {row['gross_margin_ttm']*100:.1f}%")
        
        if (show_all or 'operating_margin' in requested_metrics):
            if 'operating_margin' in row and row['operating_margin'] is not None:
                parts.append(f"operating margin of {row['operating_margin']*100:.1f}%")
            elif 'operating_margin_annual' in row and row['operating_margin_annual'] is not None:
                parts.append(f"operating margin of {row['operating_margin_annual']*100:.1f}%")
            elif 'operating_margin_ttm' in row and row['operating_margin_ttm'] is not None:
                parts.append(f"operating margin of {row['operating_margin_ttm']*100:.1f}%")
        
        if (show_all or 'net_margin' in requested_metrics):
            if 'net_margin' in row and row['net_margin'] is not None:
                parts.append(f"net margin of {row['net_margin']*100:.1f}%")
            elif 'net_margin_annual' in row and row['net_margin_annual'] is not None:
                parts.append(f"net margin of {row['net_margin_annual']*100:.1f}%")
            elif 'net_margin_ttm' in row and row['net_margin_ttm'] is not None:
                parts.append(f"net margin of {row['net_margin_ttm']*100:.1f}%")
        
        # ROE
        if (show_all or 'roe' in requested_metrics):
            if 'roe' in row and row['roe'] is not None:
                parts.append(f"ROE of {row['roe']*100:.1f}%")
            elif 'roe_annual_avg_equity' in row and row['roe_annual_avg_equity'] is not None:
                parts.append(f"ROE of {row['roe_annual_avg_equity']*100:.1f}%")
            elif 'roe_ttm' in row and row['roe_ttm'] is not None:
                parts.append(f"ROE of {row['roe_ttm']*100:.1f}%")
        
        # ROA
        if (show_all or 'roa' in requested_metrics):
            if 'roa' in row and row['roa'] is not None:
                parts.append(f"ROA of {row['roa']*100:.1f}%")
            elif 'roa_annual' in row and row['roa_annual'] is not None:
                parts.append(f"ROA of {row['roa_annual']*100:.1f}%")
            elif 'roa_ttm' in row and row['roa_ttm'] is not None:
                parts.append(f"ROA of {row['roa_ttm']*100:.1f}%")
        
        # Debt ratios
        if (show_all or 'debt_to_equity' in requested_metrics or 'debt to equity' in requested_metrics):
            if 'debt_to_equity' in row and row['debt_to_equity'] is not None:
                parts.append(f"debt-to-equity ratio of {float(row['debt_to_equity']):.2f}")
            elif 'debt_to_equity_annual' in row and row['debt_to_equity_annual'] is not None:
                parts.append(f"debt-to-equity ratio of {float(row['debt_to_equity_annual']):.2f}")
        
        if (show_all or 'debt_to_assets' in requested_metrics or 'debt to assets' in requested_metrics):
            if 'debt_to_assets' in row and row['debt_to_assets'] is not None:
                parts.append(f"debt-to-assets ratio of {float(row['debt_to_assets']):.2f}")
            elif 'debt_to_assets_annual' in row and row['debt_to_assets_annual'] is not None:
                parts.append(f"debt-to-assets ratio of {float(row['debt_to_assets_annual']):.2f}")
        
        # Intensity ratios
        if (show_all or 'rnd_to_revenue' in requested_metrics or 'intensity' in requested_metrics):
            if 'rnd_to_revenue' in row and row['rnd_to_revenue'] is not None:
                parts.append(f"R&D intensity of {float(row['rnd_to_revenue'])*100:.1f}%")
            elif 'rnd_to_revenue_annual' in row and row['rnd_to_revenue_annual'] is not None:
                parts.append(f"R&D intensity of {float(row['rnd_to_revenue_annual'])*100:.1f}%")
        
        if (show_all or 'sgna_to_revenue' in requested_metrics or 'intensity' in requested_metrics):
            if 'sgna_to_revenue' in row and row['sgna_to_revenue'] is not None:
                parts.append(f"SG&A intensity of {float(row['sgna_to_revenue'])*100:.1f}%")
            elif 'sgna_to_revenue_annual' in row and row['sgna_to_revenue_annual'] is not None:
                parts.append(f"SG&A intensity of {float(row['sgna_to_revenue_annual'])*100:.1f}%")
        
        # Balance sheet items
        if (show_all or 'assets' in requested_metrics):
            if 'total_assets' in row and row['total_assets'] is not None:
                val = float(row['total_assets']) / 1e9
                parts.append(f"total assets of ${val:.2f}B")
            elif 'total_assets_eoy' in row and row['total_assets_eoy'] is not None:
                val = float(row['total_assets_eoy']) / 1e9
                parts.append(f"total assets of ${val:.2f}B")
        
        if (show_all or 'liabilities' in requested_metrics):
            if 'total_liabilities' in row and row['total_liabilities'] is not None:
                val = float(row['total_liabilities']) / 1e9
                parts.append(f"total liabilities of ${val:.2f}B")
            elif 'total_liabilities_eoy' in row and row['total_liabilities_eoy'] is not None:
                val = float(row['total_liabilities_eoy']) / 1e9
                parts.append(f"total liabilities of ${val:.2f}B")
        
        if (show_all or 'equity' in requested_metrics):
            if 'equity' in row and row['equity'] is not None:
                val = float(row['equity']) / 1e9  # Convert to billions
                parts.append(f"equity of ${val:.2f}B")
            elif 'equity_eoy' in row and row['equity_eoy'] is not None:
                val = float(row['equity_eoy']) / 1e9  # Convert to billions
                parts.append(f"equity of ${val:.2f}B")
        
        # Cash flow items (values are already in billions if from query, or need conversion if raw)
        if (show_all or 'operating_cash_flow' in requested_metrics):
            if 'operating_cash_flow' in row and row['operating_cash_flow'] is not None:
                val = float(row['operating_cash_flow'])
                parts.append(f"operating cash flow of ${val:.2f}B")
            elif 'cash_from_operations' in row and row['cash_from_operations'] is not None:
                val = float(row['cash_from_operations'])
                parts.append(f"operating cash flow of ${val:.2f}B")
            elif 'ocf' in row and row['ocf'] is not None:
                val = float(row['ocf'])
                parts.append(f"operating cash flow of ${val:.2f}B")
        
        if (show_all or 'investing_cash_flow' in requested_metrics):
            if 'investing_cash_flow' in row and row['investing_cash_flow'] is not None:
                val = float(row['investing_cash_flow'])
                parts.append(f"investing cash flow of ${val:.2f}B")
            elif 'cash_from_investing' in row and row['cash_from_investing'] is not None:
                val = float(row['cash_from_investing'])
                parts.append(f"investing cash flow of ${val:.2f}B")
        
        if (show_all or 'financing_cash_flow' in requested_metrics):
            if 'financing_cash_flow' in row and row['financing_cash_flow'] is not None:
                val = float(row['financing_cash_flow'])
                parts.append(f"financing cash flow of ${val:.2f}B")
            elif 'cash_from_financing' in row and row['cash_from_financing'] is not None:
                val = float(row['cash_from_financing'])
                parts.append(f"financing cash flow of ${val:.2f}B")
        
        if (show_all or 'fcf' in requested_metrics):
            if 'free_cash_flow' in row and row['free_cash_flow'] is not None:
                val = float(row['free_cash_flow'])
                parts.append(f"free cash flow of ${val:.2f}B")
            elif 'fcf' in row and row['fcf'] is not None:
                val = float(row['fcf'])
                parts.append(f"free cash flow of ${val:.2f}B")
        
        if (show_all or 'capex' in requested_metrics):
            if 'capex' in row and row['capex'] is not None:
                val = float(row['capex'])
                parts.append(f"capex of ${val:.2f}B")
            elif 'capex_annual_b' in row and row['capex_annual_b'] is not None:
                val = float(row['capex_annual_b'])
                parts.append(f"capex of ${val:.2f}B")
        
        # Shareholder actions
        if (show_all or 'dividends' in requested_metrics):
            if 'dividends' in row and row['dividends'] is not None:
                val = float(row['dividends'])
                parts.append(f"dividends of ${val:.2f}B")
            elif 'dividend_payments' in row and row['dividend_payments'] is not None:
                val = float(row['dividend_payments'])
                parts.append(f"dividends of ${val:.2f}B")
        
        if (show_all or 'buybacks' in requested_metrics):
            if 'buybacks' in row and row['buybacks'] is not None:
                val = float(row['buybacks'])
                parts.append(f"buybacks of ${val:.2f}B")
            elif 'share_repurchases' in row and row['share_repurchases'] is not None:
                val = float(row['share_repurchases'])
                parts.append(f"buybacks of ${val:.2f}B")
        
        # Per-share metrics
        if (show_all or 'eps' in requested_metrics):
            if 'eps' in row and row['eps'] is not None:
                parts.append(f"EPS of ${row['eps']:.2f}")
            elif 'earnings_per_share' in row and row['earnings_per_share'] is not None:
                parts.append(f"EPS of ${row['earnings_per_share']:.2f}")
        
        # Stock price metrics - check for specific types requested
        # Check if user asked for "average" explicitly
        question_upper = question.upper() if question else ''
        wants_average = 'AVERAGE' in question_upper or 'AVG' in question_upper
        
        # Opening price
        if ('opening_price' in requested_metrics):
            print(f"[DEBUG FORMATTER] Checking opening_price...")
            if wants_average:
                # User explicitly asked for average
                if 'avg_open_price_annual' in row and row['avg_open_price_annual'] is not None:
                    parts.append(f"average opening price of ${float(row['avg_open_price_annual']):.2f}")
                elif 'avg_open_price' in row and row['avg_open_price'] is not None:
                    parts.append(f"average opening price of ${float(row['avg_open_price']):.2f}")
            else:
                # User asked for just "opening price" - check quarterly then annual
                # Quarterly: open_price (start of quarter)
                if 'open_price' in row and row['open_price'] is not None:
                    parts.append(f"opening price of ${float(row['open_price']):.2f}")
                    print(f"[DEBUG FORMATTER] Added quarterly opening price: ${float(row['open_price']):.2f}")
                # Annual: Use average (no "first day of year" opening price exists)
                elif 'avg_open_price_annual' in row and row['avg_open_price_annual'] is not None:
                    parts.append(f"opening price of ${float(row['avg_open_price_annual']):.2f}")
                    print(f"[DEBUG FORMATTER] Added annual opening price: ${float(row['avg_open_price_annual']):.2f}")
                # Fallback to averages
                elif 'avg_open_price' in row and row['avg_open_price'] is not None:
                    parts.append(f"opening price of ${float(row['avg_open_price']):.2f}")
        
        # Closing price
        if ('closing_price' in requested_metrics):
            if wants_average:
                # User explicitly asked for average - use avg_close_price_annual or avg_close_price
                if 'avg_close_price_annual' in row and row['avg_close_price_annual'] is not None:
                    parts.append(f"average closing price of ${float(row['avg_close_price_annual']):.2f}")
                elif 'avg_close_price' in row and row['avg_close_price'] is not None:
                    parts.append(f"average closing price of ${float(row['avg_close_price']):.2f}")
            else:
                # User asked for just "closing price" - check quarterly then annual
                # Quarterly: close_price (end of quarter)
                if 'close_price' in row and row['close_price'] is not None:
                    parts.append(f"closing price of ${float(row['close_price']):.2f}")
                # Annual: close_price_eoy (end of year)
                elif 'close_price_eoy' in row and row['close_price_eoy'] is not None:
                    parts.append(f"closing price of ${float(row['close_price_eoy']):.2f}")
                # Fallback to averages
                elif 'avg_close_price_annual' in row and row['avg_close_price_annual'] is not None:
                    parts.append(f"closing price of ${float(row['avg_close_price_annual']):.2f}")
                elif 'avg_close_price' in row and row['avg_close_price'] is not None:
                    parts.append(f"closing price of ${float(row['avg_close_price']):.2f}")
        
        # High price
        if ('high_price' in requested_metrics):
            if 'high_price' in row and row['high_price'] is not None:
                parts.append(f"high price of ${float(row['high_price']):.2f}")
            elif 'high_price_annual' in row and row['high_price_annual'] is not None:
                parts.append(f"high price of ${float(row['high_price_annual']):.2f}")
        
        # Low price
        if ('low_price' in requested_metrics):
            if 'low_price' in row and row['low_price'] is not None:
                parts.append(f"low price of ${float(row['low_price']):.2f}")
            elif 'low_price_annual' in row and row['low_price_annual'] is not None:
                parts.append(f"low price of ${float(row['low_price_annual']):.2f}")
        
        # Average price
        if ('average_price' in requested_metrics):
            if 'avg_price' in row and row['avg_price'] is not None:
                parts.append(f"average price of ${float(row['avg_price']):.2f}")
            elif 'avg_price_annual' in row and row['avg_price_annual'] is not None:
                parts.append(f"average price of ${float(row['avg_price_annual']):.2f}")
        
        # Generic price - show average or closing if no specific type requested
        if (show_all or 'price' in requested_metrics):
            # Only show if no specific price type was requested
            if 'opening_price' not in requested_metrics and 'closing_price' not in requested_metrics and 'high_price' not in requested_metrics and 'low_price' not in requested_metrics and 'average_price' not in requested_metrics:
                # Quarterly average price
                if 'avg_price' in row and row['avg_price'] is not None:
                    parts.append(f"average stock price of ${float(row['avg_price']):.2f}")
                # Annual average price
                elif 'avg_price_annual' in row and row['avg_price_annual'] is not None:
                    parts.append(f"average stock price of ${float(row['avg_price_annual']):.2f}")
                # Closing price (quarterly)
                elif 'close_price' in row and row['close_price'] is not None:
                    parts.append(f"closing price of ${float(row['close_price']):.2f}")
                # Closing price EOY (annual)
                elif 'close_price_eoy' in row and row['close_price_eoy'] is not None:
                    parts.append(f"year-end closing price of ${float(row['close_price_eoy']):.2f}")
                
                # Stock price range (only if generic price)
                # Quarterly high/low
                if 'high_price' in row and 'low_price' in row and row['high_price'] is not None and row['low_price'] is not None:
                    parts.append(f"trading range of ${float(row['low_price']):.2f}-${float(row['high_price']):.2f}")
                # Annual high/low
                elif 'high_price_annual' in row and 'low_price_annual' in row and row['high_price_annual'] is not None and row['low_price_annual'] is not None:
                    parts.append(f"year-high/low of ${float(row['low_price_annual']):.2f}-${float(row['high_price_annual']):.2f}")
        
        # Stock returns - only show if explicitly requested or if show_all AND it's a stock query
        if ('return' in requested_metrics) or (show_all and 'avg_price_annual' in row):
            # Quarterly return (QoQ)
            if 'return_qoq' in row and row['return_qoq'] is not None:
                val = float(row['return_qoq']) * 100
                parts.append(f"quarterly return of {val:+.1f}%")
            # Annual return
            if 'return_annual' in row and row['return_annual'] is not None:
                val = float(row['return_annual']) * 100
                parts.append(f"annual return of {val:+.1f}%")
            # Year-over-year return
            elif 'return_yoy' in row and row['return_yoy'] is not None:
                val = float(row['return_yoy']) * 100
                parts.append(f"year-over-year return of {val:+.1f}%")
        
        # Stock volatility - only show if explicitly requested or if show_all AND it's a stock query
        if ('volatility' in requested_metrics) or (show_all and 'avg_price_annual' in row):
            if 'volatility_pct' in row and row['volatility_pct'] is not None:
                val = float(row['volatility_pct']) * 100
                parts.append(f"volatility of {val:.1f}%")
            elif 'volatility_pct_annual' in row and row['volatility_pct_annual'] is not None:
                val = float(row['volatility_pct_annual']) * 100
                parts.append(f"annual volatility of {val:.1f}%")
        
        # Dividend info (from stock data) - only show if explicitly requested
        if ('dividend' in requested_metrics):
            if 'dividend_yield' in row and row['dividend_yield'] is not None:
                val = float(row['dividend_yield']) * 100
                parts.append(f"dividend yield of {val:.2f}%")
            elif 'dividend_yield_annual' in row and row['dividend_yield_annual'] is not None:
                val = float(row['dividend_yield_annual']) * 100
                parts.append(f"dividend yield of {val:.2f}%")
        
        # Additional ratios (debt ratios already handled above, so skip them here)
        
        # Growth rates (show only if requested or in growth query)
        if (show_all or 'yoy' in requested_metrics or 'revenue' in requested_metrics):
            if 'revenue_yoy' in row and row['revenue_yoy'] is not None:
                parts.append(f"revenue YoY growth of {row['revenue_yoy']*100:.1f}%")
        
        if (show_all or 'qoq' in requested_metrics or 'revenue' in requested_metrics):
            if 'revenue_qoq' in row and row['revenue_qoq'] is not None:
                parts.append(f"revenue QoQ growth of {row['revenue_qoq']*100:.1f}%")
        
        if (show_all or 'cagr' in requested_metrics):
            if 'revenue_cagr_3y' in row and row['revenue_cagr_3y'] is not None:
                parts.append(f"3-year revenue CAGR of {row['revenue_cagr_3y']*100:.1f}%")
            if 'revenue_cagr_5y' in row and row['revenue_cagr_5y'] is not None:
                parts.append(f"5-year revenue CAGR of {row['revenue_cagr_5y']*100:.1f}%")
        
        # Build final response
        print(f"[DEBUG FORMATTER] Final parts list: {parts}")
        print(f"[DEBUG FORMATTER] Parts count: {len(parts)}")
        
        if len(parts) > 0:
            metrics_str = ", ".join(parts)
            
            if len(df) == 1:
                # Single result - simple sentence
                return f"{name} ({ticker}) reported {metrics_str} for {period_str}."
            else:
                # Multiple results - add count
                return f"Found {len(df)} periods of data for {name} ({ticker}). For {period_str}: {metrics_str}."
        else:
            print(f"[DEBUG FORMATTER] WARNING: Empty parts list! Returning generic message.")
            return f"Data found for {name} ({ticker}) in {period_str}."
    
    def _generate_multi_company_summary(self, df: pd.DataFrame, context: Dict) -> str:
        """Generate direct summary for multi-company queries"""
        # Get the question to understand what was requested
        question = context.get('question', '')
        requested_metrics = self._extract_requested_metrics(question) if question else {'all'}
        show_all = 'all' in requested_metrics or len(requested_metrics) == 0
        
        # Check if user wants "average" explicitly
        question_upper = question.upper() if question else ''
        wants_average = 'AVERAGE' in question_upper or 'AVG' in question_upper
        
        # Extract period info from first row
        first_row = df.iloc[0]
        year = first_row.get('fiscal_year')
        quarter = first_row.get('fiscal_quarter')
        
        # Build period string
        if quarter:
            period_str = f"Q{quarter} {year}"
        elif year:
            period_str = f"{year}"
        else:
            period_str = "the requested period"
        
        # Build intro line based on what metrics were requested
        metric_names = []
        if 'revenue' in requested_metrics or show_all:
            metric_names.append("revenue")
        if 'net_income' in requested_metrics:
            metric_names.append("net income")
        if 'gross_margin' in requested_metrics:
            metric_names.append("gross margin")
        if 'operating_margin' in requested_metrics:
            metric_names.append("operating margin")
        if 'net_margin' in requested_metrics:
            metric_names.append("net margin")
        if 'roe' in requested_metrics:
            metric_names.append("ROE")
        if 'opening_price' in requested_metrics:
            metric_names.append("opening price")
        if 'closing_price' in requested_metrics:
            metric_names.append("closing price")
        if 'high_price' in requested_metrics:
            metric_names.append("high price")
        if 'low_price' in requested_metrics:
            metric_names.append("low price")
        if 'average_price' in requested_metrics:
            metric_names.append("average price")
        
        # Create intro
        if len(metric_names) > 0:
            metrics_phrase = ", ".join(metric_names) if len(metric_names) <= 2 else f"{', '.join(metric_names[:-1])}, and {metric_names[-1]}"
            intro = f"Here is the {metrics_phrase} for {period_str}:"
        else:
            intro = f"Here is the data for {period_str}:"
        
        # Build company summaries
        company_lines = []
        for _, row in df.iterrows():
            ticker = row.get('ticker', 'Unknown')
            name = row.get('name', ticker)
            
            # Build metrics for this company
            parts = []
            
            # Revenue
            if (show_all or 'revenue' in requested_metrics) and 'revenue_b' in row and row['revenue_b'] is not None:
                parts.append(f"${row['revenue_b']:.2f}B revenue")
            
            # Net income  
            if ('net_income' in requested_metrics) and 'net_income_b' in row and row['net_income_b'] is not None:
                parts.append(f"${row['net_income_b']:.2f}B net income")
            
            # Margins
            if ('gross_margin' in requested_metrics):
                if 'gross_margin' in row and row['gross_margin'] is not None:
                    parts.append(f"{row['gross_margin']*100:.1f}% gross margin")
                elif 'gross_margin_annual' in row and row['gross_margin_annual'] is not None:
                    parts.append(f"{row['gross_margin_annual']*100:.1f}% gross margin")
            
            if ('operating_margin' in requested_metrics):
                if 'operating_margin' in row and row['operating_margin'] is not None:
                    parts.append(f"{row['operating_margin']*100:.1f}% operating margin")
                elif 'operating_margin_annual' in row and row['operating_margin_annual'] is not None:
                    parts.append(f"{row['operating_margin_annual']*100:.1f}% operating margin")
            
            if ('net_margin' in requested_metrics):
                if 'net_margin' in row and row['net_margin'] is not None:
                    parts.append(f"{row['net_margin']*100:.1f}% net margin")
                elif 'net_margin_annual' in row and row['net_margin_annual'] is not None:
                    parts.append(f"{row['net_margin_annual']*100:.1f}% net margin")
            
            # ROE
            if ('roe' in requested_metrics):
                if 'roe' in row and row['roe'] is not None:
                    parts.append(f"{row['roe']*100:.1f}% ROE")
                elif 'roe_annual_avg_equity' in row and row['roe_annual_avg_equity'] is not None:
                    parts.append(f"{row['roe_annual_avg_equity']*100:.1f}% ROE")
            
            # Stock price metrics
            if ('opening_price' in requested_metrics):
                if 'avg_open_price_annual' in row and row['avg_open_price_annual'] is not None:
                    label = "average opening price" if wants_average else "opening price"
                    parts.append(f"${float(row['avg_open_price_annual']):.2f} {label}")
            
            if ('closing_price' in requested_metrics):
                if wants_average:
                    # User explicitly asked for average
                    if 'avg_close_price_annual' in row and row['avg_close_price_annual'] is not None:
                        parts.append(f"${float(row['avg_close_price_annual']):.2f} average closing price")
                else:
                    # User asked for just "closing price" - prefer actual EOY price
                    if 'close_price_eoy' in row and row['close_price_eoy'] is not None:
                        parts.append(f"${float(row['close_price_eoy']):.2f} closing price")
                    elif 'avg_close_price_annual' in row and row['avg_close_price_annual'] is not None:
                        # Fallback to average if EOY not available
                        parts.append(f"${float(row['avg_close_price_annual']):.2f} closing price")
            
            if ('high_price' in requested_metrics):
                if 'high_price_annual' in row and row['high_price_annual'] is not None:
                    parts.append(f"${float(row['high_price_annual']):.2f} high price")
            
            if ('low_price' in requested_metrics):
                if 'low_price_annual' in row and row['low_price_annual'] is not None:
                    parts.append(f"${float(row['low_price_annual']):.2f} low price")
            
            if ('average_price' in requested_metrics):
                if 'avg_price_annual' in row and row['avg_price_annual'] is not None:
                    parts.append(f"${float(row['avg_price_annual']):.2f} average price")
            
            # Format the line
            if len(parts) > 0:
                metrics_str = ", ".join(parts)
                company_lines.append(f"- **{name}**: {metrics_str}")
        
        # Combine intro and company lines
        if len(company_lines) > 0:
            return intro + "\n" + "\n".join(company_lines)
        else:
            return intro
    
    def _summarize_dataframe(self, df: pd.DataFrame) -> str:
        """Create a text summary of DataFrame for LLM"""
        summary_parts = []
        
        # Row count
        summary_parts.append(f"{len(df)} rows")
        
        # Column names
        summary_parts.append(f"Columns: {', '.join(df.columns[:10])}")
        
        # Sample values for key columns
        key_cols = []
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['revenue', 'margin', 'roe', 'growth', 'rank', 'yoy', 'qoq']):
                key_cols.append(col)
        
        if key_cols:
            summary_parts.append("Key metrics:")
            for col in key_cols[:5]:  # Limit to 5 key columns
                if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                    mean_val = df[col].mean()
                    min_val = df[col].min()
                    max_val = df[col].max()
                    summary_parts.append(f"  {col}: mean={mean_val:.2f}, range=[{min_val:.2f}, {max_val:.2f}]")
        
        return "\n".join(summary_parts)
    
    def _generate_macro_summary(self, df: pd.DataFrame, context: Dict) -> str:
        """Generate summary for macro indicator queries"""
        if len(df) == 0:
            return "No macro data found."
        
        row = df.iloc[0]
        year = row.get('fiscal_year')
        quarter = row.get('fiscal_quarter')
        
        # Build period string
        if quarter:
            period_str = f"Q{quarter} FY{year}"
        elif year:
            period_str = f"FY{year}"
        else:
            period_str = "the period"
        
        # Determine which indicators to show based on query
        question = context.get('question', '').upper()
        parts = []
        
        # GDP
        if 'GDP' in question or 'GROSS DOMESTIC' in question:
            if 'gdp_t' in row and row['gdp_t'] is not None:
                parts.append(f"GDP was ${float(row['gdp_t']):.2f} trillion")
            elif 'gdp' in row and row['gdp'] is not None:
                parts.append(f"GDP was ${float(row['gdp']):.2f}B")
            elif 'gdp_annual' in row and row['gdp_annual'] is not None:
                parts.append(f"GDP was ${float(row['gdp_annual']):.2f}B")
        
        # Inflation indicators
        if 'INFLATION' in question or 'CPI' in question or 'CONSUMER PRICE' in question:
            if 'cpi' in row and row['cpi'] is not None:
                parts.append(f"CPI was {float(row['cpi']):.2f}")
            elif 'cpi_annual' in row and row['cpi_annual'] is not None:
                parts.append(f"CPI was {float(row['cpi_annual']):.2f}")
            
            if 'core_cpi' in row and row['core_cpi'] is not None:
                parts.append(f"Core CPI was {float(row['core_cpi']):.2f}")
            elif 'core_cpi_annual' in row and row['core_cpi_annual'] is not None:
                parts.append(f"Core CPI was {float(row['core_cpi_annual']):.2f}")
        
        # Unemployment
        if 'UNEMPLOYMENT' in question or 'JOBLESS' in question:
            if 'unemployment_rate' in row and row['unemployment_rate'] is not None:
                parts.append(f"the unemployment rate was {float(row['unemployment_rate']):.2f}%")
            elif 'unemployment_rate_annual' in row and row['unemployment_rate_annual'] is not None:
                parts.append(f"the unemployment rate was {float(row['unemployment_rate_annual']):.2f}%")
        
        # Fed funds rate
        if 'FED' in question or 'INTEREST RATE' in question or 'FEDERAL FUNDS' in question:
            if 'fed_funds_rate' in row and row['fed_funds_rate'] is not None:
                parts.append(f"the Federal Funds Rate was {float(row['fed_funds_rate']):.2f}%")
            elif 'fed_funds_rate_annual' in row and row['fed_funds_rate_annual'] is not None:
                parts.append(f"the Federal Funds Rate was {float(row['fed_funds_rate_annual']):.2f}%")
        
        # S&P 500
        if 'S&P' in question or 'SPX' in question or 'MARKET INDEX' in question:
            if 'sp500_index' in row and row['sp500_index'] is not None:
                parts.append(f"S&P 500 Index of {float(row['sp500_index']):.2f}")
            elif 'sp500_index_annual' in row and row['sp500_index_annual'] is not None:
                parts.append(f"S&P 500 Index (annual average) of {float(row['sp500_index_annual']):.2f}")
        
        # VIX
        if 'VIX' in question or 'VOLATILITY INDEX' in question or 'FEAR' in question:
            if 'vix_index' in row and row['vix_index'] is not None:
                parts.append(f"VIX of {float(row['vix_index']):.2f}")
            elif 'vix_index_annual' in row and row['vix_index_annual'] is not None:
                parts.append(f"VIX (annual average) of {float(row['vix_index_annual']):.2f}")
        
        # Yield spread
        if 'YIELD' in question or 'SPREAD' in question or 'CURVE' in question:
            if 'term_spread_10y_2y' in row and row['term_spread_10y_2y'] is not None:
                parts.append(f"10Y-2Y yield spread of {float(row['term_spread_10y_2y']):.2f}%")
            elif 'term_spread_10y_2y_annual' in row and row['term_spread_10y_2y_annual'] is not None:
                parts.append(f"10Y-2Y yield spread (annual average) of {float(row['term_spread_10y_2y_annual']):.2f}%")
        
        # PCE
        if 'PCE' in question or 'PERSONAL CONSUMPTION' in question:
            if 'pce' in row and row['pce'] is not None:
                parts.append(f"PCE of ${float(row['pce']):.2f}B")
            elif 'pce_annual' in row and row['pce_annual'] is not None:
                parts.append(f"PCE (annual average) of ${float(row['pce_annual']):.2f}B")
            
            if 'pce_price_index' in row and row['pce_price_index'] is not None:
                parts.append(f"PCE Price Index of {float(row['pce_price_index']):.2f}")
            elif 'pce_price_index_annual' in row and row['pce_price_index_annual'] is not None:
                parts.append(f"PCE Price Index (annual average) of {float(row['pce_price_index_annual']):.2f}")
        
        # If no specific indicators matched, show all available
        if not parts:
            parts = []
            if 'gdp' in row and row['gdp'] is not None:
                parts.append(f"Real GDP of ${float(row['gdp']):.2f}B")
            elif 'gdp_annual' in row and row['gdp_annual'] is not None:
                parts.append(f"Real GDP of ${float(row['gdp_annual']):.2f}B")
            
            if 'cpi' in row and row['cpi'] is not None:
                parts.append(f"CPI of {float(row['cpi']):.2f}")
            elif 'cpi_annual' in row and row['cpi_annual'] is not None:
                parts.append(f"CPI of {float(row['cpi_annual']):.2f}")
            
            if 'unemployment_rate' in row and row['unemployment_rate'] is not None:
                parts.append(f"unemployment rate of {float(row['unemployment_rate']):.2f}%")
            elif 'unemployment_rate_annual' in row and row['unemployment_rate_annual'] is not None:
                parts.append(f"unemployment rate of {float(row['unemployment_rate_annual']):.2f}%")
            
            if 'fed_funds_rate' in row and row['fed_funds_rate'] is not None:
                parts.append(f"Fed Funds Rate of {float(row['fed_funds_rate']):.2f}%")
            elif 'fed_funds_rate_annual' in row and row['fed_funds_rate_annual'] is not None:
                parts.append(f"Fed Funds Rate of {float(row['fed_funds_rate_annual']):.2f}%")
        
        if parts:
            # Natural language formatting
            if len(parts) == 1:
                return f"In {year}, {parts[0]}."
            else:
                metrics_str = ", and ".join([", ".join(parts[:-1]), parts[-1]])
                return f"In {year}, {metrics_str}."
        else:
            return f"Macro data available for {period_str}."
    
    def _generate_sensitivity_summary(self, df: pd.DataFrame, context: Dict) -> str:
        """Generate summary for macro sensitivity queries (betas)"""
        if len(df) == 0:
            return "No sensitivity data found."
        
        row = df.iloc[0]
        ticker = row.get('ticker', 'Unknown')
        name = row.get('name', ticker)
        year = row.get('fiscal_year')
        quarter = row.get('fiscal_quarter')
        
        # Build period string
        if quarter:
            period_str = f"Q{quarter} FY{year}"
        elif year:
            period_str = f"FY{year}"
        else:
            period_str = "the period"
        
        # Determine which sensitivity metrics to show based on query
        question = context.get('question', '').upper()
        parts = []
        
        # Check if quarterly or annual
        is_annual = 'beta_gm_cpi_annual' in row or 'beta_nm_cpi_annual' in row
        
        # Beta to CPI (inflation sensitivity)
        if 'CPI' in question or 'INFLATION' in question or 'BETA' not in question:
            if not is_annual:
                if 'beta_nm_cpi_12q' in row and row['beta_nm_cpi_12q'] is not None:
                    val = float(row['beta_nm_cpi_12q'])
                    parts.append(f"net margin beta to CPI of {val:.6f}")
                if 'beta_om_cpi_12q' in row and row['beta_om_cpi_12q'] is not None:
                    val = float(row['beta_om_cpi_12q'])
                    parts.append(f"operating margin beta to CPI of {val:.6f}")
                if 'beta_gm_cpi_12q' in row and row['beta_gm_cpi_12q'] is not None:
                    val = float(row['beta_gm_cpi_12q'])
                    parts.append(f"gross margin beta to CPI of {val:.6f}")
            else:
                if 'beta_nm_cpi_annual' in row and row['beta_nm_cpi_annual'] is not None:
                    val = float(row['beta_nm_cpi_annual'])
                    parts.append(f"net margin beta to CPI of {val:.6f}")
                if 'beta_om_cpi_annual' in row and row['beta_om_cpi_annual'] is not None:
                    val = float(row['beta_om_cpi_annual'])
                    parts.append(f"operating margin beta to CPI of {val:.6f}")
                if 'beta_gm_cpi_annual' in row and row['beta_gm_cpi_annual'] is not None:
                    val = float(row['beta_gm_cpi_annual'])
                    parts.append(f"gross margin beta to CPI of {val:.6f}")
        
        # Beta to Fed Funds Rate
        if 'FED' in question or 'FEDERAL FUNDS' in question or 'INTEREST RATE' in question:
            if not is_annual:
                if 'beta_nm_ffr_12q' in row and row['beta_nm_ffr_12q'] is not None:
                    val = float(row['beta_nm_ffr_12q'])
                    parts.append(f"net margin beta to Fed rate of {val:.6f}")
                if 'beta_om_ffr_12q' in row and row['beta_om_ffr_12q'] is not None:
                    val = float(row['beta_om_ffr_12q'])
                    parts.append(f"operating margin beta to Fed rate of {val:.6f}")
            else:
                if 'beta_nm_ffr_annual' in row and row['beta_nm_ffr_annual'] is not None:
                    val = float(row['beta_nm_ffr_annual'])
                    parts.append(f"net margin beta to Fed rate of {val:.6f}")
                if 'beta_om_ffr_annual' in row and row['beta_om_ffr_annual'] is not None:
                    val = float(row['beta_om_ffr_annual'])
                    parts.append(f"operating margin beta to Fed rate of {val:.6f}")
        
        # Beta to S&P 500
        if 'S&P' in question or 'SPX' in question or 'MARKET' in question:
            if not is_annual:
                if 'beta_nm_spx_12q' in row and row['beta_nm_spx_12q'] is not None:
                    val = float(row['beta_nm_spx_12q'])
                    parts.append(f"net margin beta to S&P 500 of {val:.6f}")
            else:
                if 'beta_nm_spx_annual' in row and row['beta_nm_spx_annual'] is not None:
                    val = float(row['beta_nm_spx_annual'])
                    parts.append(f"net margin beta to S&P 500 of {val:.6f}")
        
        # Beta to Unemployment
        if 'UNEMPLOYMENT' in question or 'JOBLESS' in question:
            if not is_annual:
                if 'beta_nm_unrate_12q' in row and row['beta_nm_unrate_12q'] is not None:
                    val = float(row['beta_nm_unrate_12q'])
                    parts.append(f"net margin beta to unemployment of {val:.6f}")
            else:
                if 'beta_nm_unrate_annual' in row and row['beta_nm_unrate_annual'] is not None:
                    val = float(row['beta_nm_unrate_annual'])
                    parts.append(f"net margin beta to unemployment of {val:.6f}")
        
        # If no specific betas matched, show key ones
        if not parts:
            if not is_annual:
                if 'beta_nm_cpi_12q' in row and row['beta_nm_cpi_12q'] is not None:
                    val = float(row['beta_nm_cpi_12q'])
                    parts.append(f"net margin beta to CPI of {val:.6f}")
                if 'beta_nm_ffr_12q' in row and row['beta_nm_ffr_12q'] is not None:
                    val = float(row['beta_nm_ffr_12q'])
                    parts.append(f"net margin beta to Fed rate of {val:.6f}")
            else:
                if 'beta_nm_cpi_annual' in row and row['beta_nm_cpi_annual'] is not None:
                    val = float(row['beta_nm_cpi_annual'])
                    parts.append(f"net margin beta to CPI of {val:.6f}")
                if 'beta_nm_ffr_annual' in row and row['beta_nm_ffr_annual'] is not None:
                    val = float(row['beta_nm_ffr_annual'])
                    parts.append(f"net margin beta to Fed rate of {val:.6f}")
        
        if parts:
            metrics_str = ", ".join(parts)
            return f"{name} ({ticker}) macro sensitivity for {period_str}: {metrics_str}."
        else:
            return f"Macro sensitivity data available for {name} ({ticker}) in {period_str}."
