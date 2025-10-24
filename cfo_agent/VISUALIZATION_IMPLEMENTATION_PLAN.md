# 🎨 VISUALIZATION IMPLEMENTATION PLAN

**Based on complete understanding of 93 query types and data structure**

---

## 🔍 KEY FINDINGS FROM ANALYSIS

### **What We Learned:**

1. **Data Coverage is Excellent:**
   - Annual: 2019-2023 (5 years complete)
   - Quarterly: Q1 2019 - Q2 2025 (25+ quarters)
   - All 5 companies have full coverage
   - 100% completeness for key metrics

2. **Current Problem:**
   - User asks: "Apple revenue 2023"
   - We return: "Apple reported revenue of $385.71B"
   - User doesn't know: Is this good? Growing? Declining?
   - **We need context = visualization**

3. **93 Query Types Map to 6 Chart Patterns:**
   - Time Series Line (60% of queries)
   - Comparison Bar (20%)
   - Dual-Axis (10%)
   - OHLC/Candlestick (5%)
   - Dashboard (3%)
   - Other (2%)

---

## 🎯 RECOMMENDED IMPLEMENTATION: HYBRID APPROACH

### **Why Hybrid?**
- ✅ No overhead for users who just want text
- ✅ Professional presentation for those who want visuals
- ✅ Easy to implement incrementally
- ✅ Can add auto-detection later

### **User Experience Flow:**

```
┌──────────────────────────────────────────────────────────┐
│ User Query: "Apple revenue 2023"                         │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ BACKEND RESPONSE                                         │
│ {                                                        │
│   "response": "Apple reported revenue of $385.71B...",  │
│   "viz_available": true,                                │
│   "viz_config": {                                        │
│     "type": "line",                                      │
│     "title": "Apple Revenue Trend",                      │
│     "suggested": true  ← Indicate we recommend chart    │
│   }                                                      │
│ }                                                        │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌──────────────────────────────────────────────────────────┐
│ STREAMLIT DISPLAY                                        │
│                                                          │
│ ✅ Query completed in 2.3s                               │
│                                                          │
│ Apple Inc. (AAPL) reported revenue of $385.71B          │
│ for FY2023.                                              │
│                                                          │
│ [📊 View 5-Year Trend] ← Button appears                 │
│                                                          │
│ Sources: ALPHAVANTAGE_FIN...                             │
└──────────────────────────────────────────────────────────┘
             ↓ (User clicks button)
┌──────────────────────────────────────────────────────────┐
│ CHART RENDERED                                           │
│                                                          │
│ Apple Revenue Trend (2019-2023)                          │
│                                                          │
│ $400B ┤                           ●                      │
│       │                       ●                          │
│ $300B ┤                   ●                              │
│       │               ●                                  │
│ $200B ┤           ●                                      │
│       └───────────────────────────                       │
│        2019 2020 2021 2022 2023                          │
│                                                          │
│ 5-Year CAGR: +10.3% | Latest: $385.71B                  │
│ Status: Slight decline from 2022 peak (-2.2%)           │
└──────────────────────────────────────────────────────────┘
```

---

## 🏗️ ARCHITECTURE

### **Component 1: Visualization Data Fetcher**

**File:** `cfo_agent/viz_data_fetcher.py` (NEW)

