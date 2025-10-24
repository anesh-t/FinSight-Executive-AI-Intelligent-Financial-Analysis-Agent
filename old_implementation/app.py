import streamlit as st
import pandas as pd
from datetime import datetime
from cfo_assistant import CFOAssistant
from database import SupabaseConnector
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="CFO Assistant Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for company-colored panels and consistent styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .apple-card { background: linear-gradient(135deg, #007AFF 0%, #5AC8FA 100%); color: white; }
    .microsoft-card { background: linear-gradient(135deg, #00A4EF 0%, #7FBA00 100%); color: white; }
    .amazon-card { background: linear-gradient(135deg, #FF9900 0%, #FFB84D 100%); color: white; }
    .google-card { background: linear-gradient(135deg, #FBBC04 0%, #EA4335 100%); color: white; }
    .meta-card { background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%); color: white; }
    
    .stButton>button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    
    /* Consistent section headers */
    h3 {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #111827 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Info boxes */
    .stAlert {
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        font-family: 'Fira Code', 'Courier New', monospace !important;
        background-color: #1f2937 !important;
        border-radius: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cfo_assistant' not in st.session_state:
    st.session_state.cfo_assistant = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_result' not in st.session_state:
    st.session_state.current_result = None

with st.sidebar:
    st.markdown("### 🎯 CFO Assistant")
    st.markdown("**AI-Powered Financial Analysis**")
    st.markdown("---")
    
    # Initialize button
    if st.button("🚀 Initialize CFO Assistant", use_container_width=True):
        with st.spinner("Connecting to database and initializing agent..."):
            try:
                st.session_state.cfo_assistant = CFOAssistant(verbose=False)
                st.success("✅ CFO Assistant initialized!")
                st.info("🔗 LangChain SQL Agent + Enhanced Analysis")
            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📝 Example Queries")
    
    st.markdown("**💡 Simple Queries:**")
    simple_queries = [
        "Show Apple revenue for 2023",
        "Compare Microsoft and Google net income",
        "What is Amazon's ROE trend?",
    ]
    
    for idx, query in enumerate(simple_queries):
        if st.button(f"📌 {query}", key=f"simple_{idx}"):
            st.session_state.current_query = query
    
    st.markdown("**🔥 Advanced Queries:**")
    advanced_queries = [
        "Compare revenue growth rates for all companies since 2020",
        "Which company had the highest ROE in 2023?",
        "Show correlation between Fed rate and tech stock returns",
        "Rank companies by operating margin improvement 2020-2023",
        "Compare debt-to-equity ratios across all companies"
    ]
    
    for idx, query in enumerate(advanced_queries):
        if st.button(f"🚀 {query}", key=f"advanced_{idx}"):
            st.session_state.current_query = query
    
    st.markdown("---")
    with st.expander("❓ Query Tips"):
        st.markdown("""
        **What you can ask:**
        - 📊 **Comparisons:** "Compare X and Y"
        - 📈 **Trends:** "Show trend of X over time"
        - 🏆 **Rankings:** "Which company has highest X?"
        - 🔍 **Specific data:** "Show Apple revenue in 2023"
        - 📉 **Growth:** "Calculate revenue growth rate"
        - 💹 **Ratios:** "Compare debt-to-equity ratios"
        - 🌍 **Macro:** "Show GDP impact on margins"
        
        **Available metrics:**
        - Revenue, Net Income, EPS, Assets, Equity
        - ROE, ROA, Margins (gross, operating, net)
        - Stock returns, Volatility, Dividends
        - GDP, CPI, Fed Funds Rate, Unemployment
        
        **Time periods:** 2019-2025, by quarter
        **Companies:** Apple, Microsoft, Amazon, Google, Meta
        """)
    
    st.markdown("---")
    st.markdown("⏱️ **Tip:** Wait 30 seconds between queries to avoid rate limits")

# Main content
st.markdown('<div class="main-header">📊 CFO Assistant Dashboard</div>', unsafe_allow_html=True)
st.markdown("**AI-Powered Financial Analysis for Tech Giants** | Apple • Microsoft • Amazon • Google • Meta")

# Check if assistant is initialized
if st.session_state.cfo_assistant is None:
    st.info("👈 Please initialize the CFO Assistant from the sidebar to get started.")
    
    # Show company cards
    st.markdown("### 🏢 Companies in Database")
    cols = st.columns(5)
    
    company_info = [
        ("Apple", "apple-card", "🍎"),
        ("Microsoft", "microsoft-card", "🪟"),
        ("Amazon", "amazon-card", "📦"),
        ("Google", "google-card", "🔍"),
        ("Meta", "meta-card", "👥")
    ]
    
    for col, (company, card_class, emoji) in zip(cols, company_info):
        with col:
            st.markdown(f"""
            <div class="metric-card {card_class}">
                <h3>{emoji} {company}</h3>
                <p>2019-2025 Data</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Available Data")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Financial Metrics:**
        - Revenue & Income
        - Assets & Liabilities
        - Cash Flow
        - Operating Metrics
        """)
    
    with col2:
        st.markdown("""
        **Analysis Tools:**
        - Financial Ratios (ROE, ROA, Margins)
        - Stock Performance
        - Macro Economic Indicators
        - Event Timeline Analysis
        """)

else:
    # Query interface
    st.markdown("### 💬 Ask a Financial Question")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input(
            "Enter your question:",
            value=st.session_state.get('current_query', ''),
            placeholder="e.g., Compare revenue growth for all companies in 2023",
            key="query_input"
        )
    
    with col2:
        # Analyze button
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if user_query:
                try:
                    with st.spinner("🤖 Analyzing your question..."):
                        result = st.session_state.cfo_assistant.analyze(user_query)
                        st.session_state.current_result = result
                        st.session_state.query_history.append({
                            'query': user_query,
                            'timestamp': datetime.now(),
                            'status': result.get('status', 'unknown')
                        })
                        st.rerun()
                except Exception as e:
                    import traceback
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.code(traceback.format_exc())
                    st.session_state.current_result = {
                        'status': 'error',
                        'message': str(e),
                        'query': user_query
                    }
    
    # Display results
    if st.session_state.current_result:
        result = st.session_state.current_result
        
        # Check if result has status
        if not isinstance(result, dict) or 'status' not in result:
            st.error("❌ Invalid result format")
            st.code(str(result))
            st.stop()
        
        if result.get('status') == 'success':
            # Show question classification
            if result.get('intent'):
                category_name = result['intent'].replace('_', ' ').title()
                analysis_type = result.get('analysis_type', 'summary').title()
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.caption(f"📊 **Category:** {category_name}")
                with col2:
                    st.caption(f"🎯 **Analysis Type:** {analysis_type}")
            
            # Executive Summary
            st.markdown("### 📋 Executive Summary")
            st.info(result.get('summary', 'No summary available'))
            
            # CFO Narrative with enhanced formatting
            st.markdown("### 💼 CFO Analysis")
            st.markdown(result.get('narrative', 'Analysis not available'))
            
            # Key Metrics Card (if numeric data exists)
            if result.get('data') is not None and not result['data'].empty:
                numeric_cols = result['data'].select_dtypes(include=['number']).columns.tolist()
                numeric_cols = [col for col in numeric_cols if col not in ['fiscal_year', 'fiscal_quarter', 'company_id']]
                
                if numeric_cols and len(result['data']) > 0:
                    st.markdown("### 📊 Key Metrics")
                    cols = st.columns(min(4, len(numeric_cols)))
                    for idx, col_name in enumerate(numeric_cols[:4]):
                        with cols[idx]:
                            value = result['data'][col_name].iloc[0]
                            # Format large numbers
                            if abs(value) > 1_000_000_000:
                                display_val = f"${value/1_000_000_000:.2f}B"
                            elif abs(value) > 1_000_000:
                                display_val = f"${value/1_000_000:.2f}M"
                            elif abs(value) < 1 and abs(value) > 0:
                                display_val = f"{value*100:.2f}%"
                            else:
                                display_val = f"{value:,.2f}"
                            
                            st.metric(
                                label=col_name.replace('_', ' ').title(),
                                value=display_val
                            )
            
            # Data Table
            with st.expander("📑 View Data Table"):
                if result['data'] is not None and not result['data'].empty:
                    st.dataframe(result['data'], use_container_width=True)
                    
                    # Download button
                    csv = result['data'].to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download Data as CSV",
                        data=csv,
                        file_name=f"cfo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.write("No data available.")
            
            # Agent Response and SQL
            with st.expander("🤖 Technical Details (SQL & Agent Response)"):
                if result.get('sql_query'):
                    st.markdown("**SQL Query:**")
                    st.code(result['sql_query'], language='sql')
                    st.markdown("---")
                st.markdown("**Agent Response:**")
                st.code(result.get('agent_response', 'No details available'), language='text')
        
        else:
            st.error(f"❌ Error: {result.get('message', 'Unknown error')}")
            
            # Show debug info
            with st.expander("🐛 Debug Information"):
                st.write("Result keys:", list(result.keys()))
                st.write("Full result:", result)
    
    # Query History
    if st.session_state.query_history:
        with st.expander("📜 Query History"):
            for idx, item in enumerate(reversed(st.session_state.query_history[-10:])):
                status_emoji = "✅" if item['status'] == 'success' else "❌"
                st.markdown(f"{status_emoji} **{item['timestamp'].strftime('%H:%M:%S')}** - {item['query']}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>CFO Assistant Agent</strong> | Powered by GPT-3.5-Turbo + LangChain + Supabase</p>
    <p>Structured Financial Analysis for Apple, Microsoft, Amazon, Google, and Meta (2019-2025)</p>
</div>
""", unsafe_allow_html=True)
