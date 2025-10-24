"""
LangGraph state machine for CFO Agent
"""
from typing import TypedDict, List, Dict, Annotated
import operator
import copy
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

from decomposer import QueryDecomposer
from router import IntentRouter
from planner import TaskPlanner
from sql_builder import SQLBuilder
from sql_exec import SQLExecutor
from citations import CitationFetcher
from formatter import ResponseFormatter
from memory import session_memory
from hitl import hitl_gate


class AgentState(TypedDict):
    """State passed between nodes"""
    # Input
    question: str
    session_id: str
    
    # Decomposition
    decomposed: Dict
    tasks: List[Dict]
    greeting: str
    
    # Routing & Planning
    routed_tasks: List[Dict]
    plans: List[Dict]
    
    # Execution
    results: List[Dict]
    sql_executed: List[str]
    params_used: List[Dict]
    
    # Citations & Formatting
    citations: List[Dict]
    formatted_responses: List[str]
    
    # Final output
    final_response: str
    
    # Metadata
    errors: Annotated[List[str], operator.add]
    is_generative: bool


class CFOAgentGraph:
    """LangGraph-based CFO Intelligence Agent"""
    
    def __init__(self):
        self.decomposer = QueryDecomposer()
        self.router = IntentRouter()
        self.planner = TaskPlanner()
        self.sql_builder = SQLBuilder()
        self.sql_executor = SQLExecutor()
        self.citation_fetcher = CitationFetcher()
        self.formatter = ResponseFormatter()
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("decompose", self.decompose_node)
        workflow.add_node("resolve_entities", self.resolve_entities_node)
        workflow.add_node("run_tasks", self.run_tasks_node)
        workflow.add_node("fetch_citations", self.fetch_citations_node)
        workflow.add_node("format_response", self.format_response_node)
        workflow.add_node("update_memory", self.update_memory_node)
        
        # Define edges
        workflow.set_entry_point("decompose")
        workflow.add_edge("decompose", "resolve_entities")
        workflow.add_edge("resolve_entities", "run_tasks")
        workflow.add_edge("run_tasks", "fetch_citations")
        workflow.add_edge("fetch_citations", "format_response")
        workflow.add_edge("format_response", "update_memory")
        workflow.add_edge("update_memory", END)
        
        return workflow.compile()
    
    async def decompose_node(self, state: AgentState) -> AgentState:
        """Node 1: Decompose question into tasks"""
        question = state['question']
        
        decomposed = await self.decomposer.decompose(question)
        
        state['decomposed'] = decomposed
        state['tasks'] = decomposed.get('tasks', [])
        state['greeting'] = decomposed.get('greeting', '')
        
        return state
    
    async def resolve_entities_node(self, state: AgentState) -> AgentState:
        """Node 2: Route tasks and resolve entities"""
        tasks = state['tasks']
        
        # Route tasks
        routed_tasks = self.router.route_all_tasks(tasks)
        
        # Plan tasks (includes entity resolution)
        plans = await self.planner.plan_all_tasks(routed_tasks)
        
        state['routed_tasks'] = routed_tasks
        state['plans'] = plans
        
        return state
    
    async def run_tasks_node(self, state: AgentState) -> AgentState:
        """Node 3: Execute SQL for each task"""
        plans = state['plans']
        
        results = []
        sql_executed = []
        params_used = []
        errors = []
        
        for plan in plans:
            try:
                # Check if this is a stock price query with multiple entities
                intent = plan.get('intent', '')
                entities_resolved = plan.get('entities_resolved', {})
                is_stock_query = intent in ['stock_price_annual', 'stock_price_quarterly']
                
                print(f"[DEBUG GRAPH] Intent: {intent}")
                print(f"[DEBUG GRAPH] Entities resolved: {entities_resolved}")
                print(f"[DEBUG GRAPH] Is stock query: {is_stock_query}")
                print(f"[DEBUG GRAPH] Num entities: {len(entities_resolved)}")
                
                if is_stock_query and len(entities_resolved) > 1:
                    print(f"[DEBUG GRAPH] Handling multi-company stock query with {len(entities_resolved)} entities")
                    # Handle multiple entities for stock queries
                    combined_results = []
                    all_sqls = []
                    all_params = []
                    
                    # Execute query for each entity
                    for entity, ticker in entities_resolved.items():
                        print(f"[DEBUG GRAPH] Processing entity: {entity} -> {ticker}")
                        if ticker:
                            # Create deep copy of plan with single entity
                            single_plan = copy.deepcopy(plan)
                            single_plan['entities_resolved'] = {entity: ticker}
                            
                            # CRITICAL: Update the ticker in params (params were pre-built with wrong ticker)
                            if 'params' in single_plan and 'ticker' in single_plan['params']:
                                single_plan['params']['ticker'] = ticker
                                print(f"[DEBUG GRAPH] Updated params ticker to: {ticker}")
                            
                            print(f"[DEBUG GRAPH] Single plan entities: {single_plan['entities_resolved']}")
                            print(f"[DEBUG GRAPH] Single plan params: {single_plan.get('params', {})}")
                            
                            # Build SQL for this entity
                            sql, params, is_generative = await self.sql_builder.build_sql(single_plan, use_generative=False)
                            
                            # HITL approval
                            approved, reason = await hitl_gate.approve_sql(sql, params, is_generative)
                            if not approved:
                                errors.append(f"HITL rejected for {ticker}: {reason}")
                                continue
                            
                            # Execute
                            entity_results = await self.sql_executor.execute(sql, params)
                            print(f"[DEBUG GRAPH] Got {len(entity_results)} results for {ticker}")
                            combined_results.extend(entity_results)
                            all_sqls.append(sql)
                            all_params.append(params)
                    
                    # Store combined results
                    print(f"[DEBUG GRAPH] Total combined results: {len(combined_results)}")
                    print(f"[DEBUG GRAPH] Combined tickers: {[r.get('ticker') for r in combined_results if 'ticker' in r]}")
                    results.append(combined_results)
                    sql_executed.append(" | ".join(all_sqls))
                    params_used.append(all_params[0] if all_params else {})
                else:
                    # Single entity or non-stock query - execute normally
                    # Build SQL (template-first)
                    sql, params, is_generative = await self.sql_builder.build_sql(plan, use_generative=False)
                    
                    # HITL approval
                    approved, reason = await hitl_gate.approve_sql(sql, params, is_generative)
                    if not approved:
                        errors.append(f"HITL rejected: {reason}")
                        continue
                    
                    # Execute
                    task_results = await self.sql_executor.execute(sql, params)
                    
                    results.append(task_results)
                    sql_executed.append(sql)
                    params_used.append(params)
                
            except Exception as e:
                errors.append(f"Task execution failed: {str(e)}")
                results.append([])
                sql_executed.append("")
                params_used.append({})
        
        state['results'] = results
        state['sql_executed'] = sql_executed
        state['params_used'] = params_used
        if errors:
            state['errors'] = errors
        
        return state
    
    async def fetch_citations_node(self, state: AgentState) -> AgentState:
        """Node 4: Fetch citations for results"""
        results = state['results']
        params_used = state['params_used']
        
        citations_list = []
        
        for result_set, params in zip(results, params_used):
            if result_set and params.get('ticker'):
                ticker = params['ticker']
                fy = params.get('fy')
                fq = params.get('fq')
                
                if fy:
                    citations = await self.citation_fetcher.fetch_citations(ticker, fy, fq)
                    citations_list.append(citations)
                else:
                    citations_list.append({})
            else:
                citations_list.append({})
        
        state['citations'] = citations_list
        
        return state
    
    async def format_response_node(self, state: AgentState) -> AgentState:
        """Node 5: Format responses with insights and citations"""
        results = state['results']
        plans = state['plans']
        citations_list = state['citations']
        greeting = state['greeting']
        question = state['question']
        
        formatted_responses = []
        
        for result_set, plan, citations in zip(results, plans, citations_list):
            if result_set:
                # Build context for formatter
                context = {
                    'intent': plan.get('intent'),
                    'params': plan.get('params', {}),
                    'question': question,  # Pass original question for selective display
                    'citation_line': self.citation_fetcher.format_citation_line(citations)
                }
                
                formatted = await self.formatter.format_response(result_set, context, citations)
                formatted_responses.append(formatted)
            else:
                formatted_responses.append("No results for this task.")
        
        # Combine all responses
        final_parts = []
        if greeting:
            final_parts.append(greeting)
        
        final_parts.extend(formatted_responses)
        
        state['formatted_responses'] = formatted_responses
        state['final_response'] = "\n\n---\n\n".join(final_parts)
        
        return state
    
    async def update_memory_node(self, state: AgentState) -> AgentState:
        """Node 6: Update session memory"""
        session_id = state.get('session_id', 'default')
        plans = state['plans']
        
        # Extract tickers and periods
        tickers = []
        periods = []
        surfaces = []
        
        for plan in plans:
            params = plan.get('params', {})
            if params.get('ticker'):
                tickers.append(params['ticker'])
            if params.get('t1'):
                tickers.append(params['t1'])
            if params.get('t2'):
                tickers.append(params['t2'])
            
            period = {
                'fy': params.get('fy'),
                'fq': params.get('fq'),
                'latest': params.get('latest', False)
            }
            periods.append(period)
            
            surfaces.extend(plan.get('surfaces', []))
        
        # Update memory
        if tickers:
            session_memory.update_tickers(session_id, tickers)
        if periods:
            session_memory.update_period(session_id, periods[-1])  # Last period
        if surfaces:
            session_memory.update_surfaces(session_id, list(set(surfaces)))
        
        session_memory.increment_query_count(session_id)
        
        return state
    
    async def run(self, question: str, session_id: str = "default") -> str:
        """
        Run the agent on a question
        
        Args:
            question: Natural language question
            session_id: Session identifier for memory
            
        Returns:
            Formatted response string
        """
        initial_state = {
            'question': question,
            'session_id': session_id,
            'errors': []
        }
        
        final_state = await self.graph.ainvoke(initial_state)
        
        return final_state.get('final_response', 'Error: No response generated')


# Global graph instance
cfo_agent_graph = CFOAgentGraph()
