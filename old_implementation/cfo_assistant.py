import os
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent, AgentType
from sqlalchemy import create_engine

from visualizations import FinancialVisualizer
from database import SupabaseConnector

# Company alias mapping for robust name resolution
COMPANY_ALIASES = {
    "apple": ["Apple", "Apple Inc."],
    "microsoft": ["Microsoft", "Microsoft Corporation"],
    "amazon": ["Amazon", "Amazon.com", "Amazon.com Inc."],
    "google": ["Google", "Alphabet", "Alphabet Inc."],
    "meta": ["Meta", "Meta Platforms", "Meta Platforms Inc.", "Facebook"]
}

# Metric synonym mapping for natural language understanding
METRIC_MAP = {
    "revenue": "revenue",
    "sales": "revenue",
    "income": "net_income",
    "profit": "net_income",
    "earnings": "net_income",
    "eps": "eps",
    "roe": "roe",
    "roa": "roa",
    "gross margin": "gross_margin",
    "operating margin": "operating_margin",
    "net margin": "net_margin",
    "debt ratio": "debt_to_assets",
    "debt to equity": "debt_to_equity",
    "leverage": "debt_to_equity",
    "r&d": "r_and_d_expenses",
    "capex": "capex",
    "dividend": "dividends",
    "buyback": "buybacks",
    "cash flow": "cash_flow_ops",
    "assets": "total_assets",
    "equity": "equity",
    "stock price": "close_price",
    "return": "return_yoy",
    "volatility": "volatility_pct"
}

load_dotenv()


