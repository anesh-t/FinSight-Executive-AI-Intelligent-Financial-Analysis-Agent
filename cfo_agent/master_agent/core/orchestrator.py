"""
Master Orchestrator - Coordinates RAG and SQL agents for hybrid queries
Handles routing, parallel execution, and result aggregation
"""

import sys
from pathlib import Path
import asyncio
import time
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from routing.query_classifier import QueryClassifier, QueryIntent
from execution.agent_bridge import AgentCoordinator, AgentResponse


@dataclass
class OrchestratedResponse:
    """Complete response from orchestrator"""
    text: str
    intent: str
    agents_used: List[str]
    rag_response: Optional[AgentResponse]
    sql_response: Optional[AgentResponse]
    total_latency: float
    metadata: Dict[str, Any]
    success: bool


class MasterOrchestrator:
    """Orchestrates RAG and SQL agents for comprehensive CFO analysis"""
    
    def __init__(self, verbose: bool = False, use_quick_mode: bool = True):
        """
        Initialize master orchestrator
        
        Args:
            verbose: Print progress messages
            use_quick_mode: Use quick mode for faster RAG responses (default: True)
        """
        self.verbose = verbose
        self.use_quick_mode = use_quick_mode
        
        # Initialize components
        self.classifier = QueryClassifier()
        self.coordinator = AgentCoordinator(verbose=verbose, use_quick_mode=use_quick_mode)
        
        # Initialize LLM for synthesis (using gpt-5.1 for best quality)
        # Increased max_completion_tokens for comprehensive multi-company analysis
        self.llm = ChatOpenAI(model="gpt-5.1", temperature=0.0, streaming=False, max_completion_tokens=2000)
        
        if verbose:
            print("✅ Master Orchestrator initialized")
    
    async def query_async(self, question: str, session_id: str = "default") -> OrchestratedResponse:
        """
        Process query asynchronously with intelligent routing
        
        Args:
            question: User question
            session_id: Session identifier
            
        Returns:
            OrchestratedResponse with complete result
        """
        start_time = time.time()
        
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"🎯 MASTER ORCHESTRATOR - Processing Query")
            print(f"{'='*80}")
            print(f"Question: {question}")
        
        # Step 1: Classify query
        if self.verbose:
            print(f"\n📊 Step 1: Classifying query intent...")
        
        classification = self.classifier.classify(question)
        
        if self.verbose:
            print(f"   Intent: {classification.intent.value.upper()}")
            print(f"   Confidence: {classification.confidence:.0%}")
            print(f"   Data Sources: {', '.join(classification.data_sources)}")
            if classification.entities['companies']:
                print(f"   Companies: {', '.join(classification.entities['companies'])}")
            if classification.entities['years']:
                print(f"   Years: {', '.join(map(str, classification.entities['years']))}")
        
        # Step 2: Route to appropriate agent(s)
        if self.verbose:
            print(f"\n🚀 Step 2: Executing query...")
        
        rag_response = None
        sql_response = None
        agents_used = []
        
        # Handle out-of-scope questions
        if classification.intent == QueryIntent.OUT_OF_SCOPE:
            if self.verbose:
                print(f"   → Out of scope - providing direct answer")
            
            # Use LLM to provide a simple direct answer
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            
            simple_answer = f"Today's date is {current_date}."
            
            return OrchestratedResponse(
                text=simple_answer,
                intent=classification.intent.value,
                agents_used=['DIRECT'],
                rag_response=None,
                sql_response=None,
                total_latency=time.time() - start_time,
                metadata={'reasoning': classification.reasoning},
                success=True
            )
        
        if classification.intent == QueryIntent.QUALITATIVE:
            # RAG only
            if self.verbose:
                print(f"   → RAG Agent (qualitative analysis)")
            
            rag_response = self.coordinator.query_rag(question)
            agents_used.append('RAG')
            
            # Use RAG response as final response
            response_text = rag_response.text
            
        elif classification.intent == QueryIntent.QUANTITATIVE:
            # SQL only
            if self.verbose:
                print(f"   → SQL Agent (quantitative data)")
            
            sql_response = self.coordinator.query_sql(question, session_id=session_id)
            agents_used.append('SQL')
            
            # Use SQL response as final response
            response_text = sql_response.text
            
        else:  # HYBRID
            # Both agents - PARALLEL execution (optimized)
            if self.verbose:
                print(f"   → RAG + SQL Agents (parallel execution - optimized)")
            
            # Execute both in parallel for speed
            sql_task = asyncio.create_task(
                asyncio.to_thread(self.coordinator.query_sql, question, session_id=session_id)
            )
            rag_task = asyncio.create_task(
                asyncio.to_thread(self.coordinator.query_rag, question)
            )
            
            # Wait for both with timeout
            try:
                sql_response, rag_response = await asyncio.gather(sql_task, rag_task, return_exceptions=True)
                
                # Handle exceptions
                if isinstance(sql_response, Exception):
                    sql_response = AgentResponse(text="SQL data unavailable", success=False, latency=0.0)
                if isinstance(rag_response, Exception):
                    rag_response = AgentResponse(text="10-K insights unavailable", success=False, latency=0.0)
            except Exception as e:
                # Fallback to SQL only if parallel fails
                sql_response = await asyncio.to_thread(
                    self.coordinator.query_sql, question, session_id=session_id
                )
                rag_response = AgentResponse(text="10-K insights unavailable", success=False, latency=0.0)
            
            agents_used = ['RAG', 'SQL']
            
            # Synthesize responses (simple concatenation for now, will improve)
            if self.verbose:
                print(f"\n🔄 Step 3: Synthesizing results...")
            
            response_text = self._synthesize_simple(rag_response, sql_response, question)
        
        total_latency = time.time() - start_time
        
        if self.verbose:
            print(f"\n✅ Query complete!")
            print(f"   Total time: {total_latency:.2f}s")
            print(f"   Agents used: {', '.join(agents_used)}")
            if rag_response:
                print(f"   RAG latency: {rag_response.latency:.2f}s")
            if sql_response:
                print(f"   SQL latency: {sql_response.latency:.2f}s")
            print(f"{'='*80}\n")
        
        # Build metadata
        metadata = {
            'intent': classification.intent.value,
            'confidence': classification.confidence,
            'entities': classification.entities,
            'agents_used': agents_used,
            'total_latency': total_latency,
        }
        
        if rag_response:
            metadata['rag_latency'] = rag_response.latency
            metadata['rag_metadata'] = rag_response.metadata
        
        if sql_response:
            metadata['sql_latency'] = sql_response.latency
            metadata['sql_metadata'] = sql_response.metadata
        
        # Check success
        success = True
        if rag_response and not rag_response.success:
            success = False
        if sql_response and not sql_response.success:
            success = False
        
        return OrchestratedResponse(
            text=response_text,
            intent=classification.intent.value,
            agents_used=agents_used,
            rag_response=rag_response,
            sql_response=sql_response,
            total_latency=total_latency,
            metadata=metadata,
            success=success
        )
    
    def query(self, question: str, session_id: str = "default") -> OrchestratedResponse:
        """
        Process query synchronously
        
        Args:
            question: User question
            session_id: Session identifier
            
        Returns:
            OrchestratedResponse with complete result
        """
        return asyncio.run(self.query_async(question, session_id))
    
    def _synthesize_simple(
        self,
        rag_response: AgentResponse,
        sql_response: AgentResponse,
        question: str
    ) -> str:
        """
        LLM-powered synthesis of RAG and SQL responses
        
        Combines:
        1. Original question
        2. Structured data (SQL results)
        3. Unstructured insights (10-K context)
        
        Args:
            rag_response: Response from RAG agent
            sql_response: Response from SQL agent
            question: Original question
            
        Returns:
            Synthesized comprehensive answer
        """
        # Extract the data sources
        structured_data = sql_response.text if sql_response and sql_response.success else "No structured data available."
        unstructured_insights = rag_response.text if rag_response and rag_response.success else "No 10-K insights available."
        
        # Create optimized synthesis prompt for comprehensive multi-company analysis
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert CFO analyst. Synthesize structured financial data and 10-K insights to provide a comprehensive, well-organized answer.

