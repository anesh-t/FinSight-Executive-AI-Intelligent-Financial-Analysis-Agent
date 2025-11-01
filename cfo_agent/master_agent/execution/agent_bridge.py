"""
Agent Bridge - Interface to existing RAG and SQL agents
Provides a clean abstraction without modifying existing systems
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class AgentResponse:
    """Standardized response from any agent"""
    text: str
    agent_type: str  # 'RAG' or 'SQL'
    metadata: Dict[str, Any]
    latency: float
    success: bool
    error: Optional[str] = None


class RAGAgentBridge:
    """Bridge to RAG system with enhanced capabilities"""
    
    def __init__(self, verbose: bool = False, use_enhanced: bool = True, use_quick_mode: bool = True):
        """
        Initialize RAG agent bridge
        
        Args:
            verbose: Print debug info
            use_enhanced: Use enhanced agent with 8 capabilities (default: True)
            use_quick_mode: Use quick mode for faster responses (default: True)
        """
        self.verbose = verbose
        self.use_enhanced = use_enhanced
        self.use_quick_mode = use_quick_mode
        self._agent = None
        
    def _init_agent(self):
        """Lazy initialization of RAG agent"""
        if self._agent is None:
            # Add rag_system paths to sys.path
            rag_root = Path(__file__).parent.parent.parent / 'rag_system'
            rag_generation = rag_root / '3_generation'
            rag_enhanced = rag_root / '4_enhanced_capabilities'
            
            # Add paths
            sys.path.insert(0, str(rag_enhanced))
            sys.path.insert(0, str(rag_generation))
            sys.path.insert(0, str(rag_root))
            
            if self.use_enhanced:
                # Use enhanced agent with 8 capabilities
                from enhanced_rag_agent import EnhancedRAGAgent
                self._agent = EnhancedRAGAgent(verbose=self.verbose, use_quick_mode=self.use_quick_mode)
                if self.verbose:
                    mode = "Quick Mode" if self.use_quick_mode else "Detailed Mode"
                    print(f"✅ Enhanced RAG Agent Bridge initialized (8 capabilities, {mode})")
            else:
                # Use original RAG agent
                from rag_agent import RAGAgent
                self._agent = RAGAgent(verbose=self.verbose)
                if self.verbose:
                    print("✅ RAG Agent Bridge initialized")
    
    def query(self, question: str, **kwargs) -> AgentResponse:
        """
        Query RAG agent
        
        Args:
            question: User question
            **kwargs: Additional arguments for RAG agent
            
        Returns:
            AgentResponse with RAG result
        """
        try:
            self._init_agent()
            
            start_time = time.time()
            
            # Call RAG agent (works with both original and enhanced)
            result = self._agent.query(question, **kwargs)
            
            latency = time.time() - start_time
            
            # Handle both original and enhanced result formats
            if self.use_enhanced and hasattr(result, 'answer'):
                # Enhanced agent result
                return AgentResponse(
                    text=result.answer,
                    agent_type='RAG',
                    metadata={
                        'capability': result.capability,
                        'confidence': result.confidence,
                        'entities': result.entities,
                        'sources': result.sources
                    },
                    latency=latency,
                    success=result.success
                )
            else:
                # Original agent result
                return AgentResponse(
                    text=result.text,
                    agent_type='RAG',
                    metadata=result.metadata,
                    latency=latency,
                    success=True
                )
            
        except Exception as e:
            return AgentResponse(
                text="",
                agent_type='RAG',
                metadata={},
                latency=0,
                success=False,
                error=str(e)
            )
    
    def close(self):
        """Close RAG agent connection"""
        if self._agent:
            self._agent.close()


class SQLAgentBridge:
    """Bridge to SQL system (NO changes to existing SQL system)"""
    
    def __init__(self, verbose: bool = False):
        """Initialize SQL agent bridge"""
        self.verbose = verbose
        self._graph = None
        
    def _init_agent(self):
        """Lazy initialization of SQL agent (LangGraph)"""
        if self._graph is None:
            # Add main cfo_agent directory to path
            main_path = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(main_path))
            
            # Import the existing LangGraph workflow
            from graph import cfo_agent_graph
            
            self._graph = cfo_agent_graph
            
            if self.verbose:
                print("✅ SQL Agent Bridge initialized (LangGraph)")
    
    async def query_async(self, question: str, session_id: str = "default", **kwargs) -> AgentResponse:
        """
        Query SQL agent asynchronously
        
        Args:
            question: User question
            session_id: Session identifier
            **kwargs: Additional arguments
            
        Returns:
            AgentResponse with SQL result
        """
        try:
            self._init_agent()
            
            start_time = time.time()
            
            # Call the run method of CFOAgentGraph (not ainvoke directly)
            response_text = await self._graph.run(question, session_id)
            
            latency = time.time() - start_time
            
            # Build metadata
            metadata = {
                'session_id': session_id,
                'execution_time': latency,
            }
            
            return AgentResponse(
                text=response_text,
                agent_type='SQL',
                metadata=metadata,
                latency=latency,
                success=True
            )
            
        except Exception as e:
            import traceback
            return AgentResponse(
                text="",
                agent_type='SQL',
                metadata={'error_trace': traceback.format_exc()},
                latency=0,
                success=False,
                error=str(e)
            )
    
    def query(self, question: str, **kwargs) -> AgentResponse:
        """
        Query SQL agent (synchronous wrapper)
        
        Args:
            question: User question
            **kwargs: Additional arguments
            
        Returns:
            AgentResponse with SQL result
        """
        import asyncio
        
        try:
            # Check if we're already in an async context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context, create a task and wait for it
                # This will be called from asyncio.to_thread, so we can use synchronous waiting
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(lambda: asyncio.run(self.query_async(question, **kwargs)))
                    return future.result()
            except RuntimeError:
                # No running loop, we can safely use asyncio.run
                return asyncio.run(self.query_async(question, **kwargs))
        except Exception as e:
            # Fallback error response
            import traceback
            return AgentResponse(
                text="",
                agent_type='SQL',
                metadata={'error_trace': traceback.format_exc()},
                latency=0,
                success=False,
                error=f"SQL Bridge error: {str(e)}"
            )
    
    def close(self):
        """Close SQL agent connection"""
        # LangGraph handles its own cleanup
        pass


class AgentCoordinator:
    """Coordinates multiple agents"""
    
    def __init__(self, verbose: bool = False, use_quick_mode: bool = True):
        """Initialize agent coordinator"""
        self.verbose = verbose
        self.use_quick_mode = use_quick_mode
        self.rag_bridge = RAGAgentBridge(verbose=verbose, use_quick_mode=use_quick_mode)
        self.sql_bridge = SQLAgentBridge(verbose=verbose)
    
    def query_rag(self, question: str, **kwargs) -> AgentResponse:
        """Query RAG agent"""
        return self.rag_bridge.query(question, **kwargs)
    
    def query_sql(self, question: str, **kwargs) -> AgentResponse:
        """Query SQL agent"""
        return self.sql_bridge.query(question, **kwargs)
    
    def query_both(self, question: str, **kwargs) -> Dict[str, AgentResponse]:
        """Query both agents (sequential for now, will parallelize later)"""
        rag_response = self.query_rag(question, **kwargs)
        sql_response = self.query_sql(question, **kwargs)
        
        return {
            'rag': rag_response,
            'sql': sql_response
        }
    
    def close(self):
        """Close all agent connections"""
        self.rag_bridge.close()
        self.sql_bridge.close()


if __name__ == "__main__":
    # Test the bridge
    print("="*80)
    print("AGENT BRIDGE TEST")
    print("="*80)
    
    coordinator = AgentCoordinator(verbose=True)
    
    # Test RAG
    print("\n" + "="*80)
    print("TEST 1: RAG Agent")
    print("="*80)
    rag_result = coordinator.query_rag("What are Apple's top risks in 2022?")
    print(f"Success: {rag_result.success}")
    print(f"Latency: {rag_result.latency:.2f}s")
    print(f"Preview: {rag_result.text[:200]}...")
    
    # Test SQL
    print("\n" + "="*80)
    print("TEST 2: SQL Agent")
    print("="*80)
    sql_result = coordinator.query_sql("What was Apple's revenue in 2022?")
    print(f"Success: {sql_result.success}")
    print(f"Latency: {sql_result.latency:.2f}s")
    print(f"Response: {sql_result.text}")
    
    # Test both
    print("\n" + "="*80)
    print("TEST 3: Both Agents")
    print("="*80)
    both_results = coordinator.query_both("How did risks affect margins?")
    print(f"RAG Success: {both_results['rag'].success}")
    print(f"SQL Success: {both_results['sql'].success}")
    print(f"Combined Latency: {both_results['rag'].latency + both_results['sql'].latency:.2f}s")
    
    coordinator.close()
    
    print("\n✅ Bridge test complete!")