```python
"""
Fetch extended data for visualizations
Determines chart type and fetches appropriate historical data
"""

class VizDataFetcher:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def get_viz_config(self, intent, params, query_result):
        """Determine if visualization is applicable and what type"""
        
        # Check if viz makes sense
        if not self._should_visualize(intent, params):
            return {"available": False}
        
        # Determine chart type
        chart_type = self._determine_chart_type(intent, params)
        
        return {
            "available": True,
            "type": chart_type,
            "suggested": True,  # Auto-suggest for time-series queries
            "endpoint": "/api/visualize"
        }
    
    def _should_visualize(self, intent, params):
        """Check if visualization makes sense"""
        # Visualize for:
        # - Single company queries (not multi-company yet)
        # - Time-series metrics (revenue, margins, stock)
        # - NOT for: macro-only, text descriptions
        
        viz_intents = [
            'annual_metrics', 'quarter_snapshot',
            'stock_price_annual', 'stock_price_quarterly',
            'complete_annual', 'complete_quarterly'
        ]
        
        has_ticker = 'ticker' in params
        is_viz_intent = any(vi in intent for vi in viz_intents)
        
        return has_ticker and is_viz_intent
    
    def _determine_chart_type(self, intent, params):
        """Map intent to chart type"""
        
        if 'stock' in intent:
            # Stock queries → OHLC or line
            if 'quarter' in intent:
                return 'ohlc'  # Candlestick for quarterly
            return 'line'  # Line for annual
        
        elif 'complete' in intent or 'full' in intent:
            return 'dashboard'  # Mini dashboard
        
        elif 'comparison' in intent or 'compare' in intent:
            return 'grouped_bar'  # Multi-company comparison
        
        else:
            # Default: time series line chart
            return 'line'
    
    async def fetch_viz_data(self, intent, params):
        """Fetch extended historical data for visualization"""
        
        ticker = params.get('ticker')
        fy = params.get('fy')
        fq = params.get('fq')
        
        if 'annual' in intent:
            return await self._fetch_annual_trend(ticker, fy)
        elif 'quarter' in intent:
            return await self._fetch_quarterly_trend(ticker, fy, fq)
        else:
            return await self._fetch_annual_trend(ticker, fy)
    
    async def _fetch_annual_trend(self, ticker, target_year):
        """Fetch 5-year annual trend"""
        
        sql = """
        SELECT 
            fiscal_year,
            revenue_annual/1e9 as revenue_b,
            net_income_annual/1e9 as net_income_b,
            gross_margin_annual*100 as gross_margin_pct,
            operating_margin_annual*100 as operating_margin_pct,
            net_margin_annual*100 as net_margin_pct,
            roe_annual*100 as roe_pct,
            close_price_eoy as stock_price
        FROM mv_company_complete_annual
        WHERE ticker = $1
          AND fiscal_year BETWEEN $2 AND $3
        ORDER BY fiscal_year ASC
        """
        
        start_year = target_year - 4 if target_year else 2019
        end_year = target_year if target_year else 2023
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(sql, ticker, start_year, end_year)
            return [dict(row) for row in rows]
    
    async def _fetch_quarterly_trend(self, ticker, target_year, target_quarter):
        """Fetch 8-quarter trend"""
        
        sql = """
        SELECT 
            fiscal_year,
            fiscal_quarter,
            revenue/1e9 as revenue_b,
            net_income/1e9 as net_income_b,
            gross_margin*100 as gross_margin_pct,
            operating_margin*100 as operating_margin_pct,
            net_margin*100 as net_margin_pct,
            roe*100 as roe_pct,
            close_price as stock_price,
            open_price,
            high_price,
            low_price
        FROM vw_company_complete_quarter
        WHERE ticker = $1
        ORDER BY fiscal_year DESC, fiscal_quarter DESC
        LIMIT 8
        """
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(sql, ticker)
            return [dict(row) for row in rows][::-1]  # Reverse to chronological
```

---

### **Component 2: New FastAPI Endpoint**

**File:** `cfo_agent/app.py` (MODIFY)

```python
from viz_data_fetcher import VizDataFetcher

# Initialize
viz_fetcher = VizDataFetcher(db_pool)

# Add to /ask response
@app.post("/ask")
async def ask_question(request: QueryRequest):
    # ... existing logic ...
    
    result = await graph.ainvoke(state)
    
    # Check if visualization is available
    viz_config = await viz_fetcher.get_viz_config(
        intent=result.get('intent'),
        params=result.get('params', {}),
        query_result=result.get('query_result')
    )
    
    return {
        "response": result.get("final_response"),
        "session_id": request.session_id,
        "viz_config": viz_config  # NEW!
    }

# NEW endpoint for fetching viz data
@app.post("/api/visualize")
async def get_visualization(request: VisualizationRequest):
    """
    Fetch visualization data based on previous query context
    """
    # Get session context
    session_data = get_session_data(request.session_id)
    
    # Fetch extended data
    viz_data = await viz_fetcher.fetch_viz_data(
        intent=session_data['intent'],
        params=session_data['params']
    )
    
    return {
        "chart_type": viz_fetcher._determine_chart_type(
            session_data['intent'], 
            session_data['params']
        ),
        "data": viz_data,
        "config": generate_chart_config(viz_data, session_data)
    }

class VisualizationRequest(BaseModel):
    session_id: str
    chart_type: Optional[str] = None  # User can override
```

---

### **Component 3: Streamlit Chart Renderer**

**File:** `cfo_agent/streamlit_app.py` (MODIFY)

