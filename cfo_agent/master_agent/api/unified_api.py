"""
Unified CFO Agent API - Single entry point for all queries
Handles both structured and unstructured data queries seamlessly
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import MasterOrchestrator, OrchestratedResponse
from core.response_synthesizer import ResponseSynthesizer


@dataclass
class UnifiedResponse:
    """User-facing response from unified agent"""
    answer: str
    intent: str
    data_sources: list
    latency: float
    metadata: Dict[str, Any]
    success: bool


class UnifiedCFOAgent:
    """
    Unified CFO Agent - Master-level AI assistant
    
    Handles:
    - Qualitative analysis (10-K filings via RAG)
    - Quantitative analysis (financial data via SQL)
    - Hybrid analysis (both combined)
    
    Usage:
        agent = UnifiedCFOAgent(verbose=False)
        result = agent.query("How did supply chain risks affect Apple's margins?")
        print(result.answer)
        agent.close()
    """
    
    def __init__(self, verbose: bool = False, use_quick_mode: bool = True):
        """
        Initialize unified CFO agent
        
        Args:
            verbose: Print debug/progress messages
            use_quick_mode: Use quick mode for faster RAG responses (default: True)
        """
        self.verbose = verbose
        self.use_quick_mode = use_quick_mode
        self.orchestrator = MasterOrchestrator(verbose=verbose, use_quick_mode=use_quick_mode)
        self.synthesizer = ResponseSynthesizer()
        
        if verbose:
            print("="*80)
            print("🚀 UNIFIED CFO AGENT INITIALIZED")
            print("="*80)
            print("Capabilities:")
            print("  ✅ Qualitative analysis (10-K filings)")
            print("  ✅ Quantitative analysis (financial data)")
            print("  ✅ Hybrid analysis (combined insights)")
            print("="*80)
    
    def query(self, question: str, session_id: str = "default") -> UnifiedResponse:
        """
        Query the unified CFO agent
        
        Args:
            question: User question (natural language)
            session_id: Session identifier (for SQL agent context)
            
        Returns:
            UnifiedResponse with comprehensive answer
            
        Examples:
            # Qualitative
            result = agent.query("What are Apple's top risks?")
            
            # Quantitative
            result = agent.query("What was Apple's revenue in 2022?")
            
            # Hybrid
            result = agent.query("How did risks affect Apple's margins?")
        """
        start_time = time.time()
        
        try:
            # Step 1: Orchestrate query (routing + execution)
            orchestrated = self.orchestrator.query(question, session_id)
            
            if not orchestrated.success:
                error_details = "Unknown error"
                if orchestrated.rag_response and not orchestrated.rag_response.success:
                    error_details = f"RAG Error: {orchestrated.rag_response.error}"
                if orchestrated.sql_response and not orchestrated.sql_response.success:
                    error_details = f"SQL Error: {orchestrated.sql_response.error}"
                
                return UnifiedResponse(
                    answer=f"Unable to process query. Error: {error_details}",
                    intent=orchestrated.intent if hasattr(orchestrated, 'intent') else "unknown",
                    data_sources=[],
                    latency=time.time() - start_time,
                    metadata={'error': error_details, 'orchestration': orchestrated.metadata if hasattr(orchestrated, 'metadata') else {}},
                    success=False
                )
            
            # Step 2: Synthesize response
            synthesized = self.synthesizer.synthesize(
                rag_response=orchestrated.rag_response,
                sql_response=orchestrated.sql_response,
                question=question,
                intent=orchestrated.intent
            )
            
            # Step 3: Build user-facing response
            total_latency = time.time() - start_time
            
            # Determine data sources used
            data_sources = []
            if synthesized.has_qualitative:
                data_sources.append("10-K Filings (RAG)")
            if synthesized.has_quantitative:
                data_sources.append("Financial Database (SQL)")
            
            return UnifiedResponse(
                answer=synthesized.text,
                intent=orchestrated.intent,
                data_sources=data_sources,
                latency=total_latency,
                metadata={
                    'orchestration': orchestrated.metadata,
                    'synthesis': {
                        'deduplicated': synthesized.deduplicated,
                        'citations': synthesized.citations
                    },
                    'agents_used': orchestrated.agents_used
                },
                success=True
            )
            
        except Exception as e:
            return UnifiedResponse(
                answer=f"Error processing query: {str(e)}",
                intent="error",
                data_sources=[],
                latency=time.time() - start_time,
                metadata={'error': str(e)},
                success=False
            )
    
    def close(self):
        """Close all connections"""
        self.orchestrator.close()


# Convenience function
def ask_cfo_agent(question: str, verbose: bool = False) -> str:
    """
    Quick query to CFO agent
    
    Args:
        question: User question
        verbose: Print debug info
        
    Returns:
        Answer string
    """
    agent = UnifiedCFOAgent(verbose=verbose)
    result = agent.query(question)
    agent.close()
    return result.answer


if __name__ == "__main__":
    # Demo usage
    print("\n" + "="*80)
    print("🎯 UNIFIED CFO AGENT - DEMO")
    print("="*80)
    
    agent = UnifiedCFOAgent(verbose=True)
    
    # Test queries
    demo_queries = [
        {
            'question': "What are Apple's top cybersecurity risks in 2022?",
            'type': 'Qualitative (RAG only)'
        },
        {
            'question': "What was Apple's revenue in 2022?",
            'type': 'Quantitative (SQL only)'
        },
        {
            'question': "How did supply chain risks affect Apple's profit margins in 2022?",
            'type': 'Hybrid (RAG + SQL)'
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{'='*80}")
        print(f"DEMO {i}: {demo['type']}")
        print(f"{'='*80}")
        print(f"\n❓ Question: {demo['question']}\n")
        
        result = agent.query(demo['question'])
        
        print(f"✅ Intent: {result.intent}")
        print(f"⏱️  Latency: {result.latency:.2f}s")
        print(f"📚 Sources: {', '.join(result.data_sources)}")
        print(f"\n📊 Answer:\n")
        print(result.answer[:500] + "...\n")
        
        # Wait between queries
        if i < len(demo_queries):
            time.sleep(2)
    
    agent.close()
    
    print("\n" + "="*80)
    print("✅ Demo complete!")
    print("="*80)
    print("\nUsage:")
    print("  from master_agent import UnifiedCFOAgent")
    print("  agent = UnifiedCFOAgent()")
    print("  result = agent.query('Your question here')")
    print("  print(result.answer)")
    print("  agent.close()")
    print("="*80 + "\n")
