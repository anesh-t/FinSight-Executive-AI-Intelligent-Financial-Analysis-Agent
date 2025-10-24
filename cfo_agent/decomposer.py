"""
Query decomposer: split multi-part questions into ordered tasks
"""
import json
import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()


class QueryDecomposer:
    """Decomposes natural language queries into structured tasks"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        
        # Load router/planner prompt
        with open('prompts/router_planner_prompt.md', 'r') as f:
            self.router_prompt = f.read()
        
        # Load routing examples
        with open('catalog/routing_examples.json', 'r') as f:
            self.examples = json.load(f)['examples']
    
    async def decompose(self, question: str) -> Dict:
        """
        Decompose a natural language question into structured tasks
        
        Args:
            question: User's natural language question
            
        Returns:
            Dict with 'greeting', 'tasks', and 'checks'
        """
        # Simple entity extraction and intent detection as fallback
        import re
        
        # Extract common tickers
        tickers = []
        ticker_patterns = ['AAPL', 'MSFT', 'AMZN', 'GOOG', 'META', 'GOOGL']
        for ticker in ticker_patterns:
            if ticker in question.upper():
                tickers.append(ticker)
        
        # Also check for company names
        company_map = {
            'APPLE': 'AAPL',
            'MICROSOFT': 'MSFT',
            'AMAZON': 'AMZN',
            'GOOGLE': 'GOOG',
            'ALPHABET': 'GOOG',
            'META': 'META',
            'FACEBOOK': 'META'
        }
        
        question_upper = question.upper()
        for name, ticker in company_map.items():
            if name in question_upper and ticker not in tickers:
                tickers.append(ticker)
        
        # Normalize tickers: GOOG and GOOGL represent the same company (Alphabet)
        # Keep only unique companies
        # Use GOOG as canonical since that's what's in the database
        unique_tickers = []
        has_google = False
        for ticker in tickers:
            if ticker in ['GOOG', 'GOOGL']:
                if not has_google:
                    unique_tickers.append('GOOG')  # Use GOOG as canonical (matches database)
                    has_google = True
            elif ticker not in unique_tickers:
                unique_tickers.append(ticker)
        tickers = unique_tickers
        
        # Extract year if present
        year_match = re.search(r'(FY\s*)?(\d{4})', question)
        if year_match:
            year = int(year_match.group(2))
            period = {"fy": year, "fq": None}
        else:
            period = {"fy": None, "fq": None}  # NULL means latest
        
        # Extract quarter if present (multiple patterns)
        # CHECK IN ORDER: most specific first, then more general
        quarter_match = None
        
        # Pattern 1: 1st Q, 2nd Q, 3rd Q, 4th Q (e.g., "3rd Q") - CHECK FIRST
        # Must check before general Q pattern to avoid "1st Q" matching "Q" from "2023"
        if re.search(r'\b([1-4])(ST|ND|RD|TH)\s*Q\b', question_upper):
            quarter_num_match = re.search(r'\b([1-4])(ST|ND|RD|TH)\s*Q\b', question_upper)
            period["fq"] = int(quarter_num_match.group(1))
        # Pattern 2: 1st quarter, 2nd quarter, 3rd quarter, 4th quarter
        elif re.search(r'\b([1-4])(ST|ND|RD|TH)\s+QUARTER', question_upper):
            quarter_num_match = re.search(r'\b([1-4])(ST|ND|RD|TH)\s+QUARTER', question_upper)
            period["fq"] = int(quarter_num_match.group(1))
        # Pattern 3: Q1, Q2, Q3, Q4, q1, q 1, Q 1, etc.
        # Check AFTER ordinal patterns to avoid false matches
        elif re.search(r'Q\s*([1-4])', question_upper):
            quarter_match = re.search(r'Q\s*([1-4])', question_upper)
            period["fq"] = int(quarter_match.group(1))
        # Pattern 4: first, second, third, fourth quarter
        elif 'FIRST QUARTER' in question_upper or 'FIRST-QUARTER' in question_upper:
            period["fq"] = 1
        elif 'SECOND QUARTER' in question_upper or 'SECOND-QUARTER' in question_upper:
            period["fq"] = 2
        elif 'THIRD QUARTER' in question_upper or 'THIRD-QUARTER' in question_upper:
            period["fq"] = 3
        elif 'FOURTH QUARTER' in question_upper or 'FOURTH-QUARTER' in question_upper:
            period["fq"] = 4
        
        # Detect intent from keywords
        # Default: if year but no quarter specified → annual_metrics
        # If quarter specified or "latest quarter" → quarter_snapshot
        intent = "quarter_snapshot"  # default
        
        # Check if this is a year-only query (no quarter specified)
        has_year = period.get("fy") is not None
        has_quarter = period.get("fq") is not None
        
        # Combined/Complete queries (CHECK FIRST - comprehensive views)
        # Keywords: complete, everything, full picture, comprehensive, all metrics, full analysis
        is_complete_query = any(word in question_upper for word in [
            'COMPLETE', 'EVERYTHING', 'FULL PICTURE', 'COMPREHENSIVE',
            'ALL METRICS', 'FULL ANALYSIS', 'COMPLETE PICTURE', 'FULL VIEW',
            'EVERYTHING ABOUT', 'COMPLETE VIEW', 'ALL DATA'
        ])
        
        # Check if it includes macro context or sensitivity
        has_macro_keywords = any(word in question_upper for word in [
            'MACRO', 'GDP', 'CPI', 'INFLATION', 'ECONOMIC', 'ECONOMY',
            'FED RATE', 'UNEMPLOYMENT', 'CONTEXT'
        ])
        has_sensitivity_keywords = any(word in question_upper for word in [
            'SENSITIVITY', 'BETA', 'BETAS', 'CORRELATION'
        ])
        
        # Check if query has a company ticker (company-specific query)
        has_company = len(tickers) > 0
        is_multi_company = len(tickers) >= 2  # Multiple companies for comparison
        
        # Check if this is a stock price query (check before multi-company logic)
        is_stock_query = any(word in question_upper for word in [
            'STOCK PRICE', 'STOCK', 'SHARE PRICE', 'TRADING PRICE', 'STOCK RETURN', 'STOCK PERFORMANCE',
            'OPENING PRICE', 'CLOSING PRICE', 'CLOSE PRICE', 'OPEN PRICE',
            'HIGH PRICE', 'LOW PRICE', 'AVERAGE PRICE', 'AVG PRICE', 'MARKET PRICE'
        ]) or ('RETURN' in question_upper and 'REVENUE' not in question_upper and 'INCOME' not in question_upper)
        
        # Multi-company comparison queries (CHECK FIRST)
        if is_multi_company:
            # Check if this is a stock price query for multiple companies
            if is_stock_query:
                # For multi-company stock queries, query each company separately
                # Don't set a specific multi-company intent, let it fall through to regular stock logic
                is_multi_company = False  # Treat as separate single-company queries
            # Check if user wants macro context with comparison
            elif has_macro_keywords and any(word in question_upper for word in ['COMPARE', 'VS', 'VERSUS', 'AND', 'WITH', 'AFFECTED', 'IMPACTED']):
                # Multi-company comparison WITH macro context
                if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                    intent = "multi_company_macro_quarter"
                else:
                    intent = "multi_company_macro_annual"
            else:
                # Multi-company comparison WITHOUT macro context
                if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                    intent = "multi_company_quarter"
                else:
                    intent = "multi_company_annual"
        # IMPORTANT: If multi-company intent was set, don't override it below
        # Skip remaining intent detection for multi-company queries
        elif not is_multi_company and is_complete_query:
            # Determine quarterly vs annual
            if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                # Quarterly complete query
                if has_sensitivity_keywords or 'FULL' in question_upper:
                    intent = "complete_full_quarterly"  # Layer 3
                elif has_macro_keywords:
                    intent = "complete_macro_context_quarterly"  # Layer 2
                else:
                    intent = "complete_quarterly"  # Layer 1
            else:
                # Annual complete query
                if has_sensitivity_keywords or 'FULL' in question_upper:
                    intent = "complete_full_annual"  # Layer 3
                elif has_macro_keywords:
                    intent = "complete_macro_context_annual"  # Layer 2
                else:
                    intent = "complete_annual"  # Layer 1
        # Company WITH macro context (not an explicit "complete" query but has company + macro)
        elif not is_multi_company and has_company and has_macro_keywords and any(word in question_upper for word in ['WITH', 'AND', 'INCLUDING', 'PLUS']):
            # User wants company data WITH macro context
            if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                intent = "complete_macro_context_quarterly"  # Layer 2
            else:
                intent = "complete_macro_context_annual"  # Layer 2
        # Macro sensitivity queries (CHECK SECOND - company-specific sensitivity to macro)
        # Keywords: sensitivity, beta, response, correlation with macro indicators
        is_sensitivity_query = any(word in question_upper for word in [
            'SENSITIVITY', 'BETA', 'RESPOND', 'RESPONSE', 'CORRELATION',
            'MACRO SENSITIVITY', 'MARGIN SENSITIVITY', 'SENSITIVITY TO',
            'BETA TO', 'RESPOND TO', 'CORRELATION WITH'
        ]) and any(word in question_upper for word in [
            'CPI', 'INFLATION', 'FED', 'FEDERAL FUNDS', 'MACRO', 'ECONOMIC',
            'UNEMPLOYMENT', 'S&P', 'SPX', 'MARKET'
        ])
        
        if not is_multi_company and is_sensitivity_query:
            # Determine if quarterly or annual based on period
            if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                intent = "macro_sensitivity_quarterly"
            else:
                intent = "macro_sensitivity_annual"
        # Macro indicator queries (CHECK THIRD - non-company-specific ONLY)
        # These are non-company-specific: GDP, CPI, unemployment, Fed rate, etc.
        # IMPORTANT: Only route here if NO company ticker was found
        elif not is_multi_company and not has_company and any(word in question_upper for word in [
            'GDP', 'GROSS DOMESTIC PRODUCT',
            'CPI', 'INFLATION', 'CONSUMER PRICE',
            'UNEMPLOYMENT', 'UNEMPLOYMENT RATE', 'JOBLESS',
            'FED RATE', 'FEDERAL FUNDS', 'INTEREST RATE', 'FED FUNDS',
            'YIELD SPREAD', 'YIELD CURVE', 'TERM SPREAD',
            'S&P 500', 'S&P500', 'SPX', 'MARKET INDEX',
            'VIX', 'VOLATILITY INDEX', 'FEAR INDEX',
            'PCE', 'PERSONAL CONSUMPTION',
            'MACRO INDICATOR', 'ECONOMIC INDICATOR'
        ]):
            # Determine if quarterly or annual based on period
            if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                intent = "macro_indicator_quarterly"
            else:
                intent = "macro_indicator_annual"
        # Stock price queries (CHECK SECOND)
        # Check for stock-related keywords including specific price types
        elif not is_multi_company and (
            any(word in question_upper for word in [
                'STOCK PRICE', 'STOCK', 'SHARE PRICE', 'TRADING PRICE', 'STOCK RETURN', 'STOCK PERFORMANCE',
                'OPENING PRICE', 'CLOSING PRICE', 'CLOSE PRICE', 'OPEN PRICE',
                'HIGH PRICE', 'LOW PRICE', 'AVERAGE PRICE', 'AVG PRICE'
            ]) or
            # "return" is stock-related if not talking about revenue
            ('RETURN' in question_upper and 'REVENUE' not in question_upper and 'INCOME' not in question_upper) or
            # Check for VOLATILITY but not if it's about other metrics
            ('VOLATILITY' in question_upper and 'PRICE' in question_upper)
        ):
            # Check if this is a MIXED query (financials + stock price)
            # Keywords for financial metrics
            has_financial_metrics = any(word in question_upper for word in [
                'REVENUE', 'NET INCOME', 'OPERATING INCOME', 'GROSS PROFIT',
                'MARGIN', 'ROE', 'ROA', 'EARNINGS', 'PROFIT', 'SALES',
                'ASSETS', 'LIABILITIES', 'EQUITY', 'CASH FLOW', 'CAPEX',
                'DIVIDENDS', 'BUYBACKS', 'EPS'
            ])
            
            if has_financial_metrics:
                # This is a combined query - route to complete template
                if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                    intent = "complete_quarterly"
                else:
                    intent = "complete_annual"
            else:
                # Pure stock price query
                if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                    intent = "stock_price_quarterly"
                else:
                    intent = "stock_price_annual"
        # Peer queries
        elif not is_multi_company and any(word in question_upper for word in ['WHO LED', 'RANK', 'LEADER', 'PEER', 'COMPARE ALL']):
            if any(word in question_upper for word in ['ANNUAL', 'YEAR', 'FY']):
                intent = "peer_leaderboard_annual"
            else:
                intent = "peer_leaderboard_quarter"
        # Annual queries: year specified without quarter, or explicit "annual"/"year"/"total"
        # This handles revenue, expenses (R&D, SG&A, COGS), and all other metrics
        elif not is_multi_company and has_year and not has_quarter:
            intent = "annual_metrics"
        elif not is_multi_company and any(word in question_upper for word in ['ANNUAL', 'TOTAL', 'FULL YEAR']):
            intent = "annual_metrics"
        # Explicit quarter queries - handles revenue, expenses, and all quarterly metrics
        elif not is_multi_company and (has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4', 'LATEST QUARTER'])):
            intent = "quarter_snapshot"
        # Growth queries
        elif not is_multi_company and any(word in question_upper for word in ['GROWTH', 'YOY', 'QOQ', 'CAGR']):
            if 'CAGR' in question_upper or '3-YEAR' in question_upper or '5-YEAR' in question_upper:
                intent = "growth_annual_cagr"
            else:
                intent = "growth_qoq_yoy"
        
        # Build few-shot prompt with examples
        few_shot_examples = self._build_few_shot_examples()
        
        messages = [
            SystemMessage(content=self.router_prompt + "\n\n" + few_shot_examples),
            HumanMessage(content=f"Question: {question}\n\nOutput (JSON only):")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Parse JSON response
            result = json.loads(response.content)
            
            # Validate structure
            if 'tasks' not in result:
                result['tasks'] = []
            if 'greeting' not in result:
                result['greeting'] = ""
            if 'checks' not in result:
                result['checks'] = ["use_whitelist", "bind_params", "limit_results"]
            
            # If entities are empty but we found tickers, add them
            if result['tasks'] and not result['tasks'][0].get('entities'):
                result['tasks'][0]['entities'] = tickers
            
            # OVERRIDE INTENT if multiple companies detected
            # This ensures multi-company queries use the right templates
            # Note: Filter out duplicate tickers (GOOG/GOOGL represent same company)
            unique_companies = set()
            for t in tickers:
                if t in ['GOOG', 'GOOGL']:
                    unique_companies.add('GOOG')  # Normalize to GOOG (matches database)
                else:
                    unique_companies.add(t)
            
            if result['tasks'] and len(unique_companies) >= 2:
                current_intent = result['tasks'][0].get('intent', '')
                
                # For stock price queries with multiple companies, keep as single task
                # The formatter will handle combining them into a nice multi-company summary
                if current_intent not in ['stock_price_annual', 'stock_price_quarterly']:
                    # For non-stock queries, use multi-company templates
                    # Check if we need macro context
                    if has_macro_keywords and any(word in question_upper for word in ['COMPARE', 'VS', 'VERSUS', 'AND', 'WITH', 'AFFECTED', 'IMPACTED', 'HOW']):
                        # Multi-company with macro
                        if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                            result['tasks'][0]['intent'] = 'multi_company_macro_quarter'
                        else:
                            result['tasks'][0]['intent'] = 'multi_company_macro_annual'
                    else:
                        # Multi-company without macro
                        if has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4']):
                            result['tasks'][0]['intent'] = 'multi_company_quarter'
                        elif has_year or any(word in question_upper for word in ['ANNUAL', 'YEAR', 'FY', '2023', '2024', '2022', '2021', '2020']):
                            result['tasks'][0]['intent'] = 'multi_company_annual'
                        else:
                            # Default to quarterly for multi-company
                            result['tasks'][0]['intent'] = 'multi_company_quarter'
            
            return result
        except Exception as e:
            # Fallback: create a single task with detected intent and extracted tickers
            # Make sure intent is using the same logic
            fallback_intent = intent  # Already computed above with year/quarter logic
            
            return {
                "greeting": "",
                "tasks": [{
                    "intent": fallback_intent,
                    "entities": tickers,
                    "period": period,
                    "measures": []
                }],
                "checks": ["use_whitelist", "bind_params", "limit_results"],
                "error": f"Exception in decompose: {str(e)}"
            }
    
    def _build_few_shot_examples(self) -> str:
        """Build few-shot examples from catalog"""
        examples_text = "\n\n## Examples:\n\n"
        
        for i, example in enumerate(self.examples[:5], 1):  # Use first 5 examples
            examples_text += f"### Example {i}:\n"
            examples_text += f"Question: {example['question']}\n"
            examples_text += f"Output: {json.dumps(example['expected_output'], indent=2)}\n\n"
        
        return examples_text
