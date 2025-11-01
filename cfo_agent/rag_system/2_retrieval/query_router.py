"""
Query Router - Classifies queries and extracts metadata
Determines query type (semantic vs SQL) and extracts filters
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
import re
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent.parent))
from foundation.config import config


@dataclass
class QueryAnalysis:
    """Structured query analysis result"""
    query_type: Literal["semantic", "sql", "hybrid"]
    intent: str  # e.g., "risk_analysis", "financial_metrics", "comparison"
    companies: List[str]  # Extracted company filters
    years: List[int]  # Extracted year filters
    sections: List[str]  # Relevant 10-K sections
    requires_calculation: bool  # True if needs SQL calculations
    complexity: Literal["simple", "moderate", "complex"]
    confidence: float  # 0-1 confidence in classification
    reasoning: str  # Explanation of classification


class QueryRouter:
    """Routes queries to appropriate retrieval strategy"""
    
    # Company aliases for extraction
    COMPANY_ALIASES = {
        'Amazon': ['amazon', 'amzn', 'aws'],
        'Apple': ['apple', 'aapl', 'iphone', 'ipad', 'mac'],
        'Google': ['google', 'googl', 'alphabet', 'goog'],
        'Meta': ['meta', 'facebook', 'fb', 'instagram', 'whatsapp'],
        'Microsoft': ['microsoft', 'msft', 'azure', 'windows']
    }
    
    # Section keywords for mapping
    SECTION_KEYWORDS = {
        'Risk Factors': ['risk', 'risks', 'threat', 'challenge', 'vulnerability'],
        'Business': ['business', 'operations', 'strategy', 'product', 'service'],
        'MD&A': ['performance', 'results', 'analysis', 'discussion', 'financial condition'],
        'Financial Statements': ['balance sheet', 'income statement', 'cash flow', 'statement']
    }
    
    def __init__(self, use_llm: bool = False):
        """
        Initialize query router.
        
        Args:
            use_llm: Use LLM for intelligent routing (slower but more accurate)
                    Default is False for speed (rule-based routing is fast and accurate)
        """
        self.use_llm = use_llm
        if use_llm:
            self.client = OpenAI(api_key=config.llm.get_api_key())
    
    def route(self, query: str) -> QueryAnalysis:
        """
        Route query and extract metadata.
        
        Args:
            query: User query string
            
        Returns:
            QueryAnalysis with classification and metadata
        """
        if self.use_llm:
            return self._llm_route(query)
        else:
            return self._rule_based_route(query)
    
    def _llm_route(self, query: str) -> QueryAnalysis:
        """LLM-based query routing (more accurate)"""
        
        prompt = f"""Analyze this query about SEC 10-K filings and classify it:

Query: "{query}"

Available companies: Amazon, Apple, Google, Meta, Microsoft
Available years: 2019-2024
Available sections: Business, Risk Factors, MD&A, Financial Statements, Legal Proceedings, etc.

Classify the query:
1. Query Type: 
   - "semantic" = needs text search/understanding (e.g., "what are risks?", "explain strategy")
   - "sql" = needs structured data/calculations (e.g., "revenue growth", "compare profits")
   - "hybrid" = needs both semantic understanding AND calculations

2. Intent: Brief description (e.g., "risk_analysis", "revenue_comparison")

3. Companies: Which companies mentioned? (list all or "all")

4. Years: Which years mentioned? (list specific or "all")

5. Sections: Which 10-K sections are relevant? (list specific or "any")

6. Requires Calculation: Does this need math/SQL? (true/false)

7. Complexity: simple/moderate/complex

8. Confidence: 0.0-1.0 in your classification

