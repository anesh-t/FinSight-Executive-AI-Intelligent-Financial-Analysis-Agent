import os
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from sqlalchemy import create_engine

from visualizations import FinancialVisualizer
from database import SupabaseConnector

# Load environment variables
load_dotenv()


class CFOAssistant:
    """
    LangChain-based CFO Assistant Agent for financial analysis.
    Uses GPT-3.5-Turbo to query Supabase PostgreSQL database and generate insights.
    
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
            model: OpenAI model name (default: from env or gpt-3.5-turbo)
            temperature: LLM temperature (default: 0.0 for consistency)
            verbose: Enable verbose logging
        """
        self.model = model or os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
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
        
        # Enhanced system prompt with actual schema details
        self.system_context = """
        You are an expert CFO Assistant. Query the database to answer financial questions.
        
        PRIMARY VIEW - vw_company_summary (USE THIS FOR MOST QUERIES):
        Columns: company_id, company_name, ticker, fiscal_year, fiscal_quarter,
        revenue, operating_income, net_income, eps, total_assets, total_liabilities, equity,
        roe, roa, gross_margin, operating_margin, net_margin, debt_to_equity,
        close_price, return_qoq, return_yoy, volatility_pct
        
        MACRO VIEW - vw_macro_overlay (for economic context):
        All company_summary columns PLUS: gdp_growth, cpi, unemployment_rate, fed_funds_rate, sp500_return, vix
        
        EVENT VIEW - vw_event_timeline (for event analysis):
        All company_summary columns PLUS: event_name, event_start_date, event_end_date, event_category
        
        CRITICAL RULES:
        1. ALWAYS use company_name (not company) in WHERE clauses
        2. ALWAYS filter by fiscal_year and/or fiscal_quarter for time periods
        3. Company names (EXACT): 'Apple Inc.', 'Microsoft Corporation', 'Amazon.com Inc.', 'Alphabet Inc.', 'Meta Platforms Inc.'
        4. Use LIKE for partial matching: company_name LIKE '%Apple%' OR company_name LIKE '%Microsoft%'
        5. For comparisons: SELECT company_name, metric1, metric2 WHERE company_name LIKE '%Apple%'
        6. For trends: ORDER BY fiscal_year, fiscal_quarter
        7. For growth: Use LAG() window function or calculate (new-old)/old*100
        
        EXAMPLE QUERIES:
        - "Apple revenue 2023": SELECT company_name, fiscal_year, fiscal_quarter, revenue FROM vw_company_summary WHERE company_name LIKE '%Apple%' AND fiscal_year=2023
        - "Compare revenues": SELECT company_name, SUM(revenue) as total FROM vw_company_summary WHERE company_name LIKE '%Apple%' OR company_name LIKE '%Microsoft%' GROUP BY company_name
        - "Revenue trend": SELECT fiscal_year, fiscal_quarter, revenue FROM vw_company_summary WHERE company_name LIKE '%Apple%' ORDER BY fiscal_year, fiscal_quarter
        """
    
    def analyze(self, query: str) -> Dict:
        """
        Main analysis method: understand query, execute SQL, visualize, and narrate.
        
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
            # Step 1: Execute agent query with concise context
            full_query = f"{self.system_context}\n\nQuestion: {query}"
            
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
            
            # Step 3: Generate executive narrative
            narrative = self._generate_narrative(query, df, agent_output)
            
            # Step 4: Create executive summary with actual data
            summary = self._create_executive_summary(query, df)
            
            return {
                'status': 'success',
                'summary': summary,
                'data': df,
                'visualization': None,
                'narrative': narrative,
                'agent_response': agent_output,
                'sql_query': sql_query if sql_query else "Query executed via fallback",
                'query': query
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
        
        # Detect company names
        companies = []
        for company in ['Apple', 'Microsoft', 'Amazon', 'Google', 'Meta']:
            if company.lower() in query_lower:
                companies.append(company)
        
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
        Generate CFO-style narrative interpretation of results.
        """
        if df is None or df.empty:
            return "Insufficient data available for analysis."
        
        # Use LLM to generate executive narrative - shortened prompt
        narrative_prompt = f"""
        Query: {query}
        
        Data sample:
        {df.head(5).to_string() if len(df) > 0 else 'No data'}
        
        Provide 3-5 sentence CFO narrative with key findings, trends, and specific numbers.
        """
        
        response = self.llm.invoke(narrative_prompt)
        return response.content
    
    def _create_executive_summary(self, query: str, df: pd.DataFrame) -> str:
        """
        Create brief executive summary (1-3 sentences).
        """
        if df is None or df.empty:
            return "No data available for the requested analysis."
        
        summary_prompt = f"""
        Query: {query}
        Records: {len(df)}
        
        Write 1-2 sentence summary with key metrics.
        """
        
        response = self.llm.invoke(summary_prompt)
        return response.content
    
    def get_metric_info(self, metric_name: str) -> Dict:
        """
        Query vw_data_dictionary for metric definitions.
        """
        return self.db_connector.get_metric_definition(metric_name)
    
    def list_available_metrics(self, category: str = None) -> pd.DataFrame:
        """
        List all available metrics from vw_data_dictionary.
        """
        return self.db_connector.list_metrics(category)
    
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
