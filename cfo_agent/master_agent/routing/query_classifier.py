"""
Query Classifier - Detect query intent and route to appropriate agent(s)
Classifies queries as: QUALITATIVE, QUANTITATIVE, or HYBRID
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class QueryIntent(Enum):
    """Query intent types"""
    QUALITATIVE = "qualitative"    # RAG only
    QUANTITATIVE = "quantitative"  # SQL only
    HYBRID = "hybrid"              # Both RAG + SQL


@dataclass
class QueryClassification:
    """Classified query with metadata"""
    query: str
    intent: QueryIntent
    confidence: float
    entities: Dict[str, any]
    data_sources: List[str]
    reasoning: str


class QueryClassifier:
    """Intelligent query classification"""
    
    # Keywords that indicate quantitative (SQL) queries
    QUANTITATIVE_KEYWORDS = {
        # Direct metrics
        'revenue', 'profit', 'income', 'earnings', 'sales',
        'margin', 'gross margin', 'operating margin', 'net margin',
        'assets', 'liabilities', 'equity', 'cash', 'debt',
        'ratio', 'p/e', 'price to earnings', 'roe', 'roa',
        'eps', 'earnings per share',
        
        # Financial questions
        'how much', 'what was', 'what is', 'show me',
        'calculate', 'compute', 'total', 'sum',
        'compare numbers', 'comparison of',
        
        # Stock/market data
        'stock price', 'share price', 'market cap',
        'dividend', 'yield', 'beta',
        
        # Temporal comparisons
        'growth rate', 'change from', 'increase', 'decrease',
        'trend in', 'over time', 'year over year', 'yoy',
        
        # Specific data requests
        'breakdown', 'by segment', 'by region', 'by product',
        'quarterly', 'annual', 'q1', 'q2', 'q3', 'q4',
    }
    
    # Keywords that indicate qualitative (RAG) queries
    QUALITATIVE_KEYWORDS = {
        # Risk and strategy
        'risk', 'risks', 'risk factors', 'challenges',
        'strategy', 'strategic', 'priorities', 'focus',
        'opportunity', 'opportunities', 'strengths', 'weaknesses',
        
        # Management discussion
        'management', 'explain', 'describe', 'discuss',
        'why', 'how did', 'what led to', 'reason',
        'outlook', 'guidance', 'expectation', 'forecast',
        
        # Operations and business
        'business model', 'operations', 'operational',
        'supply chain', 'manufacturing', 'distribution',
        'competition', 'competitive', 'market position',
        
        # Qualitative analysis
        'impact of', 'effect of', 'implications',
        'concerns', 'issues', 'problems', 'solutions',
        'innovation', 'technology', 'r&d', 'research',
        
        # Governance and legal
        'litigation', 'legal', 'regulatory', 'compliance',
        'governance', 'esg', 'sustainability', 'climate',
        
        # Specific 10-K sections
        'item 1a', 'item 7', 'item 7a', 'md&a',
        'risk factors', 'management discussion',
    }
    
    # Keywords that indicate hybrid queries (both needed)
    HYBRID_KEYWORDS = {
        # Impact analysis
        'affect', 'impact on', 'effect on', 'influence on',
        'relationship between', 'correlation', 'correlate',
        
        # Cause and effect
        'caused by', 'resulted in', 'led to',
        'due to', 'because of', 'driven by', 'what drove',
        
        # Comparative analysis
        'compare', 'comparison', 'versus', 'vs',
        'difference between', 'relative to',
        
        # Integrated questions
        'financial impact', 'business impact',
        'strategic implications', 'financial implications',
        
        # Explicit multi-source requests
        '10-k citations', '10k citations', 'citations',
        'macro context', 'macro', 'economic context',
        'show me the numbers', 'numbers and', 'data and',
        'context and numbers', 'qualitative and quantitative',
        
        # Conjunction patterns (strong hybrid indicators)
        ' and what was ', ' and how did ', ' and what is ',
        ' and analyze ', ' and their ', ' and show ', ' and provide ',
    }
    
    # Company name patterns
    COMPANY_NAMES = {
        'apple': ['apple', 'aapl', 'apple inc'],
        'microsoft': ['microsoft', 'msft', 'microsoft corp'],
        'amazon': ['amazon', 'amzn', 'amazon.com'],
        'google': ['google', 'googl', 'alphabet', 'alphabet inc'],
        'meta': ['meta', 'fb', 'facebook', 'meta platforms'],
    }
    
    def __init__(self, use_ml: bool = False):
        """
        Initialize query classifier
        
        Args:
            use_ml: Use machine learning for classification (future enhancement)
        """
        self.use_ml = use_ml
        
    def classify(self, query: str) -> QueryClassification:
        """
        Classify a query
        
        Args:
            query: User question
            
        Returns:
            QueryClassification with intent and metadata
        """
        query_lower = query.lower()
        
        # Count keyword matches
        quant_score = self._count_keywords(query_lower, self.QUANTITATIVE_KEYWORDS)
        qual_score = self._count_keywords(query_lower, self.QUALITATIVE_KEYWORDS)
        hybrid_score = self._count_keywords(query_lower, self.HYBRID_KEYWORDS)
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Determine intent
        intent, confidence, reasoning = self._determine_intent(
            quant_score, qual_score, hybrid_score, query_lower
        )
        
        # Determine data sources
        data_sources = self._determine_data_sources(intent)
        
        return QueryClassification(
            query=query,
            intent=intent,
            confidence=confidence,
            entities=entities,
            data_sources=data_sources,
            reasoning=reasoning
        )
    
    def _count_keywords(self, query: str, keywords: set) -> int:
        """Count keyword matches in query"""
        count = 0
        for keyword in keywords:
            if keyword in query:
                count += 1
        return count
    
    def _extract_entities(self, query: str) -> Dict[str, any]:
        """Extract entities from query (company, year, metric)"""
        entities = {
            'companies': [],
            'years': [],
            'metrics': [],
            'sections': []
        }
        
        query_lower = query.lower()
        
        # Extract companies
        for canonical, aliases in self.COMPANY_NAMES.items():
            for alias in aliases:
                if alias in query_lower:
                    entities['companies'].append(canonical)
                    break
        
        # Extract years (2019-2024)
        years = re.findall(r'\b(20[12][0-9])\b', query)
        entities['years'] = [int(y) for y in years]
        
        # Extract 10-K sections
        if 'item 1a' in query_lower or 'risk factors' in query_lower:
            entities['sections'].append('Item 1A')
        if 'item 7' in query_lower or 'md&a' in query_lower or 'management discussion' in query_lower:
            entities['sections'].append('Item 7')
        if 'item 7a' in query_lower or 'market risk' in query_lower:
            entities['sections'].append('Item 7A')
        
        return entities
    
    def _determine_intent(
        self,
        quant_score: int,
        qual_score: int,
        hybrid_score: int,
        query_lower: str
    ) -> Tuple[QueryIntent, float, str]:
        """Determine query intent based on scores"""
        
        # Explicit hybrid indicators (strong signal)
        if hybrid_score > 0:
            return QueryIntent.HYBRID, 0.90, f"Hybrid keywords detected ({hybrid_score} indicators)"
        
        # Check for multi-part questions (asking for both qual + quant)
        # Pattern: "What X... and what Y" or "How X... and Y"
        has_and = ' and ' in query_lower
        asks_about_numbers = any(word in query_lower for word in ['spending', 'revenue', 'margin', 'cash', 'expenses', 'capex', 'r&d'])
        asks_about_narrative = any(word in query_lower for word in ['risk', 'strategy', 'describe', 'discuss', 'disclose', 'address'])
        
        if has_and and asks_about_numbers and asks_about_narrative:
            return QueryIntent.HYBRID, 0.85, "Multi-part question requesting both qualitative and quantitative"
        
        # Strong quantitative signal (pure metrics question)
        if quant_score >= 3 and qual_score == 0:
            return QueryIntent.QUANTITATIVE, 0.95, f"Strong quantitative signal ({quant_score} keywords)"
        
        # Strong qualitative signal (pure narrative question)
        if qual_score >= 3 and quant_score == 0:
            return QueryIntent.QUALITATIVE, 0.95, f"Strong qualitative signal ({qual_score} keywords)"
        
        # Both signals present
        if quant_score > 0 and qual_score > 0:
            # Default to HYBRID when both types detected (safer for CFO queries)
            return QueryIntent.HYBRID, 0.80, f"Both signals present ({qual_score} qual, {quant_score} quant)"
        
        # Weak signals - use heuristics
        if quant_score > 0:
            return QueryIntent.QUANTITATIVE, 0.60, "Weak quantitative signal"
        elif qual_score > 0:
            return QueryIntent.QUALITATIVE, 0.60, "Weak qualitative signal"
        
        # Default: treat as qualitative (10-K analysis)
        return QueryIntent.QUALITATIVE, 0.50, "No clear signals, defaulting to qualitative"
    
    def _determine_data_sources(self, intent: QueryIntent) -> List[str]:
        """Determine which data sources to use"""
        if intent == QueryIntent.QUALITATIVE:
            return ['RAG']
        elif intent == QueryIntent.QUANTITATIVE:
            return ['SQL']
        else:  # HYBRID
            return ['RAG', 'SQL']
    
    def get_routing_decision(self, query: str) -> Dict[str, any]:
        """
        Get routing decision for orchestrator
        
        Returns dict with:
        - use_rag: bool
        - use_sql: bool
        - intent: str
        - confidence: float
        - entities: dict
        """
        classification = self.classify(query)
        
        return {
            'use_rag': 'RAG' in classification.data_sources,
            'use_sql': 'SQL' in classification.data_sources,
            'intent': classification.intent.value,
            'confidence': classification.confidence,
            'entities': classification.entities,
            'reasoning': classification.reasoning
        }


# Convenience function
def classify_query(query: str) -> QueryClassification:
    """Quick classification of a query"""
    classifier = QueryClassifier()
    return classifier.classify(query)


if __name__ == "__main__":
    # Test the classifier
    classifier = QueryClassifier()
    
    test_queries = [
        # Quantitative
        "What was Apple's revenue in 2022?",
        "Show me Microsoft's profit margins",
        "Calculate Apple's P/E ratio",
        
        # Qualitative
        "What are Apple's top risks?",
        "Explain Microsoft's business strategy",
        "What does Apple's management say about supply chain?",
        
        # Hybrid
        "How did supply chain risks affect Apple's margins?",
        "Compare Apple and Microsoft's risks and profitability",
        "What was the financial impact of cybersecurity risks?",
    ]
    
    print("="*80)
    print("QUERY CLASSIFIER TEST")
    print("="*80)
    
    for query in test_queries:
        result = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result.intent.value.upper()}")
        print(f"Confidence: {result.confidence:.0%}")
        print(f"Data Sources: {', '.join(result.data_sources)}")
        print(f"Companies: {', '.join(result.entities['companies']) if result.entities['companies'] else 'None'}")
        print(f"Reasoning: {result.reasoning}")
        print("-"*80)
