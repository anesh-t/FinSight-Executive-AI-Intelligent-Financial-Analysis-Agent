import os
from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import create_engine, text
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseConnector:
    """
    Database connector for Supabase PostgreSQL.
    Handles connections and queries to financial data views.
    
    Schema:
    - Dimensions: dim_company, dim_financial_metric, dim_ratio, dim_stock_metric, 
                  dim_macro_indicator, dim_event
    - Facts: fact_financials, fact_ratios, fact_stock_prices, fact_macro_indicators
    - Views: vw_company_summary, vw_macro_overlay, vw_event_timeline, 
             vw_macro_long, vw_data_dictionary
    """
    
    def __init__(self):
        """Initialize Supabase connection."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.db_url = os.getenv('SUPABASE_DB_URL')
        
        # Initialize Supabase client
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize SQLAlchemy engine for direct SQL queries
        self.engine = create_engine(self.db_url)
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute raw SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame with query results
        """
        try:
            with self.engine.connect() as conn:
                result = pd.read_sql(text(query), conn)
            return result
        except Exception as e:
            print(f"Query execution error: {e}")
            return pd.DataFrame()
    
    def query_view(self, view_name: str, filter_query: str = None, limit: int = 1000) -> pd.DataFrame:
        """
        Query a specific view with optional filtering.
        
        Args:
            view_name: Name of the view (e.g., 'vw_company_summary')
            filter_query: Optional WHERE clause conditions
            limit: Maximum rows to return
            
        Returns:
            DataFrame with view data
        """
        query = f"SELECT * FROM {view_name}"
        if filter_query:
            query += f" WHERE {filter_query}"
        query += f" LIMIT {limit}"
        
        return self.execute_query(query)
    
    def get_company_data(
        self,
        company: str,
        start_year: int = None,
        start_quarter: int = None,
        end_year: int = None,
        end_quarter: int = None,
        view: str = 'vw_company_summary'
    ) -> pd.DataFrame:
        """
        Get comprehensive company data from specified view.
        
        Args:
            company: Company name (Apple, Microsoft, Amazon, Google, Meta)
            start_year: Starting fiscal year
            start_quarter: Starting fiscal quarter (1-4)
            end_year: Ending fiscal year
            end_quarter: Ending fiscal quarter (1-4)
            view: View name to query
            
        Returns:
            DataFrame with company data
        """
        # Build query with proper joins
        query = f"""
        SELECT v.* 
        FROM {view} v
        JOIN dim_company c ON v.company_id = c.company_id
        WHERE c.name = '{company}'
        """
        
        if start_year:
            query += f" AND v.fiscal_year >= {start_year}"
            if start_quarter:
                query += f" AND (v.fiscal_year > {start_year} OR v.fiscal_quarter >= {start_quarter})"
        
        if end_year:
            query += f" AND v.fiscal_year <= {end_year}"
            if end_quarter:
                query += f" AND (v.fiscal_year < {end_year} OR v.fiscal_quarter <= {end_quarter})"
        
        query += " ORDER BY v.fiscal_year, v.fiscal_quarter"
        
        return self.execute_query(query)
    
    def get_metric_definition(self, metric_name: str) -> Dict:
        """
        Get metric definition from vw_data_dictionary.
        
        Args:
            metric_name: Name or code of the metric
            
        Returns:
            Dictionary with metric metadata
        """
        query = f"""
        SELECT * FROM vw_data_dictionary 
        WHERE LOWER(name) LIKE LOWER('%{metric_name}%')
           OR LOWER(code) LIKE LOWER('%{metric_name}%')
        LIMIT 1
        """
        
        df = self.execute_query(query)
        if not df.empty:
            return df.iloc[0].to_dict()
        return {}
    
    def list_metrics(self, category: str = None) -> pd.DataFrame:
        """
        List all available metrics from vw_data_dictionary.
        
        Args:
            category: Optional category filter (Income Statement, Balance Sheet, etc.)
            
        Returns:
            DataFrame with metric information
        """
        query = "SELECT * FROM vw_data_dictionary"
        
        if category:
            query += f" WHERE category = '{category}'"
        
        query += " ORDER BY table_name, category, name"
        
        return self.execute_query(query)
    
    def get_companies(self) -> pd.DataFrame:
        """
        Get all companies from dim_company.
        
        Returns:
            DataFrame with company information
        """
        query = "SELECT * FROM dim_company ORDER BY name"
        return self.execute_query(query)
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = self.execute_query("SELECT 1 as test")
            return not result.empty
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
