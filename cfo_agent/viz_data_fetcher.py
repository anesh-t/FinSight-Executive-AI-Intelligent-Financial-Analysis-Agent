"""
Visualization Data Fetcher
Fetches extended historical data for chart visualization
DOES NOT MODIFY ANY EXISTING FUNCTIONALITY - Completely isolated module
"""
import asyncpg
from typing import Dict, List, Optional, Any
import os


class VizDataFetcher:
    """
    Fetches historical data for visualization from the same views
    that the main agent uses for queries.
    
    This class is completely isolated and does not affect existing functionality.
    """
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    def should_visualize(self, intent: str, params: Dict[str, Any]) -> bool:
        """
        Determine if visualization is applicable for this query.
        
        Returns True if:
        - Query is for a single company (has ticker)
        - Query is for time-series data (revenue, margins, stock)
        - NOT for text-only queries (narratives, descriptions)
        """
        # Must have a ticker (single company queries only for now)
        if 'ticker' not in params or not params['ticker']:
            return False
        
        # Intents that make sense for visualization
        viz_intents = [
            'annual_metrics',
            'quarter_snapshot',
            'stock_price_annual',
            'stock_price_quarterly',
            'complete_annual',
            'complete_quarterly',
            'complete_macro_context_annual',
            'complete_macro_context_quarterly',
            'growth_annual_cagr',
            'growth_qoq_yoy'
        ]
        
        return any(vi in intent for vi in viz_intents)
    
    def get_chart_type(self, intent: str, params: Dict[str, Any]) -> str:
        """
        Determine the best chart type based on intent.
        """
        if 'stock' in intent.lower():
            # Stock queries
            if 'quarter' in intent:
                return 'ohlc'  # Candlestick for quarterly stock
            return 'line_stock'  # Line chart for annual stock
        
        elif 'growth' in intent.lower():
            return 'bar_growth'  # Bar chart for growth rates
        
        elif 'complete' in intent.lower():
            return 'combo'  # Dual-axis for combined queries
        
        else:
            # Default: simple line chart for time series
            return 'line'
    
    async def fetch_viz_data(self, intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch extended historical data for visualization.
        Uses the SAME views as the main agent queries.
        
        Args:
            intent: The query intent (e.g., 'annual_metrics', 'quarter_snapshot')
            params: Query parameters including ticker, fiscal_year, fiscal_quarter
        
        Returns:
            Dictionary with chart data and metadata
        """
        ticker = params.get('ticker')
        fy = params.get('fy')
        fq = params.get('fq')
        
        print(f"[VIZ] Fetching data for intent={intent}, ticker={ticker}, fy={fy}, fq={fq}")
        
        # ALWAYS use quarterly data for smooth, professional charts (20+ data points)
        # This creates detailed curves like in professional financial dashboards
        # Quarterly data shows business cycles and trends much better than annual
        data = await self._fetch_quarterly_trend(ticker, fy, fq)
        period = 'quarterly'
        
        chart_type = self.get_chart_type(intent, params)
        
        return {
            'type': chart_type,
            'period': period,
            'data': data,
            'ticker': ticker,
            'target_year': fy,
            'target_quarter': fq
        }
    
    async def _fetch_annual_trend(self, ticker: str, target_year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch 5-year annual trend data.
        Uses mv_company_complete_annual view - same as agent uses!
        """
        # Calculate year range
        if target_year:
            start_year = target_year - 4
            end_year = target_year
        else:
            # Default to last 5 years
            start_year = 2019
            end_year = 2023
        
        sql = """
        SELECT 
            fiscal_year,
            -- Financials
            revenue_annual/1e9 as revenue_b,
            net_income_annual/1e9 as net_income_b,
            operating_income_annual/1e9 as op_income_b,
            gross_profit_annual/1e9 as gross_profit_b,
            -- Ratios
            gross_margin_annual*100 as gross_margin_pct,
            operating_margin_annual*100 as operating_margin_pct,
            net_margin_annual*100 as net_margin_pct,
            roe_annual*100 as roe_pct,
            roa_annual*100 as roa_pct,
            -- Stock
            close_price_eoy as stock_price,
            avg_price_annual,
            high_price_annual,
            low_price_annual,
            return_annual*100 as return_pct
        FROM mv_company_complete_annual
        WHERE ticker = $1
          AND fiscal_year BETWEEN $2 AND $3
        ORDER BY fiscal_year ASC
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(sql, ticker, start_year, end_year)
            result = [dict(row) for row in rows]
            print(f"[VIZ] Fetched {len(result)} annual records for {ticker} ({start_year}-{end_year})")
            return result
    
    async def _fetch_quarterly_trend(self, ticker: str, target_year: Optional[int] = None, 
                                     target_quarter: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch 8-quarter trend data.
        Uses vw_company_complete_quarter view - same as agent uses!
        """
        sql = """
        SELECT 
            fiscal_year,
            fiscal_quarter,
            -- Financials
            revenue/1e9 as revenue_b,
            net_income/1e9 as net_income_b,
            operating_income/1e9 as op_income_b,
            gross_profit/1e9 as gross_profit_b,
            -- Ratios
            gross_margin*100 as gross_margin_pct,
            operating_margin*100 as operating_margin_pct,
            net_margin*100 as net_margin_pct,
            roe*100 as roe_pct,
            roa*100 as roa_pct,
            -- Stock (OHLC for candlestick)
            open_price,
            close_price,
            high_price,
            low_price,
            avg_price,
            return_qoq*100 as return_qoq_pct,
            return_yoy*100 as return_yoy_pct
        FROM vw_company_complete_quarter
        WHERE ticker = $1
        ORDER BY fiscal_year DESC, fiscal_quarter DESC
        LIMIT 20
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(sql, ticker)
            # Reverse to get chronological order
            result = [dict(row) for row in rows][::-1]
            print(f"[VIZ] Fetched {len(result)} quarterly records for {ticker}")
            return result
    
    def generate_chart_config(self, viz_data: Dict[str, Any], metric_name: str = None, all_metrics: list = None) -> Dict[str, Any]:
        """
        Generate chart configuration based on data and type.
        
        Args:
            viz_data: The visualization data from fetch_viz_data()
            metric_name: Optional specific metric to highlight (e.g., 'revenue_b')
            all_metrics: List of (field_name, label) tuples for combo charts
        
        Returns:
            Chart configuration for frontend
        """
        chart_type = viz_data['type']
        period = viz_data['period']
        ticker = viz_data['ticker']
        data = viz_data['data']
        
        if not data:
            return {'error': 'No data available for visualization'}
        
        # If multiple metrics detected, use combo chart
        if all_metrics and len(all_metrics) >= 2:
            return self._generate_combo_config(data, ticker, period, all_metrics)
        
        # Generate config based on chart type
        if chart_type == 'line':
            return self._generate_line_config(data, ticker, period, metric_name)
        elif chart_type == 'ohlc':
            return self._generate_ohlc_config(data, ticker)
        elif chart_type == 'combo':
            return self._generate_combo_config(data, ticker, period, all_metrics or [])
        elif chart_type == 'bar_growth':
            return self._generate_growth_config(data, ticker)
        else:
            return self._generate_line_config(data, ticker, period, metric_name)
    
    def _generate_line_config(self, data: List[Dict], ticker: str, period: str, 
                             metric_name: str = None) -> Dict[str, Any]:
        """Generate config for line chart"""
        # Default to revenue if no metric specified
        if not metric_name:
            metric_name = 'revenue_b'
        
        # Map metric names to actual DB fields (handle both annual and quarterly)
        metric_field_map = {
            'stock_price': ['stock_price', 'close_price'],  # Annual uses 'stock_price', Quarterly uses 'close_price'
            'closing_price': ['close_price', 'stock_price'],
            'close_price': ['close_price', 'stock_price'],
            'opening_price': ['open_price'],
            'open_price': ['open_price'],
            'high_price': ['high_price'],
            'low_price': ['low_price']
        }
        
        # Generate x-axis labels
        if period == 'annual':
            x_labels = [str(d['fiscal_year']) for d in data]
        else:
            x_labels = [f"Q{d['fiscal_quarter']} {d['fiscal_year']}" for d in data]
        
        # Get y values - try multiple field names
        field_names = metric_field_map.get(metric_name, [metric_name])
        if not isinstance(field_names, list):
            field_names = [field_names]
        
        y_values = []
        for d in data:
            value = None
            for field in field_names:
                value = d.get(field)
                if value is not None and value != 0:
                    break
            y_values.append(value if value is not None else 0)
        
        # Determine metric label
        metric_labels = {
            'revenue_b': 'Revenue ($B)',
            'net_income_b': 'Net Income ($B)',
            'gross_margin_pct': 'Gross Margin (%)',
            'net_margin_pct': 'Net Margin (%)',
            'roe_pct': 'ROE (%)',
            'stock_price': 'Stock Price ($)',
            'close_price': 'Stock Price ($)',
            'closing_price': 'Closing Price ($)',
            'open_price': 'Opening Price ($)',
            'high_price': 'High Price ($)',
            'low_price': 'Low Price ($)'
        }
        # Try to get label from metric_name or first field name in the list
        y_label = metric_labels.get(metric_name)
        if not y_label and field_names:
            y_label = metric_labels.get(field_names[0], metric_name)
        if not y_label:
            y_label = metric_name
        
        return {
            'title': f'{ticker} - {y_label} Trend',
            'x_labels': x_labels,
            'y_values': y_values,
            'y_label': y_label,
            'show_trend': True
        }
    
    def _generate_ohlc_config(self, data: List[Dict], ticker: str) -> Dict[str, Any]:
        """Generate config for OHLC/Candlestick chart"""
        x_labels = [f"Q{d['fiscal_quarter']} {d['fiscal_year']}" for d in data]
        
        return {
            'title': f'{ticker} Stock Price Movement',
            'x_labels': x_labels,
            'open': [d.get('open_price', 0) for d in data],
            'high': [d.get('high_price', 0) for d in data],
            'low': [d.get('low_price', 0) for d in data],
            'close': [d.get('close_price', 0) for d in data]
        }
    
    def _generate_combo_config(self, data: List[Dict], ticker: str, period: str, metrics: list = None) -> Dict[str, Any]:
        """Generate config for combo/dual-axis chart with detected metrics"""
        if period == 'annual':
            x_labels = [str(d['fiscal_year']) for d in data]
        else:
            x_labels = [f"Q{d['fiscal_quarter']} {d['fiscal_year']}" for d in data]
        
        # Use detected metrics or fallback to defaults
        if metrics and len(metrics) >= 2:
            metric1_field, metric1_label = metrics[0]
            metric2_field, metric2_label = metrics[1]
        else:
            metric1_field, metric1_label = 'revenue_b', 'Revenue ($B)'
            metric2_field, metric2_label = 'net_margin_pct', 'Net Margin (%)'
        
        # Handle stock price field aliases (same as line chart)
        field_map = {
            'stock_price': ['stock_price', 'close_price'],
            'close_price': ['close_price', 'stock_price'],
            'closing_price': ['close_price', 'stock_price']
        }
        
        # Get y1 values
        y1_fields = field_map.get(metric1_field, [metric1_field])
        y1_values = []
        for d in data:
            val = None
            for field in y1_fields:
                val = d.get(field)
                if val is not None and val != 0:
                    break
            y1_values.append(val if val is not None else 0)
        
        # Get y2 values
        y2_fields = field_map.get(metric2_field, [metric2_field])
        y2_values = []
        for d in data:
            val = None
            for field in y2_fields:
                val = d.get(field)
                if val is not None and val != 0:
                    break
            y2_values.append(val if val is not None else 0)
        
        return {
            'title': f'{ticker} - {metric1_label.split(" (")[0]} & {metric2_label.split(" (")[0]}',
            'x_labels': x_labels,
            'y1_values': y1_values,
            'y1_label': metric1_label,
            'y2_values': y2_values,
            'y2_label': metric2_label
        }
    
    def _generate_growth_config(self, data: List[Dict], ticker: str) -> Dict[str, Any]:
        """Generate config for growth bar chart"""
        x_labels = [str(d['fiscal_year']) for d in data[1:]]  # Skip first year (no prior comparison)
        
        # Calculate YoY growth
        growth_values = []
        for i in range(1, len(data)):
            prev = data[i-1].get('revenue_b', 0)
            curr = data[i].get('revenue_b', 0)
            if prev > 0:
                growth = ((curr - prev) / prev) * 100
                growth_values.append(growth)
            else:
                growth_values.append(0)
        
        return {
            'title': f'{ticker} - Revenue Growth (YoY %)',
            'x_labels': x_labels,
            'y_values': growth_values,
            'y_label': 'Growth (%)',
            'is_percentage': True
        }
