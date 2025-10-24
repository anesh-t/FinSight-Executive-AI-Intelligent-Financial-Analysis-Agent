"""
CFO Intelligence Agent - LangGraph Implementation
Multi-node agent system for financial analysis with chain-of-thought reasoning
"""

import os
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator
import json
from database import SupabaseConnector
import pandas as pd


# Define the agent state
class AgentState(TypedDict):
    """State passed between nodes in the graph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    intent: str
    entities: dict
    sql_query: str
    data: pd.DataFrame
    analysis: str
    visualization_suggestion: str
    final_output: dict


class CFOAgentGraph:
    """
    LangGraph-based CFO Intelligence Agent with specialized nodes
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.llm = ChatOpenAI(
            model=os.getenv('LLM_MODEL', 'gpt-4o'),
            temperature=float(os.getenv('LLM_TEMPERATURE', 0.0))
        )
        self.db_connector = SupabaseConnector()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("intent_classifier", self.intent_classifier_node)
        workflow.add_node("entity_resolver", self.entity_resolver_node)
        workflow.add_node("data_retrieval", self.data_retrieval_node)
        workflow.add_node("reasoning_computation", self.reasoning_computation_node)
        workflow.add_node("output_visualization", self.output_visualization_node)
        
        # Define edges
        workflow.set_entry_point("intent_classifier")
        workflow.add_edge("intent_classifier", "entity_resolver")
        workflow.add_edge("entity_resolver", "data_retrieval")
        workflow.add_edge("data_retrieval", "reasoning_computation")
        workflow.add_edge("reasoning_computation", "output_visualization")
        workflow.add_edge("output_visualization", END)
        
        return workflow.compile()
    
    def intent_classifier_node(self, state: AgentState) -> AgentState:
        """
        NODE 1: Classify the user's intent
        """
        prompt = f"""
        You are a Financial Analyst AI. Classify the user question as one of the following:
        
        - "single_metric": Direct query for a single metric/ratio (e.g. "What was Apple's net margin in Q2 2023?")
        - "trend": Requests for trends or time series (e.g. "Show Microsoft's EPS since 2020")
        - "comparison": Ranking/benchmarking/peer comparison (e.g. "Who had the best ROE in 2022?")
        - "macro_overlay": Relates macro/event to company data (e.g. "How did inflation affect Amazon?")
        - "event_overlay": Company performance during an event (e.g. "Apple during Fed tightening")
        - "scenario": Hypotheticals or what-if (e.g. "If COGS rises 10%, what happens to margins?")
        - "other": Anything that doesn't fit
        
        User Question: {state['user_query']}
        
        Return ONLY the classification (one word).
        """
        
        response = self.llm.invoke(prompt)
        intent = response.content.strip().lower()
        
        if self.verbose:
            print(f"🎯 Intent Classified: {intent}")
        
        state['intent'] = intent
        state['messages'].append(AIMessage(content=f"Intent: {intent}"))
        
        return state
    
    def entity_resolver_node(self, state: AgentState) -> AgentState:
        """
        NODE 2: Extract entities (companies, metrics, time periods, etc.)
        """
        prompt = f"""
        You are a Financial Analyst AI. Given the user question, identify and return:
        - company name(s)/ticker(s) (resolve to actual names: Apple Inc., Microsoft Corporation, etc.)
        - time period(s) (fiscal_year, fiscal_quarter if present)
        - financial metric or ratio (revenue, net_income, roe, etc.)
        - macro indicator (GDP, CPI, Fed rate) if mentioned
        - event (COVID, AI boom, Fed tightening) if mentioned
        
        User Question: {state['user_query']}
        Intent: {state['intent']}
        
        Return as JSON:
        {{
          "companies": ["Apple Inc.", "Microsoft Corporation"],
          "metrics": ["revenue", "net_income"],
          "years": [2023],
          "quarters": [1, 2, 3, 4],
          "macros": ["cpi", "gdp_growth"],
          "events": ["COVID-19"]
        }}
        
        Return ONLY valid JSON, no explanation.
        """
        
        response = self.llm.invoke(prompt)
        
        try:
            entities = json.loads(response.content.strip())
        except:
            # Fallback parsing
            entities = {
                "companies": [],
                "metrics": [],
                "years": [],
                "quarters": [],
                "macros": [],
                "events": []
            }
        
        if self.verbose:
            print(f"🔍 Entities Resolved: {json.dumps(entities, indent=2)}")
        
        state['entities'] = entities
        state['messages'].append(AIMessage(content=f"Entities: {json.dumps(entities)}"))
        
        return state
    
    def data_retrieval_node(self, state: AgentState) -> AgentState:
        """
        NODE 3: Build and execute SQL query
        """
        entities = state['entities']
        intent = state['intent']
        
        prompt = f"""
        You are a SQL expert for a financial data warehouse. Generate a SQL query.
        
        Intent: {intent}
        Entities: {json.dumps(entities)}
        
        Available Views:
        - vw_company_summary: company_name, fiscal_year, fiscal_quarter, revenue, net_income, roe, roa, margins, stock data
        - vw_macro_overlay: company data + gdp_growth, cpi, unemployment_rate, fed_funds_rate, sp500_return
        - vw_event_timeline: company data + event_name, event_start_date, event_end_date
        
        Rules:
        1. Use LIKE '%CompanyName%' for company matching (e.g., LIKE '%Apple%')
        2. For quarterly data: SELECT company_name, fiscal_year, fiscal_quarter, revenue (NO aggregation)
        3. For annual totals: SELECT company_name, fiscal_year, SUM(revenue) as total_revenue GROUP BY company_name, fiscal_year
        4. For trends: ORDER BY fiscal_year, fiscal_quarter
        5. Always include fiscal_quarter in SELECT if showing quarterly breakdown
        6. If using GROUP BY, ensure all non-aggregated columns are in GROUP BY clause
        7. CRITICAL: When using OR for multiple companies, wrap in parentheses: (company_name LIKE '%Apple%' OR company_name LIKE '%Microsoft%')
        8. Always add year filter: AND fiscal_year = XXXX
        
        IMPORTANT: 
        - For "Show X revenue for 2023" → SELECT quarterly data WITHOUT SUM
        - For "Total revenue" or "Compare totals" → Use SUM with proper GROUP BY
        - For multiple companies: WHERE (company_name LIKE '%A%' OR company_name LIKE '%B%') AND fiscal_year = XXXX
        
        Generate ONLY the SQL query, no explanation.
        """
        
        response = self.llm.invoke(prompt)
        sql_query = response.content.strip()
        
        # Clean SQL
        if '```sql' in sql_query:
            sql_query = sql_query.split('```sql')[1].split('```')[0].strip()
        elif '```' in sql_query:
            sql_query = sql_query.split('```')[1].split('```')[0].strip()
        
        if self.verbose:
            print(f"📊 SQL Query Generated:\n{sql_query}")
        
        # Execute query
        try:
            df = self.db_connector.execute_query(sql_query)
            state['data'] = df
            state['sql_query'] = sql_query
            
            if self.verbose:
                print(f"✅ Data Retrieved: {len(df)} rows")
        except Exception as e:
            if self.verbose:
                print(f"❌ Query Failed: {e}")
            state['data'] = pd.DataFrame()
            state['sql_query'] = f"Failed: {str(e)}"
        
        state['messages'].append(AIMessage(content=f"SQL: {sql_query}"))
        
        return state
    
    def reasoning_computation_node(self, state: AgentState) -> AgentState:
        """
        NODE 4: Analyze data and generate insights
        """
        df = state['data']
        
        if df is None or df.empty:
            state['analysis'] = "No data available for analysis."
            return state
        
        # Calculate aggregations for accuracy
        aggregation_summary = ""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col not in ['fiscal_year', 'fiscal_quarter', 'company_id']]
        
        if len(df) > 1 and 'fiscal_quarter' in df.columns and numeric_cols:
            aggregation_summary = "\n**PRE-CALCULATED AGGREGATIONS (USE THESE EXACT NUMBERS):**\n"
            for col in numeric_cols[:5]:
                if col in ['revenue', 'total_revenue', 'net_income', 'operating_income', 'cash_flow_ops']:
                    total = df[col].sum()
                    aggregation_summary += f"- Total {col.replace('_', ' ')}: ${total/1_000_000_000:.2f}B (sum of all quarters)\n"
                elif col in ['roe', 'roa', 'gross_margin', 'operating_margin', 'net_margin']:
                    avg = df[col].mean()
                    aggregation_summary += f"- Average {col.replace('_', ' ')}: {avg*100:.2f}% (average across quarters)\n"
        
        data_markdown = df.head(15).to_markdown(index=False)
        
        prompt = f"""
        You are a CFO Analyst. Analyze this data and provide insights.
        
        User Question: {state['user_query']}
        Intent: {state['intent']}
        {aggregation_summary}
        
        Data:
        {data_markdown}
        
        Provide:
        1. **Executive Summary** (2-3 sentences with specific numbers and units)
        2. **Aggregated Data Table** (Markdown format)
        3. **Key Insights** (2-3 bullet points with YoY%, trends, rankings)
        4. **Financial Interpretation** (1 sentence on implications)
        
        Use proper financial notation ($B, $M, %, bps). Be analytical and data-driven.
        """
        
        response = self.llm.invoke(prompt)
        analysis = response.content
        
        if self.verbose:
            print(f"💡 Analysis Generated")
        
        state['analysis'] = analysis
        state['messages'].append(AIMessage(content=f"Analysis complete"))
        
        return state
    
    def output_visualization_node(self, state: AgentState) -> AgentState:
        """
        NODE 5: Format output and suggest visualizations
        """
        df = state['data']
        intent = state['intent']
        
        # Suggest visualization based on intent
        viz_suggestions = {
            'single_metric': 'Metric card with value',
            'trend': 'Line chart (X: time, Y: metric)',
            'comparison': 'Bar chart (X: company, Y: metric)',
            'macro_overlay': 'Dual-axis line chart (company metric + macro indicator)',
            'event_overlay': 'Timeline chart with event markers',
            'scenario': 'Side-by-side comparison table'
        }
        
        viz_suggestion = viz_suggestions.get(intent, 'Table view')
        
        # Calculate aggregations for executive summary
        aggregation_context = ""
        if not df.empty:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            numeric_cols = [col for col in numeric_cols if col not in ['fiscal_year', 'fiscal_quarter', 'company_id']]
            
            if len(df) > 1 and 'fiscal_quarter' in df.columns and numeric_cols:
                aggregation_context = "\n\n**CALCULATED TOTALS (USE THESE):**\n"
                for col in numeric_cols[:3]:
                    if col in ['revenue', 'net_income', 'operating_income', 'total_revenue']:
                        total = df[col].sum()
                        aggregation_context += f"- Total {col}: ${total/1_000_000_000:.2f}B (sum of all quarters)\n"
        
        # Create executive summary with aggregations
        summary_prompt = f"""
        Create a 1-2 sentence executive summary.
        
        Question: {state['user_query']}
        {aggregation_context}
        
        Quarterly Data:
        {df.head(5).to_markdown(index=False) if not df.empty else 'No data'}
        
        CRITICAL: If showing quarterly data, use the CALCULATED TOTALS above for annual figures.
        Include specific numbers with units ($B, %). Be accurate.
        """
        
        summary_response = self.llm.invoke(summary_prompt)
        executive_summary = summary_response.content
        
        # Compile final output
        state['final_output'] = {
            'status': 'success' if not df.empty else 'error',
            'summary': executive_summary,
            'narrative': state['analysis'],
            'data': df,
            'sql_query': state['sql_query'],
            'visualization': viz_suggestion,
            'intent': intent,
            'query': state['user_query']
        }
        
        if self.verbose:
            print(f"📈 Visualization Suggested: {viz_suggestion}")
            print(f"✅ Output Complete")
        
        return state
    
    def analyze(self, query: str) -> dict:
        """
        Main entry point - run the full graph
        """
        initial_state = {
            'messages': [HumanMessage(content=query)],
            'user_query': query,
            'intent': '',
            'entities': {},
            'sql_query': '',
            'data': pd.DataFrame(),
            'analysis': '',
            'visualization_suggestion': '',
            'final_output': {}
        }
        
        try:
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            return final_state['final_output']
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Agent execution failed: {str(e)}",
                'query': query
            }
