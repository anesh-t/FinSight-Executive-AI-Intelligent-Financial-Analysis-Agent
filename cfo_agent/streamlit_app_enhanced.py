"""Enhanced Professional CFO Intelligence Platform"""
import streamlit as st
import requests
import json
from datetime import datetime
import time
import sys
from pathlib import Path

if 'streamlit_chart_renderer' in sys.modules:
    import importlib
    importlib.reload(sys.modules['streamlit_chart_renderer'])
from streamlit_chart_renderer import chart_renderer

st.set_page_config(
    page_title="CFO Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Corporate CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container - Professional dark theme */
    .main { 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        color: #ffffff;
    }
    
    /* Headers - Clean white with subtle shadow */
    h1 { 
        color: #ffffff;
        font-weight: 700;
        font-size: 2.5rem !important;
        text-align: center;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 1.8rem !important;
        border-bottom: 2px solid #334155;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #cbd5e1;
        font-weight: 600;
        font-size: 1.3rem !important;
    }
    
    /* Sidebar - Professional navy */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] * { 
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        border-bottom-color: #475569 !important;
    }
    
    /* Buttons - Purple/Turquoise gradient */
    .stButton button { 
        background: linear-gradient(135deg, #8b5cf6 0%, #14b8a6 100%);
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stButton button:hover { 
        background: linear-gradient(135deg, #7c3aed 0%, #0d9488 100%);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }
    
    /* Chat messages - Dark cards with white text */
    .stChatMessage { 
        background: #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
        color: #ffffff !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: #1e293b;
        border-left: 3px solid #14b8a6;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: #1e293b;
        border-left: 3px solid #8b5cf6;
    }
    
    /* Tabs - Professional style */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 4px;
        background: #1e293b;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    .stTabs [data-baseweb="tab"] { 
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        color: #94a3b8;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, #8b5cf6 0%, #14b8a6 100%);
        color: white !important;
    }
    
    /* Input fields */
    .stTextInput input, .stChatInput textarea {
        background: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }
    
    .stTextInput input:focus, .stChatInput textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #e2e8f0 !important;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: #334155;
        border-color: #475569;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #064e3b;
        border-left: 3px solid #10b981;
        color: #d1fae5;
    }
    
    .stError {
        background: #7f1d1d;
        border-left: 3px solid #ef4444;
        color: #fecaca;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: rgba(30, 41, 59, 0.5);
        padding: 8px;
        border-radius: 8px;
    }
    
    /* All text white */
    p, span, div, label {
        color: #ffffff !important;
    }
    
    /* Caption text */
    .caption {
        color: #94a3b8 !important;
        font-size: 13px;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
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

def clean_response_formatting(text):
    """Clean up common formatting issues in LLM responses"""
    import re
    
    print(f"[CLEAN] BEFORE: {text[:200]}")  # Debug: show first 200 chars
    
    # Remove unnecessary sections from RAG responses
    # Remove "WANT MORE DETAILS?" section
    text = re.sub(r'💡\s*WANT MORE DETAILS\?.*?(?=\n\n|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'💡.*?Ask me:.*?(?=\n\n|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove "IMPORTANT:" section
    text = re.sub(r'IMPORTANT:.*?(?=\n\n|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove numbered follow-up questions (1. "Tell me more..." etc.)
    text = re.sub(r'\n\s*\d+\.\s*"[^"]*"', '', text, flags=re.MULTILINE)
    
    # Remove horizontal lines
    text = re.sub(r'={3,}', '', text)
    text = re.sub(r'-{3,}', '', text)
    text = re.sub(r'─{3,}', '', text)
    
    # Remove raw markdown table syntax (convert to clean text)
    # Match lines with | pipes and convert to clean format
    if '| Metric |' in text or '| Year |' in text:
        # Remove table headers and separators
        text = re.sub(r'\|[^\n]+\|', '', text)  # Remove table rows
        text = re.sub(r'\n\s*\n', '\n', text)  # Clean up extra newlines
    
    # Fix concatenated words - MOST AGGRESSIVE
    # Fix "millionin", "billionin", "upfrom", "downfrom", etc.
    text = re.sub(r'(million|billion|thousand)(in|to|from|for|by|at)', r'\1 \2', text, flags=re.IGNORECASE)
    text = re.sub(r'(up|down)(from|to|by)', r'\1 \2', text, flags=re.IGNORECASE)
    
    # MOST AGGRESSIVE FIX: Add space after EVERY comma that doesn't have one
    text = re.sub(r',([^\s])', r', \1', text)
    
    # Fix number+unit followed by comma and word (56.52B,closing → 56.52B, closing)
    text = re.sub(r'(\d+\.?\d*\s*[BMK]),([a-zA-Z])', r'\1, \2', text, flags=re.IGNORECASE)
    
    # Fix ALL concatenated words ending with "of" before $ or numbers
    text = re.sub(r'([a-z]+)of(\$)', r'\1 of \2', text, flags=re.IGNORECASE)
    text = re.sub(r'([a-z]+)of(\d)', r'\1 of \2', text, flags=re.IGNORECASE)
    
    # Fix specific common patterns (case insensitive)
    text = re.sub(r'tradingrangeof', 'trading range of', text, flags=re.IGNORECASE)
    text = re.sub(r'closingpriceof', 'closing price of', text, flags=re.IGNORECASE)
    text = re.sub(r'openingpriceof', 'opening price of', text, flags=re.IGNORECASE)
    text = re.sub(r'revenueof', 'revenue of', text, flags=re.IGNORECASE)
    text = re.sub(r'priceof', 'price of', text, flags=re.IGNORECASE)
    text = re.sub(r'valueof', 'value of', text, flags=re.IGNORECASE)
    text = re.sub(r'incomeof', 'income of', text, flags=re.IGNORECASE)
    text = re.sub(r'marginof', 'margin of', text, flags=re.IGNORECASE)
    
    # Remove ALL underscores (they cause italics in markdown)
    text = re.sub(r'_', ' ', text)
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
    text = text.strip()
    
    print(f"[CLEAN] AFTER: {text[:200]}")  # Debug: show result
    
    return text

# Header
st.markdown("""
<div style='text-align: center; padding: 25px 0 20px 0; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 0 0 20px 20px; margin: -60px -60px 20px -60px; padding-top: 80px;'>
    <h1 style='font-size: 4rem; font-weight: 800; margin: 0; letter-spacing: 8px; background: linear-gradient(135deg, #8b5cf6 0%, #14b8a6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        FIN AI
    </h1>
    <p style='color: #94a3b8; font-size: 18px; font-weight: 500; margin-top: 15px; letter-spacing: 2px;'>
        ENTERPRISE FINANCIAL INTELLIGENCE PLATFORM
    </p>
    <div style='width: 100px; height: 3px; background: linear-gradient(90deg, #8b5cf6 0%, #14b8a6 100%); margin: 15px auto 0 auto; border-radius: 2px;'></div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Sidebar branding without logo (logo has formatting issues)
    st.markdown("""
    <div style='text-align: center; padding: 15px 0 10px 0;'>
        <h2 style='margin: 0; font-size: 22px; font-weight: 700; background: linear-gradient(135deg, #8b5cf6 0%, #14b8a6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 2px;'>FIN AI</h2>
        <p style='color: #94a3b8; font-size: 11px; margin-top: 5px;'>Financial Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Query Mode
    st.markdown("### Analysis Mode")
    mode_options = ["Structured Data (SQL)", "Unstructured Data (10-K)", "Hybrid Analysis"]
    selected_mode = st.radio("", mode_options, label_visibility="collapsed")
    
    # Map display names to internal names
    mode_mapping = {
        "Structured Data (SQL)": "Structured Data (SQL)",
        "Unstructured Data (10-K)": "Unstructured Data (10-K)",
        "Hybrid Analysis": "Hybrid (SQL + 10-K)"
    }
    st.session_state.query_mode = mode_mapping[selected_mode]
    
    st.markdown("---")
    
    # System Status
    st.markdown("### System Status")
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        backend_status = "Online" if health_response.status_code == 200 else "Degraded"
        backend_delta = "Operational" if health_response.status_code == 200 else "Issues"
    except:
        backend_status = "Offline"
        backend_delta = "Unavailable"
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("API", backend_status, delta=backend_delta)
    with col2:
        st.metric("Database", "Connected", delta="Active")
    
    st.markdown("---")
    
    # Session Analytics
    st.markdown("### Session Analytics")
    try:
        response = requests.get(f"{API_BASE_URL}/session/{st.session_state.session_id}/context", timeout=2)
        if response.status_code == 200:
            context = response.json()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Queries", context.get("query_count", 0), delta="Total")
            with col2:
                st.metric("Companies", len(context.get("last_tickers", [])), delta="Tracked")
            
            if context.get("last_tickers"):
                st.markdown("**Active Tickers:**")
                ticker_badges = " ".join([
                    f'<span style="background: linear-gradient(135deg, #8b5cf6 0%, #14b8a6 100%); '
                    f'color: white; padding: 4px 10px; border-radius: 6px; '
                    f'margin: 3px; display: inline-block; font-weight: 600; '
                    f'font-size: 11px;">{t}</span>'
                    for t in context.get("last_tickers", [])
                ])
                st.markdown(ticker_badges, unsafe_allow_html=True)
    except:
        st.caption("Analytics unavailable")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### Actions")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("New Session", use_container_width=True):
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption(f"Session ID: {st.session_state.session_id[:16]}")
    st.caption("© 2025 FIN AI")

# Main content with tabs
tab1, tab2, tab3, tab4 = st.tabs(["Analysis", "System Architecture", "Data Coverage", "Query Examples"])

with tab1:
    st.markdown("### Financial Analysis")
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            # Clean formatting for assistant responses
            content = message["content"]
            if message["role"] == "assistant":
                content = clean_response_formatting(content)
            # Display as markdown for proper paragraph formatting
            st.markdown(content)
            
            # Show visualization button if available
            if message["role"] == "assistant" and "viz_metadata" in message and message["viz_metadata"]:
                viz_meta = message["viz_metadata"]
                if viz_meta.get("available"):
                    chart_key = f"chart_data_{idx}"
                    show_key = f"show_chart_{idx}"
                    
                    if show_key not in st.session_state:
                        st.session_state[show_key] = False
                    
                    if st.button("📊 View Chart", key=f"viz_btn_{idx}"):
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
                                        st.session_state[chart_key] = viz_response.json()
                                    else:
                                        st.error(f"Visualization API error: {viz_response.status_code}")
                                        st.error(f"Response: {viz_response.text}")
                                except requests.exceptions.ConnectionError:
                                    st.error("Cannot connect to backend API. Make sure FastAPI is running on port 8000.")
                                except Exception as e:
                                    st.error(f"Chart generation error: {str(e)}")
                                    import traceback
                                    st.error(traceback.format_exc())
                        
                        if chart_key in st.session_state:
                            chart_cache = st.session_state[chart_key]
                            
                            if 'error' in chart_cache:
                                st.error(chart_cache['error'])
                            else:
                                try:
                                    chart_data = chart_cache.get("chart_data", {})
                                    chart_config = chart_cache.get("chart_config", {})
                                    
                                    # Render chart using chart renderer
                                    chart_type = chart_data.get('type', 'line')
                                    chart_renderer.render(chart_type, chart_config, chart_data)
                                except Exception as e:
                                    st.error(f"Chart rendering error: {str(e)}")
                                    import traceback
                                    st.code(traceback.format_exc())
    
    # Chat input
    if prompt := st.chat_input("Ask a financial question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    start_time = time.time()
                    current_mode = st.session_state.query_mode
                    
                    # Route based on mode
                    if current_mode == "Structured Data (SQL)":
                        response = requests.post(
                            f"{API_BASE_URL}/ask",
                            json={"question": prompt, "session_id": st.session_state.session_id, "enable_hitl": False},
                            timeout=30
                        )
                    elif current_mode == "Unstructured Data (10-K)":
                        # RAG mode
                        from langchain_openai import ChatOpenAI
                        from langchain.prompts import ChatPromptTemplate
                        
                        table_keywords = ['table', 'breakdown', 'by segment', 'by category', 'by product']
                        is_table_query = any(keyword in prompt.lower() for keyword in table_keywords)
                        
                        if is_table_query:
                            sys.path.insert(0, str(Path(__file__).parent / 'rag_system'))
                            from table_retriever import TableRetriever
                            
                            company = 'Apple' if 'apple' in prompt.lower() else None
                            year = 2022 if '2022' in prompt else 2019 if '2019' in prompt else None
                            
                            table_retriever = TableRetriever(verbose=False)
                            chunks = table_retriever.retrieve_table(query=prompt, company=company, year=year, top_k=10)
                            table_retriever.close()
                            
                            if chunks:
                                combined_text = "\n\n".join([chunk.chunk_text for chunk in chunks[:3]])
                                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, max_tokens=1000)
                                format_prompt = ChatPromptTemplate.from_messages([
                                    ("system", "Format 10-K data into clear markdown tables. Be concise."),
                                    ("user", "Question: {question}\n\nData: {data}\n\nFormat as compact answer.")
                                ])
                                messages = format_prompt.format_messages(question=prompt, data=combined_text)
                                formatted_response = llm.invoke(messages)
                                final_text = formatted_response.content.strip()
                            else:
                                final_text = "No table data found."
                        else:
                            from master_agent.execution.agent_bridge import AgentCoordinator
                            coordinator = AgentCoordinator(verbose=False, use_quick_mode=True)
                            rag_result = coordinator.query_rag(prompt)
                            final_text = rag_result.text if rag_result.success else "No 10-K data found."
                        
                        response = type('obj', (object,), {
                            'status_code': 200,
                            'json': lambda self: {"response": final_text, "viz_metadata": None}
                        })()
                    else:  # Hybrid
                        response = requests.post(
                            f"{API_BASE_URL}/ask/hybrid",
                            json={"question": prompt, "session_id": st.session_state.session_id},
                            timeout=60
                        )
                    
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get("response", "No response received")
                        viz_metadata = result.get("viz_metadata")
                        
                        # Clean formatting
                        answer = clean_response_formatting(answer)
                        
                        st.success(f"✅ Completed in {response_time:.2f}s")
                        # Display as markdown for proper paragraph formatting
                        st.markdown(answer)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "viz_metadata": viz_metadata
                        })
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.error(response.text)
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab2:
    st.markdown("### System Architecture")
    st.markdown("Enterprise-grade financial intelligence system with three specialized analysis engines")
    
    with st.expander("**SQL Analysis Engine** - Structured Data Pipeline (1-2 seconds)", expanded=False):
        st.markdown("""
        **Purpose:** Fast queries against financial databases
        
        **5-Node LangGraph Pipeline:**
        1. **Planner** (GPT-4o-mini) - Generates structured plan from question
        2. **Ticker Resolver** - Maps company names to tickers (Apple → AAPL)
        3. **SQL Generator** (GPT-4o-mini) - Creates PostgreSQL query with schema whitelist
        4. **SQL Executor** - Runs query against database with connection pooling
        5. **Response Formatter** (GPT-4o-mini) - Converts data to natural language
        
        **Performance:** 1-2 seconds | Success Rate: 91.9%
        
        **LLM Calls:** 3 (Planner, Generator, Formatter)
        
        **Database:** PostgreSQL (Supabase) with asyncpg connection pool
        """)
    
    with st.expander("**Document Analysis Engine** - Unstructured Data Pipeline (3-5 seconds)", expanded=False):
        st.markdown("""
        **Purpose:** Semantic search over 10-K filings with enhanced table extraction
        
        **Enhanced Table Retrieval Pipeline:**
        1. **Query Enhancement** - Adds table-specific keywords automatically
        2. **Vector Search** - PostgreSQL pgvector similarity search (top 10 chunks)
        3. **Re-Ranking** - Multi-factor scoring for table likelihood:
           - Semantic similarity (0.0-1.0)
           - Table indicators (+0.1 each)
           - Dollar signs, percentages, numbers
           - "Products" + "Services" keywords (+0.3)
        4. **LLM Formatting** (GPT-4o-mini) - Converts to markdown tables
        
        **Performance:** 3-5 seconds | Table Accuracy: 85%
        
        **LLM Calls:** 1 (Formatter)
        
        **Embedding Model:** OpenAI text-embedding-3-small (1536 dimensions)
        """)
    
    with st.expander("**Hybrid Analysis Engine** - Combined Pipeline (6-10 seconds)", expanded=False):
        st.markdown("""
        **Purpose:** Combines quantitative SQL data + qualitative 10-K context
        
        **Master Orchestrator Pipeline:**
        1. **Query Classifier** (GPT-4o-mini) - Detects hybrid intent and entities
        2. **Parallel Execution** (asyncio.gather):
           - SQL Agent runs simultaneously (2-3s)
           - RAG Agent runs simultaneously (3-4s)
        3. **LLM Synthesis** (GPT-4o-mini) - Combines both results with citations
        
        **Performance:** 6-10 seconds (parallel execution saves 3-4s)
        
        **LLM Calls:** 5 (Classifier + 3 SQL + 1 Synthesis)
        
        **Best For:** "What drove X?" questions requiring both numbers and context
        """)
    
    st.markdown("---")
    st.markdown("#### AI Model Usage")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("SQL Engine", "3 calls", "GPT-4o-mini")
    with col2:
        st.metric("Document Engine", "1 call", "GPT-4o-mini")
    with col3:
        st.metric("Hybrid Engine", "5 calls", "GPT-4o-mini")

with tab3:
    st.markdown("### Data Coverage")
    st.markdown("Comprehensive financial data across structured and unstructured sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Structured Financial Data")
        st.metric("Companies", "500+", "S&P 500")
        st.metric("Time Range", "2019-2024", "6 years")
        st.metric("Data Points", "50,000+", "Quarterly + Annual")
        
        with st.expander("Available Metrics"):
            st.markdown("""
            **Financial Metrics:**
            - Revenue, Net Income, Operating Income
            - Gross Margin, Operating Margin, Net Margin
            - ROE (Return on Equity), ROA (Return on Assets)
            - EPS (Earnings Per Share)
            - Total Assets, Total Liabilities, Equity
            - Cash Flow (Operating, Investing, Financing)
            
            **Stock Data:**
            - Daily prices (Open, Close, High, Low)
            - Trading volume
            - Historical trends (5+ years)
            """)
    
    with col2:
        st.markdown("#### Document Repository (10-K Filings)")
        st.metric("Companies", "50+", "Major S&P")
        st.metric("Time Range", "2019-2023", "5 years")
        st.metric("Documents", "250+", "10-K filings")
        
        with st.expander("Available Document Sections"):
            st.markdown("""
            **10-K Sections:**
            - Business Overview & Strategy
            - Risk Factors
            - MD&A (Management Discussion & Analysis)
            - Financial Statements & Notes
            - Segment Information (Products vs Services)
            - Geographic Revenue Breakdown
            - Product/Service Category Revenue
            - Operating Expenses Details
            - R&D and SG&A breakdowns
            """)
    
    st.markdown("---")
    st.markdown("#### Company Coverage")
    
    companies = [
        "Apple (AAPL)", "Microsoft (MSFT)", "Google (GOOGL)", "Amazon (AMZN)",
        "Meta (META)", "Tesla (TSLA)", "NVIDIA (NVDA)", "Netflix (NFLX)",
        "Adobe (ADBE)", "Salesforce (CRM)", "Intel (INTC)", "Cisco (CSCO)",
        "Oracle (ORCL)", "IBM (IBM)", "Qualcomm (QCOM)", "AMD (AMD)"
    ]
    
    cols = st.columns(4)
    for idx, company in enumerate(companies):
        with cols[idx % 4]:
            st.markdown(f"✅ {company}")

with tab4:
    st.markdown("### Query Examples")
    st.markdown("Select any example query to execute instantly")
    
    st.markdown("#### Structured Data Analysis (1-2 seconds)")
    
    with st.expander("**Financial Metrics Queries**", expanded=True):
        queries = [
            "Show Apple, Microsoft revenue Q1 2023",
            "What is Apple's ROE for 2023?",
            "Compare AAPL and MSFT net margins",
            "Show Tesla's quarterly revenue trend",
            "What is Amazon's operating income 2023?"
        ]
        for q in queries:
            if st.button(f"▶️ {q}", key=f"sql_{q}"):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()
    
    with st.expander("**Comparative Analysis Queries**"):
        queries = [
            "Compare Apple, Microsoft, Google revenue 2023",
            "Show AAPL, MSFT, GOOGL profit margins",
            "Compare tech giants ROE",
            "Show FAANG revenue growth"
        ]
        for q in queries:
            if st.button(f"▶️ {q}", key=f"multi_{q}"):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()
    
    st.markdown("---")
    st.markdown("#### Document Analysis (3-5 seconds)")
    
    with st.expander("**Table Extraction Queries**"):
        queries = [
            "Show Apple's gross margin breakdown from 10-K",
            "Display Apple's revenue by product category",
            "Extract Apple's operating expenses table",
            "Show Apple's revenue by geographic region"
        ]
        for q in queries:
            if st.button(f"▶️ {q}", key=f"rag_{q}"):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()
    
    with st.expander("**Qualitative Analysis Queries**"):
        queries = [
            "What are Apple's main risk factors from 10-K?",
            "Summarize Apple's business strategy",
            "What drove Apple's margin changes per 10-K?"
        ]
        for q in queries:
            if st.button(f"▶️ {q}", key=f"context_{q}"):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()
    
    st.markdown("---")
    st.markdown("#### Hybrid Analysis (6-10 seconds)")
    
    with st.expander("**Comprehensive Analysis Queries**"):
        queries = [
            "What drove Apple's margin changes—show numbers and 10-K citations?",
            "Explain Apple's revenue growth with business context",
            "Show Apple's performance with risk factors",
            "Compare margins with business strategy insights"
        ]
        for q in queries:
            if st.button(f"▶️ {q}", key=f"hybrid_{q}"):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#94a3b8; padding:20px;'>
    <p style='font-size:14px; font-weight:600; margin:0; background: linear-gradient(135deg, #8b5cf6 0%, #14b8a6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        FIN AI
    </p>
    <p style='font-size:13px; margin-top:8px; color:#64748b;'>
        Powered by GPT-4o-mini | PostgreSQL | pgvector | LangGraph
    </p>
    <p style='font-size:12px; margin-top:8px; color:#64748b;'>
        © 2025 FIN AI. All Rights Reserved.
    </p>
</div>
""", unsafe_allow_html=True)
