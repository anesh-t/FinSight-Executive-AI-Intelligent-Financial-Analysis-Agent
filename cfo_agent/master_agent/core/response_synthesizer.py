"""
Response Synthesizer - Combines RAG and SQL results intelligently
Handles deduplication, formatting, and CFO-level synthesis
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from execution.agent_bridge import AgentResponse


@dataclass
class SynthesizedResponse:
    """Synthesized response with metadata"""
    text: str
    has_qualitative: bool
    has_quantitative: bool
    deduplicated: bool
    citations: List[str]


class ResponseSynthesizer:
    """Synthesizes responses from multiple agents"""
    
    def __init__(self):
        """Initialize response synthesizer"""
        pass
    
    def synthesize(
        self,
        rag_response: Optional[AgentResponse],
        sql_response: Optional[AgentResponse],
        question: str,
        intent: str = "hybrid"
    ) -> SynthesizedResponse:
        """
        Synthesize responses from RAG and SQL agents
        
        Args:
            rag_response: Response from RAG agent (qualitative)
            sql_response: Response from SQL agent (quantitative)
            question: Original user question
            intent: Query intent (qualitative/quantitative/hybrid)
            
        Returns:
            SynthesizedResponse with combined analysis
        """
        has_rag = rag_response is not None and rag_response.success
        has_sql = sql_response is not None and sql_response.success
        
        # Single agent responses
        if intent == "qualitative" or (has_rag and not has_sql):
            return self._format_rag_only(rag_response, question)
        
        if intent == "quantitative" or (has_sql and not has_rag):
            return self._format_sql_only(sql_response, question)
        
        # Hybrid response
        if has_rag and has_sql:
            return self._synthesize_hybrid(rag_response, sql_response, question)
        
        # Fallback
        return SynthesizedResponse(
            text="Unable to generate response. Please try again.",
            has_qualitative=False,
            has_quantitative=False,
            deduplicated=False,
            citations=[]
        )
    
    def _format_rag_only(
        self,
        rag_response: AgentResponse,
        question: str
    ) -> SynthesizedResponse:
        """Format RAG-only response"""
        
        text = f"""# 📖 CFO ANALYSIS - Qualitative Insights

**Question:** {question}

---

{rag_response.text}

---

**Source:** SEC 10-K Filings
"""
        
        return SynthesizedResponse(
            text=text,
            has_qualitative=True,
            has_quantitative=False,
            deduplicated=False,
            citations=self._extract_citations(rag_response.text)
        )
    
    def _format_sql_only(
        self,
        sql_response: AgentResponse,
        question: str
    ) -> SynthesizedResponse:
        """Format SQL-only response"""
        
        text = f"""# 📊 CFO ANALYSIS - Financial Data

**Question:** {question}

---

{sql_response.text}

---

**Source:** Financial Database
"""
        
        return SynthesizedResponse(
            text=text,
            has_qualitative=False,
            has_quantitative=True,
            deduplicated=False,
            citations=[]
        )
    
    def _synthesize_hybrid(
        self,
        rag_response: AgentResponse,
        sql_response: AgentResponse,
        question: str
    ) -> SynthesizedResponse:
        """Synthesize hybrid response combining RAG and SQL"""
        
        # Check if SQL has actual data or just a failure message
        sql_text = sql_response.text.strip()
        has_sql_data = (
            sql_text 
            and not sql_text.startswith("No results") 
            and not sql_text.startswith("Unable to")
            and len(sql_text) > 20
        )
        
        parts = []
        
        # Header
        parts.append("# 📊 COMPREHENSIVE CFO ANALYSIS")
        parts.append(f"\n**Question:** {question}\n")
        parts.append("---\n")
        
        # Executive Summary
        parts.append("## 🎯 EXECUTIVE SUMMARY\n")
        if has_sql_data:
            parts.append("This analysis combines qualitative insights from SEC 10-K filings")
            parts.append("with quantitative financial data.\n")
        else:
            parts.append("This analysis provides qualitative insights from SEC 10-K filings.")
            parts.append("Quantitative financial data was not available for this specific query.\n")
        
        # Qualitative Section
        parts.append("\n## 📖 QUALITATIVE ANALYSIS\n")
        parts.append(rag_response.text)
        
        # Quantitative Section
        parts.append("\n\n## 📈 QUANTITATIVE DATA\n")
        if has_sql_data:
            parts.append(sql_response.text)
        else:
            # Provide helpful message about why quantitative data is missing
            parts.append("⚠️  **Note:** Specific quantitative data for this query was not available in the financial database.")
            parts.append("\n\nPossible reasons:")
            parts.append("- The query may require a different phrasing")
            parts.append("- The specific metric may not be in the database")
            parts.append("- Multi-company comparisons may need individual queries")
            parts.append("\n\n**Suggestion:** Try asking for specific metrics individually, such as:")
            parts.append("- 'What was Apple's operating margin in 2022?'")
            parts.append("- 'What was Microsoft's operating margin in 2022?'")
        
        # Integrated Insights
        parts.append("\n\n## 💡 INTEGRATED INSIGHTS\n")
        if has_sql_data:
            parts.append("- The narrative context provides important background for the metrics")
            parts.append("- CFOs should consider both qualitative risks and quantitative performance")
        else:
            parts.append("- The qualitative analysis provides strategic context and risk assessment")
            parts.append("- For complete analysis, consider querying financial metrics separately")
        parts.append("")
        
        # Sources
        parts.append("\n---\n")
        parts.append("**Sources:**")
        parts.append("- Qualitative: SEC 10-K Filings")
        if has_sql_data:
            parts.append("- Quantitative: Financial Database")
        else:
            parts.append("- Quantitative: Not available for this query")
        
        return SynthesizedResponse(
            text="\n".join(parts),
            has_qualitative=True,
            has_quantitative=has_sql_data,
            deduplicated=False,
            citations=self._extract_citations(rag_response.text)
        )
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract citation numbers from text"""
        citations = re.findall(r'\[(\d+)\]', text)
        return list(set(citations))
