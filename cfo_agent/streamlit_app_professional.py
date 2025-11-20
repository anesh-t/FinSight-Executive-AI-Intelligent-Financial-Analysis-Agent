"""
Professional CFO Intelligence Platform - Enhanced UI
Modern, clean, and corporate-ready interface
"""
import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time
import importlib
import sys

# Force reload chart renderer
if 'streamlit_chart_renderer' in sys.modules:
    importlib.reload(sys.modules['streamlit_chart_renderer'])
from streamlit_chart_renderer import chart_renderer

# Page configuration
st.set_page_config(
    page_title="CFO Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "# CFO Intelligence Platform\nPowered by AI"
    }
)

# Professional CSS with corporate styling
st.markdown("""
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container - Clean white/light theme */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        color: #1a1a1a;
    }
    
    /* Header styling - Professional gradient */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem !important;
        text-align: center;
        padding: 30px 0 10px 0;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: #667eea;
        font-weight: 700;
        border-bottom: 3px solid #667eea;
        padding-bottom: 12px;
        margin-top: 30px;
        font-size: 1.8rem !important;
    }
    
    h3 {
        color: #764ba2;
        font-weight: 600;
        font-size: 1.3rem !important;
        margin-top: 20px;
    }
    
    /* Sidebar styling - Professional dark sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid #0f3460;
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        border-bottom-color: #667eea !important;
        -webkit-text-fill-color: #ffffff !important;
        background: none !important;
    }
    
    /* Chat messages - Card-based design */
    .stChatMessage {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    /* User message - Blue accent */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
        border-left: 4px solid #667eea;
    }
    
    /* Assistant message - Purple accent */
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
        border-left: 4px solid #764ba2;
    }
    
    /* Input box - Modern design */
    .stTextInput input {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }
    
    /* Buttons - Professional style */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Radio buttons - Modern style */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 12px;
    }
    
    /* Metrics - Card style */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #667eea;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 14px;
        font-weight: 600;
    }
    
    /* Success/Error/Warning boxes */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        border-radius: 12px;
        padding: 16px;
        color: #155724;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid #dc3545;
        border-radius: 12px;
        padding: 16px;
        color: #721c24;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #ffc107;
        border-radius: 12px;
        padding: 16px;
        color: #856404;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 4px solid #17a2b8;
        border-radius: 12px;
        padding: 16px;
        color: #0c5460;
    }
    
    /* Expander - Clean design */
    .streamlit-expanderHeader {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        color: #667eea;
        font-weight: 600;
        padding: 12px;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f8f9ff;
        border-color: #667eea;
    }
    
    /* Dataframe styling */
    .dataframe {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #ffffff;
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        color: #666;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Caption text */
    .caption {
        color: #666;
        font-size: 14px;
        font-style: italic;
    }
    
    /* Code blocks */
    code {
        background: #f8f9ff;
        color: #667eea;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    /* Links */
    a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "query_mode" not in st.session_state:
    st.session_state.query_mode = "Structured Data (SQL)"

# Professional Header
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='margin-bottom: 10px;'>📊 CFO Intelligence Platform</h1>
    <p style='font-size: 18px; color: #666; font-weight: 500;'>
        AI-Powered Financial Analytics & Insights
    </p>
</div>
""", unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    # Logo/Branding
    st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <div style='font-size: 48px; margin-bottom: 10px;'>📊</div>
        <h2 style='margin: 0; font-size: 24px; color: #ffffff !important;'>CFO Intelligence</h2>
        <p style='color: #aaa; font-size: 14px; margin-top: 5px;'>Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Query Mode Selector
    st.markdown("### 🎯 Query Mode")
    mode_options = [
        "💾 Structured Data (SQL)",
        "📚 Unstructured Data (10-K)",
        "🔄 Hybrid (SQL + 10-K)"
    ]
    
    selected_mode = st.radio(
        "Choose your data source:",
        mode_options,
        index=mode_options.index(f"💾 {st.session_state.query_mode}") if f"💾 {st.session_state.query_mode}" in mode_options else 0,
        help="Select which data source to query",
        label_visibility="collapsed"
    )
    
    st.session_state.query_mode = selected_mode.split(" ", 1)[1]
    
    # Mode description
    mode_descriptions = {
        "Structured Data (SQL)": "Fast queries against financial databases (1-2s)",
        "Unstructured Data (10-K)": "Semantic search over 10-K filings (3-5s)",
        "Hybrid (SQL + 10-K)": "Combined quantitative + qualitative analysis (6-10s)"
    }
    st.caption(mode_descriptions[st.session_state.query_mode])
    
    st.markdown("---")
    
    # System Status
    st.markdown("### 📡 System Status")
    
    # Check backend health
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        backend_status = "🟢 Online" if health_response.status_code == 200 else "🟡 Degraded"
        backend_delta = "Healthy" if health_response.status_code == 200 else "Issues"
    except:
        backend_status = "🔴 Offline"
        backend_delta = "Down"
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Backend", backend_status, delta=backend_delta)
    with col2:
        st.metric("Database", "🟢 Live", delta="Connected")
    
    st.markdown("---")
    
    # Session Analytics
    st.markdown("### 📈 Session Analytics")
    
    try:
        response = requests.get(f"{API_BASE_URL}/session/{st.session_state.session_id}/context", timeout=2)
        if response.status_code == 200:
            context = response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Queries", context.get("query_count", 0), delta="Total")
            with col2:
                st.metric("Companies", len(context.get("last_tickers", [])), delta="Active")
            
            if context.get("last_tickers"):
                st.markdown("**📌 Active Tickers:**")
                ticker_badges = " ".join([
                    f'<span style="background: linear-gradient(135deg, #667eea, #764ba2); '
                    f'color: white; padding: 6px 12px; border-radius: 8px; '
                    f'margin: 4px; display: inline-block; font-weight: 600; '
                    f'font-size: 12px;">{t}</span>'
                    for t in context.get("last_tickers", [])
                ])
                st.markdown(ticker_badges, unsafe_allow_html=True)
    except:
        st.caption("Session analytics unavailable")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # Example Queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Structured (SQL):**
        - Show Apple, Microsoft revenue Q1 2023
        - What is Apple's ROE for 2023?
        - Compare AAPL and MSFT margins
        
        **Unstructured (10-K):**
        - Show Apple's gross margin breakdown
        - Display revenue by product category
        - Extract operating expenses table
        
        **Hybrid:**
        - What drove Apple's margin changes?
        - Explain revenue growth with context
        - Show numbers and business drivers
        """)
    
    # Footer
    st.markdown("---")
    st.caption(f"Session ID: {st.session_state.session_id[:12]}...")
    st.caption(f"© 2025 CFO Intelligence Platform")

# Main chat interface
st.markdown("### 💬 Chat Interface")

# Display chat messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show visualization button if available
        if message["role"] == "assistant" and "viz_metadata" in message and message["viz_metadata"]:
            viz_meta = message["viz_metadata"]
            if viz_meta.get("available"):
                chart_key = f"chart_data_{idx}"
                show_key = f"show_chart_{idx}"
                
                if show_key not in st.session_state:
                    st.session_state[show_key] = False
                
                col_btn, col_hint = st.columns([1, 3])
                with col_btn:
                    if st.button(
                        "📊 View Chart",
                        key=f"viz_btn_{idx}",
                        help="View historical trend chart"
                    ):
                        st.session_state[show_key] = not st.session_state[show_key]
                
                if st.session_state[show_key]:
                    if chart_key not in st.session_state:
                        with st.spinner("Generating chart..."):
                            try:
                                viz_response = requests.post(
                                    f"{API_BASE_URL}/api/visualize",
                                    json={
                                        "session_id": st.session_state.session_id,
                                        "intent": viz_meta["intent"],
                                        "params": viz_meta["params"],
                                        "question": viz_meta.get("question", "")
                                    },
                                    timeout=10
                                )
                                
                                if viz_response.status_code == 200:
                                    viz_data = viz_response.json()
                                    st.session_state[chart_key] = viz_data
                                else:
                                    st.error(f"Chart generation failed: {viz_response.text}")
                            except Exception as e:
                                st.error(f"Error generating chart: {str(e)}")
                    
                    if chart_key in st.session_state:
                        chart_renderer.render_chart(
                            st.session_state[chart_key]["chart_data"],
                            st.session_state[chart_key]["chart_config"]
                        )

# Chat input
if prompt := st.chat_input("Ask a financial question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                start_time = time.time()
                current_mode = st.session_state.query_mode
                
                # Route based on mode
                if current_mode == "Structured Data (SQL)":
                    response = requests.post(
                        f"{API_BASE_URL}/ask",
                        json={
                            "question": prompt,
                            "session_id": st.session_state.session_id,
                            "enable_hitl": False
                        },
                        timeout=30
                    )
                
                elif current_mode == "Unstructured Data (10-K)":
                    # RAG mode - handled in streamlit directly
                    import sys
                    from pathlib import Path
                    sys.path.insert(0, str(Path(__file__).parent))
                    
                    from langchain_openai import ChatOpenAI
                    from langchain.prompts import ChatPromptTemplate
                    
                    table_keywords = ['table', 'breakdown', 'by segment', 'by category', 'by product', 'by region', 'products and services', 'products vs services', 'segment']
                    is_table_query = any(keyword in prompt.lower() for keyword in table_keywords)
                    
                    if is_table_query:
                        sys.path.insert(0, str(Path(__file__).parent / 'rag_system'))
                        from table_retriever import TableRetriever
                        
                        company = None
                        year = None
                        if 'apple' in prompt.lower():
                            company = 'Apple'
                        if '2019' in prompt:
                            year = 2019
                        elif '2022' in prompt:
                            year = 2022
                        
                        table_retriever = TableRetriever(verbose=False)
                        chunks = table_retriever.retrieve_table(
                            query=prompt,
                            company=company,
                            year=year,
                            top_k=10
                        )
                        table_retriever.close()
                        
                        if chunks:
                            combined_text = "\n\n".join([chunk.chunk_text for chunk in chunks[:3]])
                            rag_result_text = combined_text
                            rag_success = True
                        else:
                            rag_result_text = "No table data found."
                            rag_success = False
                    else:
                        from master_agent.execution.agent_bridge import AgentCoordinator
                        coordinator = AgentCoordinator(verbose=False, use_quick_mode=True)
                        rag_result = coordinator.query_rag(prompt)
                        rag_result_text = rag_result.text
                        rag_success = rag_result.success
                    
                    if is_table_query and rag_success:
                        llm = ChatOpenAI(model="gpt-5.1", temperature=0.0, max_tokens=1000)
                        format_prompt = ChatPromptTemplate.from_messages([
                            ("system", "You are a financial analyst. Format the 10-K data into clear markdown tables. Be concise and compact. Do NOT add extra blank lines between sections."),
                            ("user", "Question: {question}\n\n10-K Data: {data}\n\nFormat this as a compact answer with markdown tables. Use single line breaks between sections, not multiple blank lines.")
                        ])
                        
                        messages = format_prompt.format_messages(question=prompt, data=rag_result_text)
                        formatted_response = llm.invoke(messages)
                        
                        import re
                        final_text = formatted_response.content.strip()
                        final_text = re.sub(r'\n\n+', '\n', final_text)
                        final_text = re.sub(r'\n(#{1,6} )', r'\n\n\1', final_text)
                        final_text = re.sub(r'\n([A-Z][A-Za-z ]+:?\n)', r'\n\n\1', final_text)
                    else:
                        final_text = rag_result_text if rag_success else "No 10-K data found for this query."
                    
                    response = type('obj', (object,), {
                        'status_code': 200,
                        'json': lambda self: {
                            "response": final_text,
                            "viz_metadata": None
                        }
                    })()
                
                else:  # Hybrid mode
                    response = requests.post(
                        f"{API_BASE_URL}/ask/hybrid",
                        json={
                            "question": prompt,
                            "session_id": st.session_state.session_id
                        },
                        timeout=60
                    )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("response", "No response received")
                    
                    # Cleanup whitespace before display
                    import re
                    if answer and answer.strip():
                        answer = re.sub(r'\n\n+', '\n', answer)
                        answer = re.sub(r'\n(#{1,6} )', r'\n\n\1', answer)
                        answer = re.sub(r'\n([A-Z][A-Za-z ]+Percentage)', r'\n\n\1', answer)
                    
                    st.success(f"✅ Completed in {response_time:.2f}s")
                    st.markdown(answer)
                    
                    # Store message with viz metadata
                    viz_metadata = result.get("viz_metadata")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "viz_metadata": viz_metadata
                    })
                    
                    # Show viz button if available
                    if viz_metadata and viz_metadata.get("available"):
                        msg_idx = len(st.session_state.messages) - 1
                        chart_key = f"chart_data_{msg_idx}"
                        show_key = f"show_chart_{msg_idx}"
                        
                        if show_key not in st.session_state:
                            st.session_state[show_key] = False
                        
                        col_btn, col_hint = st.columns([1, 3])
                        with col_btn:
                            if st.button(
                                "📊 View Chart",
                                key=f"viz_btn_new_{msg_idx}",
                                help="View historical trend chart"
                            ):
                                st.session_state[show_key] = True
                                st.rerun()
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.error(response.text)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; color: #666;'>
    <p style='font-size: 14px; margin: 0;'>
        <strong>CFO Intelligence Platform</strong> | Powered by AI | © 2025
    </p>
    <p style='font-size: 12px; margin-top: 8px;'>
        Using GPT-4o-mini | PostgreSQL | pgvector | LangGraph
    </p>
</div>
""", unsafe_allow_html=True)