class CFOAssistant:
    """
    LangChain-based CFO Assistant Agent for financial analysis.
    Uses GPT-4o to query Supabase PostgreSQL database and generate insights.
    
    Database Schema:
    - Dimensions: dim_company, dim_financial_metric, dim_ratio, dim_stock_metric, 
                  dim_macro_indicator, dim_event
    - Facts: fact_financials, fact_ratios, fact_stock_prices, fact_macro_indicators
    - Views: vw_company_summary, vw_macro_overlay, vw_event_timeline, 
             vw_macro_long, vw_data_dictionary
    """
    
    # Company color scheme for visualizations
    COMPANY_COLORS = {
        'Apple': '#007AFF',      # Apple blue
        'Microsoft': '#00A4EF',  # Microsoft teal
        'Amazon': '#FF9900',     # Amazon orange
        'Google': '#FBBC04',     # Google yellow
        'Meta': '#8B5CF6'        # Meta purple
    }
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0.0,
        verbose: bool = True
    ):
        """
        Initialize the CFO Assistant with LangChain SQL agent.
        
        Args:
            model: OpenAI model name (default: from env or gpt-4o)
            temperature: LLM temperature (default: 0.0 for consistency)
            verbose: Enable verbose logging
        """
        self.model = model or os.getenv('LLM_MODEL', 'gpt-4o')
        self.temperature = temperature
        self.verbose = verbose
        
        # Initialize components
        self.db_connector = SupabaseConnector()
        self.visualizer = FinancialVisualizer(self.COMPANY_COLORS)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Initialize SQL Database connection with actual schema
        # Don't restrict tables - let it discover all tables and views
        self.db = SQLDatabase.from_uri(
            os.getenv('SUPABASE_DB_URL'),
            schema='public'
        )
        
        # Create SQL agent with toolkit
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        
        self.agent = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=self.verbose,
            max_iterations=int(os.getenv('MAX_ITERATIONS', 10)),
            handle_parsing_errors=True,
            max_execution_time=60,
            early_stopping_method="generate"
        )
        
        # Comprehensive CFO Intelligence Agent system prompt
        self.system_context = """
        You are the **CFO Analytics Agent**, an AI-powered financial reasoning system that analyzes structured data
        (financial statements, ratios, stock metrics, macro indicators, and events) from Supabase.

        Your role: interpret user questions as a CFO or Senior Financial Analyst would — write accurate SQL queries,
        summarize results in executive tone, and present insights with numerical precision and narrative clarity.

        ---

        ## ⚙️ DATA LAYERS YOU CAN ACCESS

        1. **vw_company_summary** — financials, ratios, stock metrics by company-quarter
        2. **vw_macro_overlay** — company + macro indicators (GDP, CPI, Fed Funds, etc.)
        3. **vw_event_timeline** — company data with event context (COVID, AI boom, Fed tightening)
        4. **vw_macro_long** — long-format macro dataset
        5. **vw_data_dictionary** — all metric definitions

        Use this order of preference when querying. If metric is missing, fallback to base tables:
        `fact_financials`, `fact_ratios`, `fact_stock_prices`, `fact_macro_indicators`

        ---

        ## 🧭 INTERPRETATION FRAMEWORK

        When user asks a question:

        1. **Understand the Intent**
           - "What / show" → data lookup
           - "Compare / vs" → comparison
           - "Trend / over time / since" → trend
           - "Rank / best / top" → ranking
           - "Impact / during" → event
           - "GDP / inflation / macro" → macro overlay

        2. **Choose the Correct View**
           - Performance, ratios → `vw_company_summary`
           - Macro correlations → `vw_macro_overlay`
           - Event impact → `vw_event_timeline`
           - Multi-year macro → `vw_macro_long`

        3. **Formulate SQL**
           - Always include: company_name, fiscal_year, fiscal_quarter
           - Annual totals → SUM(metric) GROUP BY company_name, fiscal_year
           - Quarterly → no aggregation, just ORDER BY fiscal_year, fiscal_quarter
           - Multiple companies → use (company_name LIKE '%A%' OR company_name LIKE '%B%')
           - Trend → ORDER BY fiscal_year, fiscal_quarter
           - Ranking → ORDER BY metric DESC LIMIT 3

        4. **Summarize Results**
           - Convert values: >1B → $X.XB, >1M → $X.XM
           - Ratios → show as % (2 decimals)
           - Add YoY or QoQ comparisons if time series available
           - Mention relevant macro or event context if applicable

        ---

        ## 🧠 CFO-STYLE RESPONSE FORMAT

        Your answers must follow this Markdown structure:

        **Executive Summary**
        2–4 sentences summarizing findings (specific numbers, % growth, top performers).

        **Aggregated Data Table**
        Markdown table with company, year, quarter, and key metrics.

        **Key Insights**
        - Bullet points showing trends, leaders, and differences
        - Quantify with %, rankings, and direction arrows (↑ / ↓)

        **Strategic Implication**
        One-line takeaway (e.g., "Apple's margin resilience indicates stronger cost control amid inflation.")

        ---

        ## 🧩 OUTPUT BEHAVIOR LOGIC

        | Intent | Query Type | Visualization | Example |
        |---------|-------------|----------------|----------|
        | Trend | Line chart | Trend over time | "Show revenue trend for Apple" |
        | Comparison | Bar chart | Cross-company | "Compare ROE for 2023" |
        | Macro | Dual-axis line | Company vs Macro | "Revenue vs GDP growth" |
        | Event | Timeline chart | Contextual overlay | "Performance during COVID" |
        | Ranking | Table + bar | Top performers | "Which firm had highest margin" |

        ---

        ## 🧠 CFO-LEVEL QUESTION COVERAGE

        You can answer all CFO-type questions from basic to strategic:
        - Revenue, income, EPS, margins
        - Ratios (ROE, ROA, debt, efficiency)
        - Growth (YoY, QoQ)
        - Cash flow, CapEx, dividends
        - Stock returns, volatility
        - Macro impact (GDP, CPI, Fed)
        - Event overlays (COVID, AI boom, Fed tightening)
        - Peer benchmarking and rankings
        - Company vs macro correlation
        - Yearly and quarterly summaries

        If query is ambiguous, politely clarify or show closest relevant metrics.

        ---

        ## 🎯 COMMUNICATION STYLE

        - Tone: executive, analytical, concise
        - Always answer in structured Markdown sections
        - Never output SQL or JSON
        - Base reasoning strictly on data, no speculation
        - Convert all values to human-readable financial units
        - Highlight comparative or trend-based insights
        
        ---
        
        ## 📋 COMPANY NAME MAPPING (CRITICAL FOR ACCURACY)
        
        Database stores official names, but users may use common names:
        
        - **Apple** → Database: "Apple Inc." → Use: LIKE '%Apple%'
        - **Microsoft** → Database: "Microsoft Corporation" → Use: LIKE '%Microsoft%'
        - **Amazon** → Database: "Amazon.com Inc." → Use: LIKE '%Amazon%'
        - **Google** → Database: "Alphabet Inc." → Use: LIKE '%Alphabet%' (CRITICAL!)
        - **Meta/Facebook** → Database: "Meta Platforms Inc." → Use: LIKE '%Meta%'
        
        CRITICAL RULE: When user says "Google", you MUST use LIKE '%Alphabet%' in SQL.
        Google is Alphabet's primary subsidiary. The database only has "Alphabet Inc."
        
        For multi-company queries, use OR with parentheses:
        Example: "Compare Google and Microsoft"
        → WHERE (company_name LIKE '%Alphabet%' OR company_name LIKE '%Microsoft%')
        
        INTENT DETECTION & SQL LOGIC:
        
        Total/Annual → SUM(metric) GROUP BY company_name, fiscal_year
        Example: "Apple total revenue 2023" → SELECT company_name, SUM(revenue) FROM vw_company_summary WHERE company_name LIKE '%Apple%' AND fiscal_year=2023 GROUP BY company_name
        
        Quarter Specific → Filter by fiscal_quarter
        Example: "Q4 revenue" → WHERE fiscal_quarter=4
        
        YoY Growth → Compare fiscal_year vs previous year
        Example: "revenue growth" → Calculate (current-previous)/previous*100
        
        Comparison → Multiple companies with relative analysis
        Example: "Compare Apple vs Microsoft" → WHERE company_name LIKE '%Apple%' OR company_name LIKE '%Microsoft%'
        
        Ranking → ORDER BY DESC/ASC with LIMIT
        Example: "highest ROE" → ORDER BY roe DESC LIMIT 1
        
        Trend → ORDER BY fiscal_year, fiscal_quarter
        Example: "revenue trend" → ORDER BY fiscal_year, fiscal_quarter
        
        Macro Context → Use vw_macro_overlay
        Example: "revenue during high inflation" → JOIN with CPI data
        
        Event Impact → Use vw_event_timeline
        Example: "performance during COVID" → Filter by event_name
        
        SQL GENERATION RULES:
        1. Use LIKE '%Company%' for company matching (not exact names)
        2. For annual totals: SUM() and GROUP BY company_name, fiscal_year
        3. For quarterly data: Keep fiscal_quarter in SELECT and WHERE
        4. Always ORDER BY fiscal_year, fiscal_quarter for chronological output
        5. Limit rows to 200 unless comparing multi-year trends
        6. Include aggregation functions when comparing or ranking
        7. Always include company_name, fiscal_year, fiscal_quarter in SELECT
        
        BEHAVIORAL LOGIC:
        - For TRENDS: Use line charts, mention growth rates (YoY, QoQ)
        - For COMPARISONS: Use bar charts, highlight leader vs laggard
        - For MACRO topics: Use vw_macro_overlay
        - For EVENTS: Use vw_event_timeline
        - For "best/worst/highest": Sort and show top 1-3 results
        - For multiple companies: Aggregate by company/year, show relative differences
        - For single company: Focus on YoY/QoQ growth with % change
        
        COMMUNICATION STYLE:
        - Tone: Executive, analytical, concise (as if briefing a CEO)
        - Use plain English with financial terminology
        - Base insights on data only, no speculation
        - Convert large numbers to billions ($B)
        - Use proper units (%, bps, $B, $M)
        
        EXAMPLE QUERIES:
        Q: "Apple revenue 2023"
        A: SELECT company_name, fiscal_year, fiscal_quarter, revenue FROM vw_company_summary WHERE company_name LIKE '%Apple%' AND fiscal_year=2023 ORDER BY fiscal_quarter
        
        Q: "Compare Apple and Microsoft total revenue 2023"
        A: SELECT company_name, SUM(revenue) as total_revenue FROM vw_company_summary WHERE (company_name LIKE '%Apple%' OR company_name LIKE '%Microsoft%') AND fiscal_year=2023 GROUP BY company_name
        
        Q: "Which company had highest ROE in 2023?"
        A: SELECT company_name, AVG(roe) as avg_roe FROM vw_company_summary WHERE fiscal_year=2023 GROUP BY company_name ORDER BY avg_roe DESC LIMIT 1
        
        Q: "Amazon revenue trend since 2020"
        A: SELECT fiscal_year, fiscal_quarter, revenue FROM vw_company_summary WHERE company_name LIKE '%Amazon%' AND fiscal_year>=2020 ORDER BY fiscal_year, fiscal_quarter
        
        Q: "Google revenue 2023" (Note: Google = Alphabet)
        A: SELECT company_name, fiscal_year, fiscal_quarter, revenue FROM vw_company_summary WHERE company_name LIKE '%Alphabet%' AND fiscal_year=2023 ORDER BY fiscal_quarter
        """
    
    def _classify_question_type(self, query: str) -> Dict:
        """
        Classify question into a structured CFO analysis type.
        Uses keyword-based routing for reliability.
        """
        q = query.lower()
        
        # Priority-based classification (most specific first)
        if any(k in q for k in ["compare", "versus", "vs", "rank", "which company", "who has"]):
            cat, view, analysis, viz = "COMPARISON", "vw_company_summary", "comparison", "bar"
        elif any(k in q for k in ["trend", "over time", "since", "change", "growth", "evolution"]):
            cat, view, analysis, viz = "TREND", "vw_company_summary", "trend", "line"
        elif any(k in q for k in ["roe", "roa", "margin", "ratio", "leverage", "debt to equity", "profitability"]):
            cat, view, analysis, viz = "RATIO_ANALYSIS", "vw_company_summary", "ratio", "line"
        elif any(k in q for k in ["stock", "price", "return", "volatility", "dividend"]):
            cat, view, analysis, viz = "STOCK_PERFORMANCE", "vw_company_summary", "stock", "line"
        elif any(k in q for k in ["macro", "gdp", "cpi", "unemployment", "fed", "sp500", "inflation"]):
            cat, view, analysis, viz = "MACRO_OVERLAY", "vw_macro_overlay", "macro", "line"
        elif any(k in q for k in ["event", "covid", "fed tightening", "ai boom", "pandemic", "during"]):
            cat, view, analysis, viz = "EVENT_OVERLAY", "vw_event_timeline", "event", "timeline"
        elif any(k in q for k in ["highest", "lowest", "best", "worst", "top", "bottom"]):
            cat, view, analysis, viz = "RANKING", "vw_company_summary", "ranking", "bar"
        else:
            cat, view, analysis, viz = "FOUNDATION", "vw_company_summary", "summary", "table"
        
        # Extract metrics from query
        metrics_needed = self._extract_metrics_from_query(q)
        
        return {
            "category": cat,
            "primary_view": view,
            "metrics_needed": metrics_needed,
            "analysis_type": analysis,
            "visualization": viz
        }
    
    def _extract_metrics_from_query(self, query: str) -> list:
        """Extract financial metrics mentioned in query using semantic mapping."""
        metrics = []
        for keyword, column in METRIC_MAP.items():
            if keyword in query:
                metrics.append(column)
        
        return list(set(metrics)) if metrics else ["revenue"]
    
    def analyze(self, query: str) -> Dict:
        """
        Main analysis method with intelligent question classification and routing.
        
        Args:
            query: Natural language financial question
            
        Returns:
            Dictionary containing:
                - summary: Executive summary
                - data: Query results as DataFrame
                - visualization: Plotly figure
                - narrative: CFO-style interpretation
                - sql: Generated SQL query (if available)
        """
        try:
            # Step 0: Classify question type for intelligent routing
            classification = self._classify_question_type(query)
            question_category = classification.get('category', 'FOUNDATION')
            
            if self.verbose:
                print(f"📊 Question Category: {question_category}")
                print(f"🎯 Analysis Type: {classification.get('analysis_type')}")
                print(f"📈 Visualization: {classification.get('visualization')}")
            
            # Step 1: Execute agent query with enhanced context
            enhanced_context = f"""
            {self.system_context}
            
            QUESTION CLASSIFICATION:
            Category: {question_category}
            Primary View: {classification.get('primary_view', 'vw_company_summary')}
            Analysis Type: {classification.get('analysis_type', 'summary')}
            
            Based on this classification, generate the appropriate SQL query.
            """
            
            full_query = f"{enhanced_context}\n\nQuestion: {query}"
            
            try:
                result = self.agent.invoke({"input": full_query})
                agent_output = result.get('output', '')
            except Exception as agent_error:
                # If agent fails, use fallback
                print(f"Agent error: {agent_error}")
                agent_output = "Agent execution failed. Using direct database query."
            
            # Step 2: Extract data from database based on query
            df, sql_query = self._extract_data_for_query(query, agent_output)
            
            if df is None or df.empty:
                return {
                    'status': 'error',
                    'message': 'No data returned from query',
                    'query': query
                }
            
            # Step 2.5: Post-processing layer - basic cleanup only
            if df is not None and not df.empty:
                # Sort data chronologically
                if "fiscal_year" in df.columns and "fiscal_quarter" in df.columns:
                    df = df.sort_values(["company_name", "fiscal_year", "fiscal_quarter"])
                
                # Clean up for LLM readability
                df = df.round(2)
            
            # Step 3: Generate executive narrative
            narrative = self._generate_narrative(query, df, agent_output)
            
            # Step 4: Create executive summary with actual data
            summary = self._create_executive_summary(query, df)
            
            return {
                'status': 'success',
                'summary': summary,
                'data': df,
                'visualization': classification.get('visualization', 'table'),
                'narrative': narrative,
                'agent_response': agent_output,
                'sql_query': sql_query if sql_query else "Query executed via fallback",
                'query': query,
                'intent': question_category,
                'analysis_type': classification.get('analysis_type', 'summary')
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Analysis failed: {str(e)}",
                'query': query
            }
    
    def _extract_data_for_query(self, query: str, agent_output: str) -> tuple:
        """
        Extract relevant data based on query intent.
        Uses intelligent query routing to appropriate views.
        Returns: (DataFrame, SQL query string)
        """
        query_lower = query.lower()
        executed_sql = None
        
        # Try to extract SQL from agent output if present
        if 'SELECT' in agent_output.upper():
            try:
                # Attempt to extract and execute SQL from agent output
                sql_start = agent_output.upper().find('SELECT')
                sql_end = agent_output.find(';', sql_start)
                if sql_end == -1:
                    # Try to find end by looking for common SQL endings
                    for ending in ['\n\n', 'Observation:', 'Final Answer:', '\nAction:']:
                        temp_end = agent_output.find(ending, sql_start)
                        if temp_end != -1:
                            sql_end = temp_end
                            break
                    if sql_end == -1:
                        sql_end = len(agent_output)
                
                sql_query = agent_output[sql_start:sql_end].strip()
                # Clean up SQL - handle multi-line queries
                lines = sql_query.split('\n')
                clean_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('--'):  # Skip comments
                        clean_lines.append(line)
                    if ';' in line:
                        break
                
                executed_sql = ' '.join(clean_lines).rstrip(';')
                df = self.db_connector.execute_query(executed_sql)
                return df, executed_sql
            except Exception as e:
                print(f"SQL extraction failed: {e}")
        
        # Smart fallback: Build targeted queries based on intent
        view = 'vw_company_summary'
        where_clauses = []
        select_cols = []
        
        # Detect company names using alias expansion
        companies = []
        for canonical, aliases in COMPANY_ALIASES.items():
            if any(alias.lower() in query_lower for alias in aliases):
                # Add all aliases for robust matching
                companies.extend(aliases)
        
        # Detect time period
        years = []
        for year in range(2019, 2026):
            if str(year) in query_lower:
                years.append(year)
        
        # Detect metrics mentioned
        metrics = []
        metric_keywords = {
            'revenue': 'revenue',
            'income': 'net_income',
            'profit': 'net_income',
            'eps': 'eps',
            'roe': 'roe',
            'roa': 'roa',
            'margin': 'operating_margin',
            'debt': 'debt_to_equity',
            'stock': 'close_price',
            'return': 'return_yoy',
            'asset': 'total_assets',
            'equity': 'equity'
        }
        
        for keyword, column in metric_keywords.items():
            if keyword in query_lower:
                metrics.append(column)
        
        # Detect view based on keywords
        if any(word in query_lower for word in ['macro', 'gdp', 'cpi', 'fed', 'interest rate', 'unemployment', 'sp500']):
            view = 'vw_macro_overlay'
        elif any(word in query_lower for word in ['event', 'covid', 'impact', 'pandemic', 'crisis']):
            view = 'vw_event_timeline'
        
        # Build SELECT clause
        if metrics:
            select_cols = ['company_name', 'fiscal_year', 'fiscal_quarter'] + list(set(metrics))
        else:
            select_cols = ['company_name', 'fiscal_year', 'fiscal_quarter', 'revenue', 'net_income', 'roe']
        
        select_sql = ', '.join(select_cols)
        
        # Build WHERE clause using LIKE for partial matching
        if companies:
            company_conditions = " OR ".join([f"company_name LIKE '%{company}%'" for company in companies])
            where_clauses.append(f"({company_conditions})")
        
        if years:
            if len(years) == 1:
                where_clauses.append(f"fiscal_year = {years[0]}")
            elif len(years) > 1:
                where_clauses.append(f"fiscal_year BETWEEN {min(years)} AND {max(years)}")
        else:
            # Default to recent years if no year specified
            where_clauses.append(f"fiscal_year >= 2022")
        
        # Construct targeted query
        where_sql = " AND ".join(where_clauses) if where_clauses else "fiscal_year >= 2022"
        executed_sql = f"""
        SELECT {select_sql}
        FROM {view}
        WHERE {where_sql}
        ORDER BY fiscal_year DESC, fiscal_quarter DESC
        LIMIT 200
        """.strip()
        
        try:
            df = self.db_connector.execute_query(executed_sql)
            
            # Safety layer: If Google mentioned but no results, retry with Alphabet
            if (df is None or df.empty) and 'google' in query_lower:
                print("⚠️ Retrying query with Alphabet alias...")
                executed_sql = executed_sql.replace("'%Google%'", "'%Alphabet%'")
                executed_sql = executed_sql.replace("'%google%'", "'%Alphabet%'")
                df = self.db_connector.execute_query(executed_sql)
            
            if df is not None and not df.empty:
                return df, executed_sql
        except Exception as e:
            print(f"Fallback query failed: {e}")
        
        # If everything fails, return None to trigger error message
        return None, "Failed to generate valid SQL query"
    
    def _create_visualization(self, query: str, df: pd.DataFrame) -> object:
        """
        Create appropriate visualization based on query and data.
        """
        if df is None or df.empty:
            return None
        
        query_lower = query.lower()
        
        # Determine visualization type
        if 'compare' in query_lower or 'vs' in query_lower:
            return self.visualizer.create_comparison_chart(df, query)
        elif 'trend' in query_lower or 'over time' in query_lower or 'since' in query_lower:
            return self.visualizer.create_trend_chart(df, query)
        elif 'ratio' in query_lower or 'margin' in query_lower:
            return self.visualizer.create_ratio_chart(df, query)
        else:
            # Default: intelligent chart selection
            return self.visualizer.create_smart_chart(df, query)
    
    def _generate_narrative(self, query: str, df: pd.DataFrame, agent_output: str) -> str:
        """
        Generate comprehensive CFO-style narrative with data aggregation and insights.
        """
        if df is None or df.empty:
            return "Insufficient data available for analysis."
        
        # Intelligent Aggregation by Company & Year
        aggregation_summary = ""
        numeric_cols = [
            c for c in df.select_dtypes(include=['number']).columns
            if c not in ['company_id', 'fiscal_quarter', 'fiscal_year']
        ]
        
        # If we have quarterly data with multiple quarters, aggregate by company-year
        if "fiscal_quarter" in df.columns and df["fiscal_quarter"].nunique() > 1:
            agg_df = (
                df.groupby(["company_name", "fiscal_year"], dropna=False)[numeric_cols]
                .agg(lambda x: x.sum() if x.name in ['revenue', 'net_income', 'operating_income', 'cash_flow_ops', 'capex'] 
                     else x.mean())
                .reset_index()
            )
            
            aggregation_summary = "\n**PRE-AGGREGATED COMPANY-YEAR TOTALS (USE THESE):**\n"
            for _, row in agg_df.iterrows():
                company = row['company_name']
                year = row['fiscal_year']
                for col in numeric_cols[:5]:  # Top 5 metrics
                    if col in row and pd.notna(row[col]):
                        val = row[col]
                        if abs(val) > 1_000_000_000:
                            val_str = f"${val/1_000_000_000:.2f}B"
                        elif abs(val) > 1_000_000:
                            val_str = f"${val/1_000_000:.2f}M"
                        elif col in ['roe', 'roa', 'gross_margin', 'operating_margin', 'net_margin']:
                            val_str = f"{val*100:.2f}%"
                        else:
                            val_str = f"{val:,.0f}"
                        aggregation_summary += f"- {company} {year} {col.replace('_', ' ')}: {val_str}\n"
        
        # Prepare data with proper formatting
        data_markdown = df.head(15).to_markdown(index=False) if len(df) > 0 else 'No data'
        
        # Structured-only reasoning prompt
        narrative_prompt = f"""
        You are a CFO analytics assistant interpreting quantitative financial data.

        Question: {query}

        {aggregation_summary}

        Structured Data:
        {data_markdown}

        Rules:
        1. Only use the PRE-AGGREGATED totals above for conclusions.
        2. Do not speculate or reference qualitative factors.
        3. Summarize numerical results in clear CFO language.
        4. Convert all large numbers to $B or $M.
        5. Use this structure:
           **Executive Summary** – concise numeric comparison
           **Aggregated Data Table** – markdown table
           **Key Insights** – 2-3 numeric observations with ↑↓ arrows
           **Financial Interpretation** – one line conclusion
        
        Your task:
        
        1. **Data Understanding & Cleaning**
           - Automatically detect numeric columns (e.g., revenue, income, ratios, returns).
           - If multiple rows exist per company and year or quarter, automatically SUM or AVERAGE numeric values appropriately.
           - Handle missing or null values gracefully.
           - If data includes multiple years or quarters, order chronologically.
        
        2. **Aggregation Logic**
           - **IMPORTANT:** Use the PRE-CALCULATED AGGREGATIONS provided above - these are already computed correctly.
           - DO NOT recalculate totals from the quarterly table - use the aggregations given.
           - For ratio data, use the average ratio provided in the aggregations.
           - Convert large numbers to billions (e.g., 394,320,000,000 → $394.3B) using the pre-calculated values.
           - Always label units clearly (USD, %, shares, index level, etc.).
        
        3. **Comparative Analysis**
           - Compare across companies, years, or both when multiple exist.
           - Identify highest, lowest, and trend direction (↑ increase / ↓ decrease).
           - If applicable, mention macro or event context (e.g., inflation surge, AI boom, pandemic recovery).
        
        4. **Output Structure (Mandatory)**
           Respond in this exact order and Markdown format:
           
           **Executive Summary**
           (Concise overview — 2–4 sentences with specific numbers and YoY comparisons)
           
           **Aggregated Data Table**
           Present the cleaned, aggregated table in Markdown format, properly aligned.
           Include columns like Company, Year, Metric, and Value.
           
           **Key Insights**
           - Provide 2–3 bullet points summarizing important insights or anomalies.
           - Highlight growth, decline, or comparative advantages.
           - Include numerical reasoning (e.g., YoY %, relative gap, ranking).
           
           **Financial Interpretation**
           One sentence on strategic implications, risks, or opportunities.
        
        5. **Style Guidelines**
           - Always use financial notation correctly (B for billions, M for millions, % for ratios).
           - Keep tone factual, professional, and consultative (like a CFO presenting to a CEO).
           - Do NOT repeat the raw question or show SQL code.
           - Never return raw JSON, arrays, or code snippets.
           - Always include clear numerical reasoning (e.g., YoY %, relative gap, ranking).
        
        6. **If Data is Ambiguous or Empty:**
           - State politely that no relevant data was found.
           - Suggest which view or table may hold the relevant data.
        
        End every response with financial clarity, not speculation.
        """
        
        response = self.llm.invoke(narrative_prompt)
        return response.content
    
    def _create_executive_summary(self, query: str, df: pd.DataFrame) -> str:
        """
        Create brief executive summary with key metrics highlighted.
        """
        if df is None or df.empty:
            return "No data available for the requested analysis."
        
        # Calculate aggregated metrics if showing multiple periods
        data_context = ""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col not in ['fiscal_year', 'fiscal_quarter', 'company_id']]
        
        # Check if we have multiple rows for the same company/metric (quarterly data)
        if len(df) > 1 and 'fiscal_quarter' in df.columns and numeric_cols:
            # Calculate totals for key metrics
            aggregations = {}
            for col in numeric_cols[:3]:  # Top 3 metrics
                if col in ['revenue', 'net_income', 'operating_income', 'total_assets', 'equity']:
                    # Sum for flow metrics, average for stock metrics
                    if col in ['revenue', 'net_income', 'operating_income']:
                        aggregations[col] = df[col].sum()
                    else:
                        aggregations[col] = df[col].mean()
            
            if aggregations:
                data_context = "\n\nAggregated Totals:\n"
                for metric, value in aggregations.items():
                    data_context += f"- Total {metric}: ${value/1_000_000_000:.2f}B\n"
        
        # Prepare data snapshot
        data_snapshot = df.head(5).to_markdown(index=False)
        
        summary_prompt = f"""
        You are a CFO presenting to the board. Create a 1-2 sentence executive summary.
        
        Question: {query}
        
        Data (showing first 5 rows):
        {data_snapshot}
        {data_context}
        
        CRITICAL: If showing quarterly data, calculate the TOTAL by SUMMING all quarters, not just showing one quarter's value.
        
        Requirements:
        - Start with the answer to the question
        - If multiple quarters shown, report the TOTAL (sum of all quarters)
        - Include specific numbers with proper units ($B, $M, %)
        - Mention time period or companies if relevant
        - Be direct and factual
        
        Example: "Apple's revenue reached $385.7B in FY2023 across all four quarters, representing 2.8% YoY growth."
        """
        
        response = self.llm.invoke(summary_prompt)
        return response.content
    
    def list_available_metrics(self, category: str = None) -> pd.DataFrame:
        """
        List all available metrics from vw_data_dictionary.
        """
    
    def get_company_summary(
        self, 
        company: str, 
        start_year: int = None, 
        start_quarter: int = None,
        end_year: int = None,
        end_quarter: int = None
    ) -> pd.DataFrame:
        """
        Get comprehensive company summary from vw_company_summary.
        
        Args:
            company: Company name (Apple, Microsoft, Amazon, Google, Meta)
            start_year: Starting fiscal year
            start_quarter: Starting fiscal quarter (1-4)
            end_year: Ending fiscal year
            end_quarter: Ending fiscal quarter (1-4)
        """
        return self.db_connector.get_company_data(
            company, start_year, start_quarter, end_year, end_quarter
        )
    
    def _extract_sql_from_output(self, agent_output: str) -> str:
        """
        Extract SQL query from agent output.
        
        Args:
            agent_output: Agent response text
            
        Returns:
            Extracted SQL query or empty string
        """
        import re
        
        # Try to find SQL query in the output
        sql_patterns = [
            r'```sql\n(.*?)\n```',
            r'```\n(SELECT.*?)\n```',
            r'(SELECT.*?;)',
            r'Action Input:\s*"(SELECT.*?)"',
        ]
        
        for pattern in sql_patterns:
            match = re.search(pattern, agent_output, re.DOTALL | re.IGNORECASE)
            if match:
                sql = match.group(1).strip()
                # Clean up the SQL
                sql = sql.replace('\\n', '\n').replace('\\"', '"')
                return sql
        
        # If no pattern matched, try to find any SELECT statement
        if 'SELECT' in agent_output.upper():
            start = agent_output.upper().find('SELECT')
            end = agent_output.find(';', start)
            if end == -1:
                end = len(agent_output)
            return agent_output[start:end].strip()
        
        return "SQL query not found in agent output"
