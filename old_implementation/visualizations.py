import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
import numpy as np


class FinancialVisualizer:
    """
    Creates executive-style financial visualizations using Plotly.
    All charts are colorful, labeled, and ready for dashboard export.
    """
    
    def __init__(self, company_colors: Dict[str, str]):
        """
        Initialize visualizer with company color scheme.
        
        Args:
            company_colors: Dictionary mapping company names to hex colors
        """
        self.company_colors = company_colors
        self.default_layout = {
            'font': {'family': 'Inter, Arial, sans-serif', 'size': 14, 'color': '#1f2937'},
            'plot_bgcolor': '#f9fafb',
            'paper_bgcolor': '#ffffff',
            'hovermode': 'x unified',
            'hoverlabel': {'bgcolor': '#1f2937', 'font': {'size': 13, 'color': 'white'}},
            'margin': {'l': 60, 'r': 40, 't': 80, 'b': 60}
        }
    
    def create_comparison_chart(self, df: pd.DataFrame, title: str) -> go.Figure:
        """
        Create comparison bar chart for multiple companies.
        
        Args:
            df: DataFrame with company comparison data
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")
        
        # Detect company column
        company_col = self._find_column(df, ['company', 'company_name'])
        value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not company_col or not value_cols:
            return self._create_empty_chart("Invalid data structure")
        
        # Create grouped bar chart
        fig = go.Figure()
        
        for col in value_cols[:3]:  # Limit to 3 metrics for readability
            fig.add_trace(go.Bar(
                name=col.replace('_', ' ').title(),
                x=df[company_col],
                y=df[col],
                text=df[col].apply(lambda x: f'{x:,.0f}' if abs(x) > 1000 else f'{x:.2f}'),
                textposition='auto',
                marker_color=[self.company_colors.get(c, '#666666') for c in df[company_col]]
            ))
        
        fig.update_layout(
            title={'text': title, 'font': {'size': 20, 'color': '#111827', 'family': 'Inter, Arial, sans-serif'}, 'x': 0.5, 'xanchor': 'center'},
            xaxis_title='Company',
            yaxis_title='Value',
            barmode='group',
            xaxis={'gridcolor': '#e5e7eb', 'showgrid': False},
            yaxis={'gridcolor': '#e5e7eb', 'showgrid': True, 'zeroline': True},
            **self.default_layout
        )
        
        # Add smooth rounded corners effect
        fig.update_traces(marker_line_width=0, opacity=0.9)
        
        return fig
    
    def create_trend_chart(self, df: pd.DataFrame, title: str) -> go.Figure:
        """
        Create time-series trend chart.
        
        Args:
            df: DataFrame with time-series data
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")
        
        # Detect date and company columns
        date_col = self._find_column(df, ['date', 'quarter_date', 'quarter', 'period', 'fiscal_year'])
        company_col = self._find_column(df, ['company', 'company_name'])
        value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove fiscal_year and fiscal_quarter from value_cols if present
        value_cols = [col for col in value_cols if col not in ['fiscal_year', 'fiscal_quarter']]
        
        if not date_col or not value_cols:
            return self._create_empty_chart("Invalid data structure")
        
        fig = go.Figure()
        
        if company_col:
            # Multi-company trend
            for company in df[company_col].unique():
                company_data = df[df[company_col] == company]
                color = self.company_colors.get(company, '#666666')
                
                for col in value_cols[:2]:  # Limit metrics
                    fig.add_trace(go.Scatter(
                        name=f"{company} - {col.replace('_', ' ').title()}",
                        x=company_data[date_col],
                        y=company_data[col],
                        mode='lines+markers',
                        line=dict(color=color, width=3),
                        marker=dict(size=8)
                    ))
        else:
            # Single metric trend
            for col in value_cols[:3]:
                fig.add_trace(go.Scatter(
                    name=col.replace('_', ' ').title(),
                    x=df[date_col],
                    y=df[col],
                    mode='lines+markers',
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
        
        fig.update_layout(
            title={'text': title, 'font': {'size': 20, 'color': '#111827', 'family': 'Inter, Arial, sans-serif'}, 'x': 0.5, 'xanchor': 'center'},
            xaxis_title='Period',
            yaxis_title='Value',
            xaxis={'gridcolor': '#e5e7eb', 'showgrid': True},
            yaxis={'gridcolor': '#e5e7eb', 'showgrid': True, 'zeroline': True},
            legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1},
            **self.default_layout
        )
        
        # Add smooth line effect
        fig.update_traces(line_shape='spline', line_smoothing=1.3)
        
        return fig
    
    def create_ratio_chart(self, df: pd.DataFrame, title: str) -> go.Figure:
        """
        Create chart for financial ratios (typically percentages).
        
        Args:
            df: DataFrame with ratio data
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")
        
        date_col = self._find_column(df, ['date', 'quarter_date', 'quarter', 'fiscal_year'])
        company_col = self._find_column(df, ['company', 'company_name'])
        value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        value_cols = [col for col in value_cols if col not in ['fiscal_year', 'fiscal_quarter']]
        
        fig = go.Figure()
        
        if company_col and date_col:
            # Multi-company ratio comparison over time
            for company in df[company_col].unique():
                company_data = df[df[company_col] == company]
                color = self.company_colors.get(company, '#666666')
                
                fig.add_trace(go.Scatter(
                    name=company,
                    x=company_data[date_col],
                    y=company_data[value_cols[0]],
                    mode='lines+markers',
                    line=dict(color=color, width=3),
                    marker=dict(size=8),
                    hovertemplate='%{y:.2f}%<extra></extra>'
                ))
        
        fig.update_layout(
            title={'text': title, 'font': {'size': 20, 'color': '#111827', 'family': 'Inter, Arial, sans-serif'}, 'x': 0.5, 'xanchor': 'center'},
            xaxis_title='Period',
            yaxis_title='Ratio (%)',
            yaxis_ticksuffix='%',
            xaxis={'gridcolor': '#e5e7eb', 'showgrid': True},
            yaxis={'gridcolor': '#e5e7eb', 'showgrid': True, 'zeroline': True},
            legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1},
            **self.default_layout
        )
        
        # Add smooth line effect
        fig.update_traces(line_shape='spline', line_smoothing=1.3)
        
        return fig
    
    def create_smart_chart(self, df: pd.DataFrame, query: str) -> go.Figure:
        """
        Intelligently select chart type based on data structure.
        
        Args:
            df: DataFrame with data
            query: Original query for context
            
        Returns:
            Plotly Figure object
        """
        if df.empty:
            return self._create_empty_chart("No data available")
        
        # Analyze data structure
        date_col = self._find_column(df, ['date', 'quarter_date', 'quarter', 'period', 'fiscal_year'])
        company_col = self._find_column(df, ['company', 'company_name'])
        
        if date_col:
            # Time-series data
            return self.create_trend_chart(df, query)
        elif company_col:
            # Comparison data
            return self.create_comparison_chart(df, query)
        else:
            # Default to bar chart
            return self._create_simple_bar_chart(df, query)
    
    def _create_simple_bar_chart(self, df: pd.DataFrame, title: str) -> go.Figure:
        """Create simple bar chart as fallback."""
        fig = go.Figure()
        
        x_col = df.columns[0]
        y_col = df.select_dtypes(include=[np.number]).columns[0]
        
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            marker_color='#3b82f6',
            text=df[y_col].apply(lambda x: f'{x:,.0f}'),
            textposition='auto'
        ))
        
        fig.update_layout(
            title={'text': title, 'font': {'size': 18, 'color': '#1f2937'}},
            **self.default_layout
        )
        
        return fig
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message."""
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="#666666")
        )
        
        fig.update_layout(**self.default_layout)
        
        return fig
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column by possible names."""
        df_cols_lower = {col.lower(): col for col in df.columns}
        
        for name in possible_names:
            if name.lower() in df_cols_lower:
                return df_cols_lower[name.lower()]
        
        return None
