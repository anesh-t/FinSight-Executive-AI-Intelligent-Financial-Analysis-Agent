"""
Enhanced RAG Agent - Integrates 8 advanced capabilities
"""

import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / '2_retrieval'))
sys.path.insert(0, str(Path(__file__).parent.parent / '3_generation'))

from classifiers.enhanced_classifier import EnhancedQueryClassifier, CapabilityType
from prompts.enhanced_prompts import select_enhanced_prompt

# Import existing RAG components
from semantic_retriever import SemanticRetriever
from context_builder import ContextBuilder
from response_generator import ResponseGenerator


@dataclass
class EnhancedResult:
    """Enhanced result with capability metadata"""
    answer: str
    capability: str
    confidence: float
    entities: dict
    sources: list
    success: bool
    
    def __str__(self):
        return f"EnhancedResult(capability={self.capability}, confidence={self.confidence:.2f})"


class EnhancedRAGAgent:
    """
    Enhanced RAG Agent with 8 advanced capabilities.
    
    Capabilities:
    1. Financial Extraction
    2. Disclosure Summarization  
    3. Historical Comparison (Phase 2)
    4. Peer Benchmarking (Phase 3)
    5. Sentiment Analysis (Phase 3)
    6. Compliance Review
    7. Board Briefing
    8. ESG & Regulatory
    """
    
    def __init__(self, verbose: bool = False, use_quick_mode: bool = True):
        """
        Initialize enhanced RAG agent
        
        Args:
            verbose: Print debug info
            use_quick_mode: Use quick prompts for faster responses (default: True)
        """
        self.verbose = verbose
        self.use_quick_mode = use_quick_mode
        
        if self.verbose:
            print("🚀 Initializing Enhanced RAG Agent...")
        
        # Initialize components
        self.classifier = EnhancedQueryClassifier()
        self.retriever = SemanticRetriever()
        self.context_builder = ContextBuilder()
        self.generator = ResponseGenerator(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=1024  # Reduced from 2048 for faster responses
        )
        
        if self.verbose:
            print("✅ Enhanced RAG Agent ready!")
            print(f"   Capabilities: 8 (4 active, 4 coming soon)")
        print()
    
    def query(self, question: str, top_k: int = 3) -> EnhancedResult:  # Reduced from 5 to 3
        """
        Process query with enhanced capabilities.
        
        Args:
            question: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            EnhancedResult with answer and metadata
        """
        try:
            # Step 1: Classify query
            if self.verbose:
                print(f"📝 Query: {question}")
                print(f"🎯 Classifying query...")
            
            classification = self.classifier.classify(question)
            
            if self.verbose:
                print(f"   Capability: {classification.capability.value}")
                print(f"   Confidence: {classification.confidence:.2f}")
                print(f"   Entities: {classification.entities}")
                print()
            
            # Step 2: Retrieve relevant context
            if self.verbose:
                print(f"🔍 Retrieving context...")
            
            # Extract filters from entities
            companies = classification.entities.get('companies', None)
            years = classification.entities.get('years', None)
            
            # Map company names to proper format
            if companies:
                company_map = {
                    'Apple': 'Apple',
                    'Microsoft': 'Microsoft', 
                    'Google': 'Alphabet',  # Google -> Alphabet
                    'Amazon': 'Amazon',
                    'Meta': 'Meta'
                }
                companies = [company_map.get(c, c) for c in companies]
            
            chunks = self.retriever.retrieve(
                query=question,
                top_k=top_k,
                companies=companies if companies else None,
                years=years if years else None
            )
            
            if self.verbose:
                print(f"   Retrieved: {len(chunks)} chunks")
                if chunks:
                    print(f"   Top match: {chunks[0].company_name} {chunks[0].fiscal_year} - {chunks[0].section}")
                print()
            
            # Step 3: Build context (optimized for speed)
            context = self.context_builder.build_context(
                chunks=chunks,
                include_metadata=True,
                include_citations=True,
                format_style="compact"  # Changed from "detailed" to "compact" for speed
            )
            
            # Step 4: Select appropriate prompt
            capability_type = classification.capability.value
            
            # Check if capability is implemented
            implemented_capabilities = [
                'financial_extraction',
                'disclosure_summary',
                'board_briefing',
                'esg_regulatory'
            ]
            
            if capability_type not in implemented_capabilities:
                if self.verbose:
                    print(f"⚠️  Capability '{capability_type}' not yet implemented")
                    print(f"   Falling back to disclosure_summary")
                capability_type = 'disclosure_summary'
            
            # Step 5: Generate response
            if self.verbose:
                print(f"🤖 Generating response with {capability_type}...")
            
            # Import CFO system message and prompts
            from cfo_prompts import CFO_SYSTEM_MESSAGE
            from prompts.enhanced_prompts import select_enhanced_prompt
            
            # Get the appropriate prompt (quick or detailed)
            if self.use_quick_mode:
                from prompts.quick_prompts import select_quick_prompt
                prompt_template = select_quick_prompt(capability_type)
                if self.verbose:
                    print(f"   Using QUICK mode for faster response")
            else:
                prompt_template = select_enhanced_prompt(capability_type)
                if self.verbose:
                    print(f"   Using DETAILED mode")
            
            # Format prompt with context
            formatted_prompt = prompt_template.format(
                context=context.formatted_context,
                query=question
            )
            
            # Generate using LLM client
            llm_response = self.generator.llm_client.generate(
                prompt=formatted_prompt,
                system_message=CFO_SYSTEM_MESSAGE
            )
            
            if self.verbose:
                print(f"✅ Response generated")
                print(f"   Tokens: {llm_response.total_tokens}")
                print(f"   Cost: ${llm_response.cost:.4f}")
                print()
            
            return EnhancedResult(
                answer=llm_response.text,
                capability=capability_type,
                confidence=classification.confidence,
                entities=classification.entities,
                sources=[f"{c.company_name} {c.fiscal_year} - {c.section}" for c in chunks[:3]],
                success=True
            )
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            if self.verbose:
                print(f"❌ {error_msg}")
            
            return EnhancedResult(
                answer=error_msg,
                capability='error',
                confidence=0.0,
                entities={},
                sources=[],
                success=False
            )
    
    def close(self):
        """Close database connections"""
        if hasattr(self.retriever, 'conn'):
            self.retriever.conn.close()
            if self.verbose:
                print("🔌 Database connection closed")


if __name__ == "__main__":
    # Test the enhanced agent
    print("="*80)
    print("TESTING ENHANCED RAG AGENT")
    print("="*80)
    print()
    
    agent = EnhancedRAGAgent(verbose=True)
    
    # Test queries for each capability
    test_queries = [
        # Disclosure Summary
        "Summarize all major risk factors for Apple in 2022",
        
        # ESG & Regulatory
        "What are Apple's ESG commitments in 2022?",
        
        # Board Briefing
        "Create a board briefing from Apple's 2022 10-K",
        
        # Financial Extraction
        "What was Apple's cash flow in 2022?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}")
        print(f"{'='*80}\n")
        
        result = agent.query(query)
        
        print(f"Capability: {result.capability}")
        print(f"Success: {result.success}")
        print(f"\nAnswer Preview:")
        print(result.answer[:500] + "..." if len(result.answer) > 500 else result.answer)
        print()
    
    agent.close()
    
    print("="*80)
    print("TESTING COMPLETE")
    print("="*80)
