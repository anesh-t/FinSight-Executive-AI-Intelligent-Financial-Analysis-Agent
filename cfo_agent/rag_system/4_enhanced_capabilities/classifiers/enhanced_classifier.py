"""
Enhanced Query Classifier - Detect 8 advanced capability types
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re


class CapabilityType(Enum):
    """8 advanced capability types"""
    FINANCIAL_EXTRACTION = "financial_extraction"
    DISCLOSURE_SUMMARY = "disclosure_summary"
    HISTORICAL_COMPARISON = "historical_comparison"
    PEER_BENCHMARK = "peer_benchmark"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    COMPLIANCE_REVIEW = "compliance_review"
    BOARD_BRIEFING = "board_briefing"
    ESG_REGULATORY = "esg_regulatory"
    GENERAL = "general"  # Fallback


@dataclass
class ClassificationResult:
    """Classification result with metadata"""
    capability: CapabilityType
    confidence: float
    entities: Dict[str, List[str]]
    keywords_matched: List[str]
    
    def __str__(self):
        return f"{self.capability.value} (confidence: {self.confidence:.2f})"


class EnhancedQueryClassifier:
    """Classify queries into 8 capability types"""
    
    # Keyword patterns for each capability
    CAPABILITY_PATTERNS = {
        CapabilityType.FINANCIAL_EXTRACTION: {
            'keywords': [
                'cash flow', 'net cash', 'operating cash', 'free cash flow',
                'revenue', 'net income', 'earnings', 'profit',
                'expense', 'cost', 'spending', 'expenditure',
                'capex', 'capital expenditure', 'r&d expense',
                'debt', 'equity', 'assets', 'liabilities',
                'margin', 'ratio', 'return on'
            ],
            'patterns': [
                r'what (was|is|were) .* (cash flow|revenue|income|expense)',
                r'show .* (cash flow|revenue|income|expense)',
                r'how much .* (spent|earned|generated)',
                r'\$[\d,]+',  # Dollar amounts
                r'\d+%',  # Percentages
            ],
            'question_words': ['what', 'how much', 'show']
        },
        
        CapabilityType.DISCLOSURE_SUMMARY: {
            'keywords': [
                'summarize', 'summary', 'overview', 'list all',
                'major', 'key', 'main', 'primary',
                'risk factors', 'risks', 'disclosures',
                'business description', 'operations',
                'legal proceedings', 'material weaknesses'
            ],
            'patterns': [
                r'summarize (all|major|key)',
                r'list (all|major|key)',
                r'what are (all|the|major) .* (risks|disclosures)',
                r'give .* overview',
                r'provide .* summary'
            ],
            'question_words': ['summarize', 'list', 'overview', 'what are']
        },
        
        CapabilityType.HISTORICAL_COMPARISON: {
            'keywords': [
                'compare', 'comparison', 'trend', 'over time',
                'year over year', 'yoy', 'change', 'growth',
                'last 3 years', 'past years', 'historical',
                'evolution', 'trajectory', 'over the',
                'from 2019 to', 'between 2020 and'
            ],
            'patterns': [
                r'compare .* (over|across|from) .* (year|period)',
                r'how (did|has) .* (change|evolve|grow)',
                r'trend .* (over|across)',
                r'(last|past) \d+ years',
                r'from \d{4} to \d{4}',
                r'between \d{4} and \d{4}',
                r'year over year',
                r'yoy'
            ],
            'question_words': ['compare', 'how did', 'trend', 'change']
        },
        
        CapabilityType.PEER_BENCHMARK: {
            'keywords': [
                'compare', 'vs', 'versus', 'against',
                'peer', 'competitor', 'industry',
                'rank', 'ranking', 'benchmark',
                'top 3', 'competitors', 'peers',
                'how does', 'relative to'
            ],
            'patterns': [
                r'compare .* (and|vs|versus)',
                r'(apple|microsoft|google|amazon|meta) (and|vs|versus)',
                r'how does .* compare',
                r'rank .* by',
                r'benchmark .* against',
                r'top \d+ (companies|competitors|peers)',
                r'relative to (peers|competitors|industry)'
            ],
            'question_words': ['compare', 'rank', 'benchmark', 'how does']
        },
        
        CapabilityType.SENTIMENT_ANALYSIS: {
            'keywords': [
                'tone', 'sentiment', 'optimistic', 'pessimistic',
                'outlook', 'attitude', 'perspective',
                'ceo', 'management', 'md&a',
                'positive', 'negative', 'bullish', 'bearish',
                'confidence', 'concern'
            ],
            'patterns': [
                r'analyze .* tone',
                r'sentiment .* (analysis|change)',
                r'(ceo|management) .* (tone|outlook)',
                r'how (optimistic|pessimistic|positive|negative)',
                r'tone .* (vs|versus|compared)',
                r'outlook .* (change|shift)'
            ],
            'question_words': ['analyze', 'sentiment', 'tone']
        },
        
        CapabilityType.COMPLIANCE_REVIEW: {
            'keywords': [
                'sox', 'sarbanes-oxley', 'compliance',
                'internal control', 'material weakness',
                'control deficiency', 'audit',
                'item 9a', 'controls and procedures',
                'certification', 'attestation'
            ],
            'patterns': [
                r'sox (compliance|disclosure)',
                r'material weakness',
                r'internal control',
                r'control (deficiency|deficiencies)',
                r'item 9a',
                r'compliance (review|disclosure)'
            ],
            'question_words': ['list', 'show', 'what']
        },
        
        CapabilityType.BOARD_BRIEFING: {
            'keywords': [
                'board', 'executive', 'briefing',
                'presentation', 'slide', 'deck',
                'overview', 'summary', 'highlights',
                'key points', 'executive summary',
                'board meeting', 'c-suite'
            ],
            'patterns': [
                r'board (briefing|presentation|meeting)',
                r'executive (overview|summary|briefing)',
                r'create .* (presentation|slide|deck)',
                r'prepare .* (board|executive)',
                r'key points for',
                r'highlights for'
            ],
            'question_words': ['create', 'prepare', 'generate']
        },
        
        CapabilityType.ESG_REGULATORY: {
            'keywords': [
                'esg', 'environmental', 'social', 'governance',
                'sustainability', 'climate', 'carbon',
                'regulatory', 'regulation', 'compliance',
                'green', 'renewable', 'emissions',
                'diversity', 'inclusion', 'ethics'
            ],
            'patterns': [
                r'esg (commitment|disclosure|reporting)',
                r'environmental .* (risk|commitment|disclosure)',
                r'climate .* (risk|commitment|change)',
                r'regulatory (risk|challenge|disclosure)',
                r'sustainability .* (initiative|commitment)',
                r'carbon .* (emission|footprint|neutral)'
            ],
            'question_words': ['summarize', 'what', 'show']
        }
    }
    
    def __init__(self):
        """Initialize classifier"""
        print("🎯 Enhanced Query Classifier initialized")
        print(f"   Capabilities: {len(CapabilityType) - 1}")  # Exclude GENERAL
    
    def classify(self, query: str) -> ClassificationResult:
        """
        Classify query into capability type.
        
        Args:
            query: User query
            
        Returns:
            ClassificationResult with capability and metadata
        """
        query_lower = query.lower()
        
        # Score each capability
        scores = {}
        matched_keywords = {}
        
        for capability, patterns in self.CAPABILITY_PATTERNS.items():
            score = 0
            keywords_found = []
            
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword in query_lower:
                    score += 1
                    keywords_found.append(keyword)
            
            # Check regex patterns (weighted higher)
            for pattern in patterns['patterns']:
                if re.search(pattern, query_lower):
                    score += 2
                    keywords_found.append(f"pattern:{pattern[:20]}")
            
            # Check question words
            for qword in patterns['question_words']:
                if query_lower.startswith(qword):
                    score += 0.5
            
            scores[capability] = score
            matched_keywords[capability] = keywords_found
        
        # Get best match
        if max(scores.values()) > 0:
            best_capability = max(scores, key=scores.get)
            confidence = min(scores[best_capability] / 5.0, 1.0)  # Normalize to 0-1
        else:
            best_capability = CapabilityType.GENERAL
            confidence = 1.0
        
        # Extract entities
        entities = self._extract_entities(query)
        
        return ClassificationResult(
            capability=best_capability,
            confidence=confidence,
            entities=entities,
            keywords_matched=matched_keywords[best_capability]
        )
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from query"""
        entities = {
            'companies': [],
            'years': [],
            'metrics': [],
            'sections': []
        }
        
        query_lower = query.lower()
        
        # Extract companies
        companies = ['apple', 'microsoft', 'google', 'amazon', 'meta', 'alphabet']
        for company in companies:
            if company in query_lower:
                entities['companies'].append(company.title())
        
        # Extract years
        year_pattern = r'\b(20\d{2})\b'
        years = re.findall(year_pattern, query)
        entities['years'] = [int(y) for y in years]
        
        # Extract common metrics
        metrics = [
            'revenue', 'cash flow', 'net income', 'r&d', 'capex',
            'debt', 'equity', 'margin', 'expense', 'profit'
        ]
        for metric in metrics:
            if metric in query_lower:
                entities['metrics'].append(metric)
        
        # Extract sections
        sections = ['risk', 'md&a', 'business', 'legal', 'controls']
        for section in sections:
            if section in query_lower:
                entities['sections'].append(section)
        
        return entities
    
    def get_capability_description(self, capability: CapabilityType) -> str:
        """Get human-readable description of capability"""
        descriptions = {
            CapabilityType.FINANCIAL_EXTRACTION: "Extract financial metrics from 10-K text",
            CapabilityType.DISCLOSURE_SUMMARY: "Summarize specific disclosure sections",
            CapabilityType.HISTORICAL_COMPARISON: "Compare metrics across multiple years",
            CapabilityType.PEER_BENCHMARK: "Compare metrics across multiple companies",
            CapabilityType.SENTIMENT_ANALYSIS: "Analyze tone and sentiment changes",
            CapabilityType.COMPLIANCE_REVIEW: "Review SOX and compliance disclosures",
            CapabilityType.BOARD_BRIEFING: "Create executive-level overview",
            CapabilityType.ESG_REGULATORY: "Summarize ESG and regulatory disclosures",
            CapabilityType.GENERAL: "General 10-K analysis"
        }
        return descriptions.get(capability, "Unknown capability")


if __name__ == "__main__":
    # Test the classifier
    classifier = EnhancedQueryClassifier()
    
    test_queries = [
        "What was Apple's net cash flow in 2022?",
        "Summarize all major risk factors for Microsoft",
        "How did R&D expense change over the last 3 years?",
        "Compare Apple and Microsoft's debt-to-equity ratios",
        "Analyze the CEO's tone in the 2022 MD&A",
        "List SOX compliance disclosures",
        "Create a board briefing from Apple's 10-K",
        "Summarize Apple's ESG commitments"
    ]
    
    print("\n" + "="*80)
    print("TESTING ENHANCED CLASSIFIER")
    print("="*80)
    
    for query in test_queries:
        result = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"Capability: {result.capability.value}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Companies: {result.entities['companies']}")
        print(f"Years: {result.entities['years']}")
        print(f"Keywords: {result.keywords_matched[:3]}")