```python
import plotly.graph_objects as go
import plotly.express as px

# After displaying text response
result = response.json()
answer = result.get("response", "")
viz_config = result.get("viz_config", {})

# Display text
st.text(answer)

# Check if visualization is available
if viz_config.get("available", False):
    col1, col2 = st.columns([1, 4])
    
    with col1:
        show_chart = st.button("📊 View Chart", key=f"viz_{len(st.session_state.messages)}")
    
    with col2:
        if viz_config.get("suggested"):
            st.caption("💡 Recommended: View trend for context")
    
    if show_chart:
        with st.spinner("Loading chart..."):
            # Fetch visualization data
            viz_response = requests.post(
                f"{API_URL}/api/visualize",
                json={
                    "session_id": st.session_state.session_id
                }
            )
            
            if viz_response.status_code == 200:
                viz_data = viz_response.json()
                
                # Render chart based on type
                if viz_data['chart_type'] == 'line':
                    render_line_chart(viz_data)
                elif viz_data['chart_type'] == 'ohlc':
                    render_ohlc_chart(viz_data)
                elif viz_data['chart_type'] == 'grouped_bar':
                    render_grouped_bar(viz_data)
                elif viz_data['chart_type'] == 'dashboard':
                    render_mini_dashboard(viz_data)

def render_line_chart(viz_data):
    """Render time series line chart"""
    data = viz_data['data']
    config = viz_data['config']
    
    fig = go.Figure()
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=[d['fiscal_year'] for d in data],
        y=[d[config['y_field']] for d in data],
        mode='lines+markers',
        name=config['metric_name'],
        line=dict(color='#4a9eff', width=3),
        marker=dict(size=10, line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>' + 
                      config['metric_name'] + ': %{y:.2f}<br>' +
                      '<extra></extra>'
    ))
    
    # Add trend line if available
    if config.get('show_trend'):
        # Calculate linear regression
        x_vals = list(range(len(data)))
        y_vals = [d[config['y_field']] for d in data]
        
        # Simple trend calculation
        import numpy as np
        z = np.polyfit(x_vals, y_vals, 1)
        p = np.poly1d(z)
        trend_y = [p(x) for x in x_vals]
        
        fig.add_trace(go.Scatter(
            x=[d['fiscal_year'] for d in data],
            y=trend_y,
            mode='lines',
            name='Trend',
            line=dict(color='orange', width=2, dash='dash'),
            hoverinfo='skip'
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': config['title'],
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#e8eaed'}
        },
        xaxis_title="Fiscal Year",
        yaxis_title=config['y_label'],
        template="plotly_dark",
        hovermode='x unified',
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e8eaed'},
        xaxis={'gridcolor': 'rgba(255,255,255,0.1)'},
        yaxis={'gridcolor': 'rgba(255,255,255,0.1)'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add insights
    if config.get('insights'):
        st.info(config['insights'])

def render_ohlc_chart(viz_data):
    """Render OHLC/Candlestick for stock prices"""
    data = viz_data['data']
    
    fig = go.Figure(data=[go.Candlestick(
        x=[f"Q{d['fiscal_quarter']} {d['fiscal_year']}" for d in data],
        open=[d['open_price'] for d in data],
        high=[d['high_price'] for d in data],
        low=[d['low_price'] for d in data],
        close=[d['close_price'] for d in data],
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    )])
    
    fig.update_layout(
        title="Stock Price Movement (Last 8 Quarters)",
        yaxis_title="Price ($)",
        template="plotly_dark",
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_grouped_bar(viz_data):
    """Render grouped bar chart for comparisons"""
    data = viz_data['data']
    
    fig = go.Figure()
    
    # Group by company
    companies = set(d['ticker'] for d in data)
    
    for company in companies:
        company_data = [d for d in data if d['ticker'] == company]
        
        fig.add_trace(go.Bar(
            name=company,
            x=[d['fiscal_year'] for d in company_data],
            y=[d['revenue_b'] for d in company_data],
            text=[f"${d['revenue_b']:.1f}B" for d in company_data],
            textposition='outside'
        ))
    
    fig.update_layout(
        title="Revenue Comparison",
        xaxis_title="Fiscal Year",
        yaxis_title="Revenue ($B)",
        template="plotly_dark",
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

---

## 📋 IMPLEMENTATION CHECKLIST

### **Phase 1: Foundation** (Week 1, Day 1-2)
- [ ] Create `viz_data_fetcher.py`
- [ ] Add `VizDataFetcher` class with basic methods
- [ ] Test data fetching with sample queries
- [ ] Verify 5-year and 8-quarter data retrieval

### **Phase 2: Backend Integration** (Week 1, Day 3-4)
- [ ] Modify `/ask` endpoint to include `viz_config`
- [ ] Create `/api/visualize` endpoint
- [ ] Add session context storage
- [ ] Test API responses

### **Phase 3: Frontend Rendering** (Week 1, Day 5-7)
- [ ] Add "View Chart" button in Streamlit
- [ ] Implement `render_line_chart()`
- [ ] Implement `render_ohlc_chart()`
- [ ] Add Plotly styling for dark theme
- [ ] Test with sample queries

### **Phase 4: Testing & Polish** (Week 2)
- [ ] Test all 93 query types for viz applicability
- [ ] Add insights generation (CAGR, trends)
- [ ] Optimize chart loading speed
- [ ] Add chart export functionality
- [ ] User feedback collection

---

## 🎯 SUCCESS METRICS

1. **Adoption:** % of queries where users click "View Chart"
2. **Value:** User survey on usefulness (target: 4.5/5)
3. **Performance:** Chart load time < 2 seconds
4. **Coverage:** 60%+ of queries have viz available

---

## ✅ READY TO START?

We have:
- ✅ Complete understanding of data structure
- ✅ Mapped all 93 query types to chart types
- ✅ Designed hybrid approach
- ✅ Detailed architecture
- ✅ Implementation plan

**Shall I start building Component 1 (VizDataFetcher)?**