CRITICAL FORMATTING RULES - DO NOT USE MARKDOWN TABLES:
- NEVER use vertical bars (|) or Markdown table syntax
- Use numbered lists, bullet points, and labeled sections instead
- Format metrics in clean blocks like:
  Gross Margin (2023): 44.1%
  Revenue: $383.3B
  Products GM: 36.5%
- Use bold labels for key metrics
- Use bullet points (•) for lists
- Use clear section headers with numbers (1., 2., 3.)
- Keep formatting simple and readable
- No ASCII tables, no pipes, no complex formatting"""),
            ("user", """Question: {question}

STRUCTURED DATA (SQL):
{structured_data}

UNSTRUCTURED INSIGHTS (10-K):
{unstructured_insights}

Provide a comprehensive answer that:
1. Directly answers the question with a brief summary
2. Presents ALL data in clean labeled format (NO TABLES, NO PIPES)
3. Uses numbered sections and bullet points
4. Explains key drivers/trends for EACH company mentioned
5. Combines quantitative data with qualitative insights
6. Highlights important patterns or differences across companies

Remember: Format like ChatGPT - clean, readable, NO Markdown tables!""")
        ])
        
        # Generate synthesis
        try:
            messages = synthesis_prompt.format_messages(
                question=question,
                structured_data=structured_data,
                unstructured_insights=unstructured_insights
            )
            
            response = self.llm.invoke(messages)
            synthesized_answer = response.content
            
            # Add source attribution
            sources = []
            if sql_response and sql_response.success:
                sources.append("Financial Database (SQL)")
            if rag_response and rag_response.success:
                sources.append("SEC 10-K Filings")
            
            if sources:
                synthesized_answer += f"\n\n**Sources:** {', '.join(sources)}"
            
            return synthesized_answer
            
        except Exception as e:
            # Fallback to simple concatenation if LLM synthesis fails
            if self.verbose:
                print(f"⚠️  LLM synthesis failed: {str(e)}, using fallback")
            
            parts = []
            parts.append(f"**Question:** {question}\n")
            
            if rag_response and rag_response.success:
                parts.append("\n**10-K Insights:**")
                parts.append(rag_response.text)
            
            if sql_response and sql_response.success:
                parts.append("\n**Financial Data:**")
                parts.append(sql_response.text)
            
            return "\n".join(parts)
    
    def close(self):
        """Close all connections"""
        self.coordinator.close()


# Convenience function
def orchestrate_query(question: str, verbose: bool = False) -> OrchestratedResponse:
    """Quick query orchestration"""
    orchestrator = MasterOrchestrator(verbose=verbose)
    result = orchestrator.query(question)
    orchestrator.close()
    return result


if __name__ == "__main__":
    # Test the orchestrator
    import sys
    
    print("="*80)
    print("🎯 MASTER ORCHESTRATOR TEST")
    print("="*80)
    
    orchestrator = MasterOrchestrator(verbose=True)
    
    test_queries = [
        # Qualitative (RAG only)
        "What are Apple's top risks in 2022?",
        
        # Quantitative (SQL only)
        "What was Apple's revenue in 2022?",
        
        # Hybrid (both)
        "How did supply chain risks affect Apple's margins in 2022?",
    ]
    
    for i, question in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}")
        print(f"{'='*80}")
        
        result = orchestrator.query(question)
        
        print(f"\n📊 RESULT:")
        print(f"Intent: {result.intent}")
        print(f"Agents: {', '.join(result.agents_used)}")
        print(f"Success: {result.success}")
        print(f"Latency: {result.total_latency:.2f}s")
        print(f"\nResponse Preview:")
        print(result.text[:300] + "...\n")
        
        # Wait a bit between queries
        if i < len(test_queries):
            time.sleep(1)
    
    orchestrator.close()
    
    print("\n✅ Orchestrator test complete!")
