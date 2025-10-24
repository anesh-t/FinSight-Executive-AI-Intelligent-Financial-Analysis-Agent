"""
Streamlit Chart Renderer
Renders Plotly charts for financial data visualization
Completely isolated - does not affect existing Streamlit functionality
"""
# VERSION: 2025-10-22-23:15 - Force reload to pick up Y-axis fixes
import plotly.graph_objects as go
import streamlit as st
import numpy as np
from typing import Dict, List, Any

print("[CHART RENDERER] Module loaded - Version 2025-10-22-23:15")


class ChartRenderer:
    """
    {{ ... }}
    Renders various chart types for financial data visualization.
    Uses Plotly for interactive, professional charts.
    """
    
    # Color scheme for dark theme
    COLORS = {
        'primary': '#4a9eff',
        'secondary': '#7b68ee',
        'success': '#26a69a',
        'danger': '#ef5350',
        'warning': '#ffa726',
        'accent': '#ff6b9d'
    }
    
    def __init__(self):
        """Initialize chart renderer"""
        pass
    
    def render(self, chart_type: str, chart_config: Dict[str, Any], chart_data: Dict[str, Any]):
        """
        Main rendering method - routes to specific chart type
        
        Args:
            chart_type: Type of chart ('line', 'ohlc', 'combo', 'comparison', 'bar_growth')
            chart_config: Chart configuration (title, labels, etc.)
            chart_data: Raw data for the chart
        """
        if chart_type == 'line' or chart_type == 'line_stock':
            self.render_line_chart(chart_config, chart_data)
        elif chart_type == 'ohlc':
            self.render_ohlc_chart(chart_config, chart_data)
        elif chart_type == 'combo':
            self.render_combo_chart(chart_config, chart_data)
        elif chart_type == 'comparison':
            self.render_comparison_chart(chart_config, chart_data)
        elif chart_type == 'bar_growth':
            self.render_bar_chart(chart_config, chart_data)
        else:
            # Default to line chart
            self.render_line_chart(chart_config, chart_data)
    
    def render_line_chart(self, config: Dict[str, Any], data: Dict[str, Any]):
        """
        Render clean line chart with proper Y-axis scaling
        COMPLETELY REWRITTEN for accuracy and clarity
        """
        import math
        
        # Extract data
        x_labels = config['x_labels']
        y_values = [float(y) if y is not None else 0 for y in config['y_values']]
        y_label = config['y_label']
        title = config['title']
        
        # Check if all values are 0 (data issue)
        if all(y == 0 for y in y_values):
            st.warning("⚠️ No data available for this metric. All values are 0.")
            return
        
        # Calculate Y-axis range
        y_min = min(y_values)
        y_max = max(y_values)
        
        # Determine tick interval based on data range
        if y_max > 500:
            tick_interval = 100
        elif y_max > 200:
            tick_interval = 50
        elif y_max > 100:
            tick_interval = 20
        else:
            tick_interval = 10
        
        # Calculate clean min/max
        y_axis_min = 0
        y_axis_max = math.ceil(y_max * 1.25 / tick_interval) * tick_interval
        
        # Ensure at least 2 ticks above max value
        if y_axis_max < (y_max + 2 * tick_interval):
            y_axis_max = math.ceil((y_max + 2 * tick_interval) / tick_interval) * tick_interval
        
        # Create figure from scratch (NO template!)
        fig = go.Figure()
        
        # Add line trace
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=y_values,
            mode='lines+markers+text',
            line=dict(color='#26a69a', width=2.5),
            marker=dict(color='#ffa726', size=8, line=dict(color='white', width=1.5)),
            text=[f"{y:.1f}" for y in y_values],
            textposition='top center',
            textfont=dict(size=10, color='#ffa726'),
            name=y_label
        ))
        
        # Apply layout - MINIMAL, NO TEMPLATE
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20, color='white')),
            xaxis=dict(
                title='Period',
                gridcolor='rgba(255,255,255,0.2)',
                showgrid=True,
                color='white'
            ),
            yaxis=dict(
                title=y_label,
                range=[y_axis_min, y_axis_max],
                dtick=tick_interval,
                tickmode='linear',
                tick0=0,
                tickformat=',.0f',
                gridcolor='rgba(255,255,255,0.2)',
                showgrid=True,
                color='white'
            ),
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#0f1419',
            font=dict(color='white', size=12),
            height=500,
            showlegend=False
        )
        
        # Display debug info and chart
        st.write(f"**✅ Y-axis: {y_axis_min} to {y_axis_max}, interval: {tick_interval}**")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insights
        self._add_insights(config, data)
    
    def render_ohlc_chart(self, config: Dict[str, Any], data: Dict[str, Any]):
        """
        Render clean OHLC/Candlestick chart for stock prices
        REWRITTEN for clarity - same approach as other charts
        """
        import math
        
        # Extract data
        x_labels = config['x_labels']
        open_prices = config['open']
        high_prices = config['high']
        low_prices = config['low']
        close_prices = config['close']
        title = config['title']
        
        # Calculate Y-axis range (filter out None values)
        all_prices = [p for p in (open_prices + high_prices + low_prices + close_prices) if p is not None and p != '']
        
        if not all_prices:
            st.error("No valid stock price data available")
            return
        
        all_prices = [float(p) for p in all_prices]
        price_min = min(all_prices)
        price_max = max(all_prices)
        
        # Determine tick interval
        if price_max > 500:
            tick_interval = 100
        elif price_max > 200:
            tick_interval = 50
        elif price_max > 100:
            tick_interval = 20
        else:
            tick_interval = 10
        
        # Calculate clean min/max with padding
        y_axis_min = math.floor(price_min * 0.95 / tick_interval) * tick_interval
        y_axis_max = math.ceil(price_max * 1.05 / tick_interval) * tick_interval
        
        # Create figure
        fig = go.Figure(data=[go.Candlestick(
            x=x_labels,
            open=open_prices,
            high=high_prices,
            low=low_prices,
            close=close_prices,
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350',
            name='Stock Price'
        )])
        
        # Update layout
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20, color='white')),
            xaxis=dict(
                title='Period',
                gridcolor='rgba(255,255,255,0.2)',
                showgrid=True,
                rangeslider=dict(visible=False),
                color='white'
            ),
            yaxis=dict(
                title='Stock Price ($)',
                range=[y_axis_min, y_axis_max],
                dtick=tick_interval,
                tickmode='linear',
                tickformat=',.0f',
                gridcolor='rgba(255,255,255,0.2)',
                showgrid=True,
                color='white'
            ),
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#0f1419',
            font=dict(color='white', size=12),
            height=500
        )
        
        st.write(f"**✅ Stock Price Range: ${y_axis_min:.0f} to ${y_axis_max:.0f}, interval: ${tick_interval}**")
        st.plotly_chart(fig, use_container_width=True)
    
    def render_combo_chart(self, config: Dict[str, Any], data: Dict[str, Any]):
        """
        Render clean dual-axis combo chart
        REWRITTEN for clarity - same approach as line charts
        """
        import math
        
        # Extract data
        x_labels = config['x_labels']
        y1_values = [float(y) for y in config['y1_values']]
        y2_values = [float(y) for y in config['y2_values']]
        y1_label = config['y1_label']
        y2_label = config['y2_label']
        title = config['title']
        
        # Calculate Y1 axis (primary - usually revenue)
        y1_max = max(y1_values)
        if y1_max > 500:
            y1_tick = 100
        elif y1_max > 200:
            y1_tick = 50
        elif y1_max > 100:
            y1_tick = 20
        else:
            y1_tick = 10
        
        y1_axis_min = 0
        y1_axis_max = math.ceil(y1_max * 1.25 / y1_tick) * y1_tick
        if y1_axis_max < (y1_max + 2 * y1_tick):
            y1_axis_max = math.ceil((y1_max + 2 * y1_tick) / y1_tick) * y1_tick
        
        # Calculate Y2 axis (secondary - percentage or stock price)
        y2_max = max(y2_values)
        is_y2_pct = '%' in y2_label or 'pct' in y2_label.lower() or 'margin' in y2_label.lower()
        
        if is_y2_pct:
            y2_tick = 5
            y2_axis_min = 0
            y2_axis_max = math.ceil(y2_max * 1.2 / y2_tick) * y2_tick
        else:
            if y2_max > 500:
                y2_tick = 100
            elif y2_max > 200:
                y2_tick = 50
            elif y2_max > 100:
                y2_tick = 20
            else:
                y2_tick = 10
            y2_axis_min = 0
            y2_axis_max = math.ceil(y2_max * 1.25 / y2_tick) * y2_tick
        
        # Create figure
        fig = go.Figure()
        
        # Debug output
        print(f"[COMBO CHART] Y1 (bars): {y1_label} = {y1_values[:3]}... (max={y1_max})")
        print(f"[COMBO CHART] Y2 (line): {y2_label} = {y2_values[:3]}... (max={y2_max})")
        
        # Add bar trace (Y1 - primary axis) - RENDER FIRST SO VISIBLE
        # Use wider bars for annual data (fewer points)
        bar_width = 0.6 if len(x_labels) <= 10 else None
        
        fig.add_trace(go.Bar(
            x=x_labels,
            y=y1_values,
            name=y1_label,
            marker=dict(color='#4a9eff', opacity=0.8),
            text=[f"{y:.1f}" for y in y1_values],
            textposition='outside',
            textfont=dict(size=9, color='#4a9eff'),
            width=bar_width,
            yaxis='y'
        ))
        
        # Add line trace (Y2 - secondary axis) - RENDER SECOND (ON TOP)
        fig.add_trace(go.Scatter(
            x=x_labels,
            y=y2_values,
            name=y2_label,
            mode='lines+markers+text',
            line=dict(color='#ffa726', width=2.5),
            marker=dict(color='#ffa726', size=7, line=dict(color='white', width=1.5)),
            text=[f"{y:.1f}" for y in y2_values],
            textposition='top center',
            textfont=dict(size=9, color='#ffa726'),
            yaxis='y2'
        ))
        
        # Update layout
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20, color='white')),
            xaxis=dict(
                title='Period',
                gridcolor='rgba(255,255,255,0.2)',
                showgrid=True,
                color='white'
            ),
            yaxis=dict(
                title=y1_label,
                range=[y1_axis_min, y1_axis_max],
                dtick=y1_tick,
                tickmode='linear',
                tick0=0,
                tickformat=',.0f',
                gridcolor='rgba(255,255,255,0.2)',
                showgrid=True,
                color='#4a9eff'
            ),
            yaxis2=dict(
                title=y2_label,
                range=[y2_axis_min, y2_axis_max],
                dtick=y2_tick,
                tickmode='linear',
                tick0=0,
                tickformat=',.1f' if is_y2_pct else ',.0f',
                overlaying='y',
                side='right',
                showgrid=False,
                color='#ffa726'
            ),
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#0f1419',
            font=dict(color='white', size=12),
            height=500,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.write(f"**✅ Y1-axis: {y1_axis_min} to {y1_axis_max} ({y1_tick}) | Y2-axis: {y2_axis_min} to {y2_axis_max} ({y2_tick})**")
        st.plotly_chart(fig, use_container_width=True)
        
        # Add insights
        self._add_insights(config, data)
    
    def render_comparison_chart(self, config: Dict[str, Any], data: Dict[str, Any]):
        """
        Render grouped bar chart for company comparisons
        NEW - handles multi-company queries
        """
        import math
        
        # Extract data
        companies = config['companies']  # ['AAPL', 'GOOG']
        company_names = config['company_names']  # ['Apple Inc.', 'Alphabet Inc.']
        metrics = config['metrics']  # ['revenue', 'net_income']
        metric_labels = config['metric_labels']  # ['Revenue ($B)', 'Net Income ($B)']
        title = config['title']
        
        # Create figure
        fig = go.Figure()
        
        # Add bar for each metric
        colors = ['#4a9eff', '#ffa726', '#26a69a', '#ef5350']
        for idx, metric in enumerate(metrics):
            values = [config['data'][company][metric] for company in companies]
            
            fig.add_trace(go.Bar(
                name=metric_labels[idx],
                x=company_names,
                y=values,
                text=[f"{v:.1f}" for v in values],
                textposition='outside',
                marker_color=colors[idx % len(colors)]
            ))
        
        # Calculate Y-axis
        all_values = [config['data'][company][metric] for company in companies for metric in metrics]
        y_max = max(all_values)
        
        if y_max > 500:
            y_tick = 100
        elif y_max > 200:
            y_tick = 50
        elif y_max > 100:
            y_tick = 20
        else:
            y_tick = 10
        
        y_axis_max = math.ceil(y_max * 1.25 / y_tick) * y_tick
        
        # Update layout
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(size=20, color='white')),
            xaxis=dict(
                title='Company',
                color='white'
            ),
            yaxis=dict(
                title='Value',
                range=[0, y_axis_max],
                dtick=y_tick,
                tickmode='linear',
                tick0=0,
                tickformat=',.0f',
                gridcolor='rgba(255,255,255,0.2)',
                showgrid=True,
                color='white'
            ),
            barmode='group',
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#0f1419',
            font=dict(color='white', size=12),
            height=500,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.write(f"**✅ Comparing {len(companies)} companies across {len(metrics)} metric(s)**")
        st.plotly_chart(fig, use_container_width=True)
    
    def render_combo_chart_OLD(self, config: Dict[str, Any], data: Dict[str, Any]):
        # OLD COMPLEX VERSION - KEPT FOR REFERENCE
        y2_vals = [float(y) for y in config['y2_values']]
        y2_min = min(y2_vals)
        y2_max = max(y2_vals)
        is_y2_percentage = '%' in config['y2_label'] or 'pct' in config['y2_label'].lower()
        
        if is_y2_percentage:
            # Fixed 5% intervals for percentages
            y2_axis_min = (y2_min // 5) * 5
            y2_axis_max = ((y2_max // 5) + 2) * 5
            
            # Ensure minimum range
            if (y2_axis_max - y2_axis_min) < 15:
                center = (y2_axis_min + y2_axis_max) / 2
                y2_axis_min = max(0, (center - 10) // 5 * 5)
                y2_axis_max = min(100, ((center + 10) // 5 + 1) * 5)
            
            y2_tick_interval = 5
        else:
            y2_axis_min = 0
            y2_axis_max = ((y2_max // round_to_1) + 2) * round_to_1
            y2_tick_interval = round_to_1
        
        # Update layout with dual axes
        fig.update_layout(
            title={
                'text': config['title'],
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#e8eaed'}
            },
            xaxis_title='Period',
            yaxis=dict(
                title=config['y1_label'],
                titlefont=dict(color=self.COLORS['primary']),
                tickfont=dict(color=self.COLORS['primary']),
                gridcolor='rgba(255,255,255,0.1)',
                range=[y1_axis_min, y1_axis_max],
                dtick=y1_tick_interval,
                tickmode='linear',
                tick0=0,
                tickformat=',.0f',
                separatethousands=True
            ),
            yaxis2=dict(
                title=config['y2_label'],
                titlefont=dict(color=self.COLORS['secondary']),
                tickfont=dict(color=self.COLORS['secondary']),
                anchor='x',
                overlaying='y',
                side='right',
                range=[y2_axis_min, y2_axis_max],
                dtick=y2_tick_interval,
                tickmode='linear',
                tick0=0,
                tickformat=',.0f',
                separatethousands=True
            ),
            template='plotly_dark',
            hovermode='x unified',
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#e8eaed', 'size': 12},
            legend={
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': 1.02,
                'xanchor': 'right',
                'x': 1
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_bar_chart(self, config: Dict[str, Any], data: Dict[str, Any]):
        """
        Render bar chart for growth/comparison data
        
        Args:
            config: Chart configuration
            data: Chart data
        """
        # Color bars based on positive/negative
        colors = [self.COLORS['success'] if v >= 0 else self.COLORS['danger'] 
                 for v in config['y_values']]
        
        fig = go.Figure(data=[go.Bar(
            x=config['x_labels'],
            y=config['y_values'],
            marker_color=colors,
            text=[f"{v:.1f}%" for v in config['y_values']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Growth: %{y:.2f}%<extra></extra>'
        )])
        
        # Smart Y-axis range for growth (can be negative) with FIXED INTERVALS
        import math
        
        y_vals = config['y_values']
        y_min = min(y_vals)
        y_max = max(y_vals)
        
        # Determine appropriate interval for growth percentages
        y_abs_max = max(abs(y_min), abs(y_max))
        
        if y_abs_max > 100:
            tick_interval = 20   # Very large growth: 20% intervals
        elif y_abs_max > 50:
            tick_interval = 10   # Large growth: 10% intervals  
        elif y_abs_max > 20:
            tick_interval = 5    # Medium growth: 5% intervals
        elif y_abs_max > 10:
            tick_interval = 2    # Small-medium growth: 2% intervals
        else:
            tick_interval = 1    # Small growth: 1% intervals
        
        # For growth charts, use symmetric or asymmetric based on data
        if y_min >= 0:  # All positive growth
            y_axis_min = 0
            y_axis_max = math.ceil(y_max / tick_interval) * tick_interval
            # Add headroom
            if y_axis_max < y_max + (2 * tick_interval):
                y_axis_max = y_axis_max + (2 * tick_interval)
        elif y_max <= 0:  # All negative growth
            y_axis_max = 0
            y_axis_min = math.floor(y_min / tick_interval) * tick_interval
            # Add headroom
            if y_axis_min > y_min - (2 * tick_interval):
                y_axis_min = y_axis_min - (2 * tick_interval)
        else:  # Mixed positive and negative - make symmetric
            y_symmetric = math.ceil(y_abs_max / tick_interval) * tick_interval
            # Add at least 1 interval of headroom
            y_symmetric = y_symmetric + tick_interval
            y_axis_min = -y_symmetric
            y_axis_max = y_symmetric
        
        fig.update_layout(
            title={
                'text': config['title'],
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#e8eaed'}
            },
            xaxis_title='Period',
            yaxis_title=config['y_label'],
            template='plotly_dark',
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#e8eaed', 'size': 12},
            xaxis={'gridcolor': 'rgba(255,255,255,0.1)'},
            yaxis={
                'gridcolor': 'rgba(255,255,255,0.1)', 
                'zeroline': True, 
                'zerolinecolor': 'white',
                'range': [y_axis_min, y_axis_max],
                'dtick': tick_interval,
                'tickmode': 'linear',
                'tick0': 0,
                'tickformat': ',.0f',
                'separatethousands': True
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _add_insights(self, config: Dict[str, Any], data: Dict[str, Any]):
        """Add textual insights below the chart"""
        # Handle both line charts (y_values) and combo charts (y1_values)
        y_values = config.get('y_values') or config.get('y1_values')
        y_label = config.get('y_label') or config.get('y1_label') or 'Metric'
        
        if not y_values:
            return
        
        if len(y_values) < 2:
            return
        
        # Calculate metrics
        first_val = float(y_values[0])
        last_val = float(y_values[-1])
        
        if first_val > 0:
            total_change = ((last_val - first_val) / first_val) * 100
            cagr = (((last_val / first_val) ** (1 / (len(y_values) - 1))) - 1) * 100
            
            # Determine trend
            if total_change > 5:
                trend = "📈 Strong Growth"
                trend_color = "green"
            elif total_change > 0:
                trend = "📊 Moderate Growth"
                trend_color = "blue"
            elif total_change > -5:
                trend = "📉 Slight Decline"
                trend_color = "orange"
            else:
                trend = "⚠️ Significant Decline"
                trend_color = "red"
            
            # Display insights
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Period Change",
                    value=f"{total_change:+.1f}%",
                    delta=f"{last_val:.2f}" if 'B' in y_label or '$' in y_label else f"{last_val:.1f}%"
                )
            
            with col2:
                st.metric(
                    label=f"{len(y_values)-1}Y CAGR",
                    value=f"{cagr:.1f}%",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="Trend",
                    value=trend,
                    delta=None
                )
    
    def _add_stock_insights(self, config: Dict[str, Any], data: Dict[str, Any]):
        """Add stock-specific insights"""
        if not config.get('close'):
            return
        
        closes = [float(c) for c in config['close']]
        
        if len(closes) < 2:
            return
        
        first_close = closes[0]
        last_close = closes[-1]
        
        if first_close > 0:
            return_pct = ((last_close - first_close) / first_close) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Period Return",
                    value=f"{return_pct:+.1f}%",
                    delta=f"${last_close:.2f}"
                )
            
            with col2:
                high = max([float(h) for h in config['high']])
                low = min([float(l) for l in config['low']])
                st.metric(
                    label="Trading Range",
                    value=f"${low:.2f} - ${high:.2f}",
                    delta=None
                )


# Global instance
chart_renderer = ChartRenderer()