Respond in this exact format:
TYPE: [semantic/sql/hybrid]
INTENT: [brief description]
COMPANIES: [comma-separated or "all"]
YEARS: [comma-separated or "all"]
SECTIONS: [comma-separated or "any"]
CALCULATION: [true/false]
COMPLEXITY: [simple/moderate/complex]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence explanation]
"""
        
        try:
            response = self.client.chat.completions.create(
                model=config.llm.get_model(),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            result = response.choices[0].message.content
            return self._parse_llm_response(query, result)
            
        except Exception as e:
            print(f"⚠️  LLM routing failed, falling back to rules: {e}")
            return self._rule_based_route(query)
    
    def _parse_llm_response(self, query: str, response: str) -> QueryAnalysis:
        """Parse LLM response into QueryAnalysis"""
        
        # Extract fields using regex
        query_type = self._extract_field(response, "TYPE", "semantic")
        intent = self._extract_field(response, "INTENT", "general_query")
        companies_str = self._extract_field(response, "COMPANIES", "all")
        years_str = self._extract_field(response, "YEARS", "all")
        sections_str = self._extract_field(response, "SECTIONS", "any")
        calculation = self._extract_field(response, "CALCULATION", "false").lower() == "true"
        complexity = self._extract_field(response, "COMPLEXITY", "simple")
        confidence = float(self._extract_field(response, "CONFIDENCE", "0.7"))
        reasoning = self._extract_field(response, "REASONING", "LLM analysis")
        
        # Parse companies
        if companies_str.lower() == "all":
            companies = []
        else:
            companies = [c.strip() for c in companies_str.split(',')]
        
        # Parse years
        if years_str.lower() == "all":
            years = []
        else:
            years = [int(y.strip()) for y in years_str.split(',') if y.strip().isdigit()]
        
        # Parse sections
        if sections_str.lower() == "any":
            sections = []
        else:
            sections = [s.strip() for s in sections_str.split(',')]
        
        return QueryAnalysis(
            query_type=query_type,
            intent=intent,
            companies=companies,
            years=years,
            sections=sections,
            requires_calculation=calculation,
            complexity=complexity,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _extract_field(self, text: str, field: str, default: str) -> str:
        """Extract field from LLM response"""
        pattern = f"{field}:\\s*(.+?)(?:\\n|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default
    
    def _rule_based_route(self, query: str) -> QueryAnalysis:
        """Rule-based query routing (fallback)"""
        
        query_lower = query.lower()
        
        # Determine query type
        sql_keywords = ['revenue', 'profit', 'earnings', 'growth rate', 'compare', 
                       'total', 'average', 'calculate', 'sum', 'percentage']
        
        semantic_keywords = ['why', 'how', 'explain', 'describe', 'what are',
                            'strategy', 'risk', 'challenge', 'opportunity']
        
        has_sql = any(kw in query_lower for kw in sql_keywords)
        has_semantic = any(kw in query_lower for kw in semantic_keywords)
        
        if has_sql and has_semantic:
            query_type = "hybrid"
        elif has_sql:
            query_type = "sql"
        else:
            query_type = "semantic"
        
        # Extract companies
        companies = []
        for company, aliases in self.COMPANY_ALIASES.items():
            if any(alias in query_lower for alias in aliases):
                companies.append(company)
        
        # Extract years
        years = []
        for year in range(2019, 2025):
            if str(year) in query:
                years.append(year)
        
        # Extract sections
        sections = []
        for section, keywords in self.SECTION_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                sections.append(section)
        
        return QueryAnalysis(
            query_type=query_type,
            intent="general_query",
            companies=companies,
            years=years,
            sections=sections,
            requires_calculation=has_sql,
            complexity="simple" if not (has_sql and has_semantic) else "moderate",
            confidence=0.6,
            reasoning="Rule-based classification"
        )
    
    def print_analysis(self, analysis: QueryAnalysis):
        """Pretty print query analysis"""
        print("=" * 70)
        print("QUERY ANALYSIS")
        print("=" * 70)
        print(f"Query Type:     {analysis.query_type.upper()}")
        print(f"Intent:         {analysis.intent}")
        print(f"Complexity:     {analysis.complexity}")
        print(f"Confidence:     {analysis.confidence:.2%}")
        print()
        print(f"Companies:      {', '.join(analysis.companies) if analysis.companies else 'All'}")
        print(f"Years:          {', '.join(map(str, analysis.years)) if analysis.years else 'All'}")
        print(f"Sections:       {', '.join(analysis.sections) if analysis.sections else 'Any'}")
        print()
        print(f"Needs SQL:      {analysis.requires_calculation}")
        print(f"Reasoning:      {analysis.reasoning}")
        print("=" * 70)


def test_query_router():
    """Test query router with sample queries"""
    print("TESTING QUERY ROUTER")
    print()
    
    router = QueryRouter(use_llm=True)
    
    test_queries = [
        "What are Apple's main business risks in 2024?",
        "Compare Amazon and Microsoft revenue growth from 2022 to 2024",
        "Explain Meta's AI strategy",
        "What were the cybersecurity challenges across all companies?",
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}\n")
        analysis = router.route(query)
        router.print_analysis(analysis)
        input("\nPress Enter for next query...")


if __name__ == "__main__":
    test_query_router()
