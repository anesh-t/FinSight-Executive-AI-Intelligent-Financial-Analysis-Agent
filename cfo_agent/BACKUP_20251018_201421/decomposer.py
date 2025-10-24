"""
Query decomposer: split multi-part questions into ordered tasks
"""
import json
import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()


class QueryDecomposer:
    """Decomposes natural language queries into structured tasks"""
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        
        # Load router/planner prompt
        with open('prompts/router_planner_prompt.md', 'r') as f:
            self.router_prompt = f.read()
        
        # Load routing examples
        with open('catalog/routing_examples.json', 'r') as f:
            self.examples = json.load(f)['examples']
    
    async def decompose(self, question: str) -> Dict:
        """
        Decompose a natural language question into structured tasks
        
        Args:
            question: User's natural language question
            
        Returns:
            Dict with 'greeting', 'tasks', and 'checks'
        """
        # Simple entity extraction and intent detection as fallback
        import re
        
        # Extract common tickers
        tickers = []
        ticker_patterns = ['AAPL', 'MSFT', 'AMZN', 'GOOG', 'META', 'GOOGL']
        for ticker in ticker_patterns:
            if ticker in question.upper():
                tickers.append(ticker)
        
        # Also check for company names
        company_map = {
            'APPLE': 'AAPL',
            'MICROSOFT': 'MSFT',
            'AMAZON': 'AMZN',
            'GOOGLE': 'GOOG',
            'ALPHABET': 'GOOG',
            'META': 'META',
            'FACEBOOK': 'META'
        }
        
        question_upper = question.upper()
        for name, ticker in company_map.items():
            if name in question_upper and ticker not in tickers:
                tickers.append(ticker)
        
        # Extract year if present
        year_match = re.search(r'(FY\s*)?(\d{4})', question)
        if year_match:
            year = int(year_match.group(2))
            period = {"fy": year, "fq": None}
        else:
            period = {"fy": None, "fq": None}  # NULL means latest
        
        # Extract quarter if present (multiple patterns)
        quarter_match = None
        
        # Pattern 1: Q1, Q2, Q3, Q4
        quarter_match = re.search(r'Q\s*(\d)', question_upper)
        if quarter_match:
            period["fq"] = int(quarter_match.group(1))
        # Pattern 2: 1st quarter, 2nd quarter, 3rd quarter, 4th quarter
        elif re.search(r'(\d)(ST|ND|RD|TH)\s+QUARTER', question_upper):
            quarter_num_match = re.search(r'(\d)(ST|ND|RD|TH)\s+QUARTER', question_upper)
            period["fq"] = int(quarter_num_match.group(1))
        # Pattern 3: first, second, third, fourth quarter
        elif 'FIRST QUARTER' in question_upper or 'FIRST-QUARTER' in question_upper:
            period["fq"] = 1
        elif 'SECOND QUARTER' in question_upper or 'SECOND-QUARTER' in question_upper:
            period["fq"] = 2
        elif 'THIRD QUARTER' in question_upper or 'THIRD-QUARTER' in question_upper:
            period["fq"] = 3
        elif 'FOURTH QUARTER' in question_upper or 'FOURTH-QUARTER' in question_upper:
            period["fq"] = 4
        
        # Detect intent from keywords
        # Default: if year but no quarter specified → annual_metrics
        # If quarter specified or "latest quarter" → quarter_snapshot
        intent = "quarter_snapshot"  # default
        
        # Check if this is a year-only query (no quarter specified)
        has_year = period.get("fy") is not None
        has_quarter = period.get("fq") is not None
        
        # Peer queries
        if any(word in question_upper for word in ['WHO LED', 'RANK', 'LEADER', 'PEER', 'COMPARE ALL']):
            if any(word in question_upper for word in ['ANNUAL', 'YEAR', 'FY']):
                intent = "peer_leaderboard_annual"
            else:
                intent = "peer_leaderboard_quarter"
        # Annual queries: year specified without quarter, or explicit "annual"/"year"/"total"
        # This handles revenue, expenses (R&D, SG&A, COGS), and all other metrics
        elif has_year and not has_quarter:
            intent = "annual_metrics"
        elif any(word in question_upper for word in ['ANNUAL', 'TOTAL', 'FULL YEAR']):
            intent = "annual_metrics"
        # Explicit quarter queries - handles revenue, expenses, and all quarterly metrics
        elif has_quarter or any(word in question_upper for word in ['QUARTER', 'Q1', 'Q2', 'Q3', 'Q4', 'LATEST QUARTER']):
            intent = "quarter_snapshot"
        # Growth queries
        elif any(word in question_upper for word in ['GROWTH', 'YOY', 'QOQ', 'CAGR']):
            if 'CAGR' in question_upper or '3-YEAR' in question_upper or '5-YEAR' in question_upper:
                intent = "growth_annual_cagr"
            else:
                intent = "growth_qoq_yoy"
        
        # Build few-shot prompt with examples
        few_shot_examples = self._build_few_shot_examples()
        
        messages = [
            SystemMessage(content=self.router_prompt + "\n\n" + few_shot_examples),
            HumanMessage(content=f"Question: {question}\n\nOutput (JSON only):")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Parse JSON response
            result = json.loads(response.content)
            
            # Validate structure
            if 'tasks' not in result:
                result['tasks'] = []
            if 'greeting' not in result:
                result['greeting'] = ""
            if 'checks' not in result:
                result['checks'] = ["use_whitelist", "bind_params", "limit_results"]
            
            # If entities are empty but we found tickers, add them
            if result['tasks'] and not result['tasks'][0].get('entities'):
                result['tasks'][0]['entities'] = tickers
            
            return result
        except json.JSONDecodeError as e:
            # Fallback: create a single task with detected intent and extracted tickers
            # Make sure intent is using the same logic
            fallback_intent = intent  # Already computed above with year/quarter logic
            
            return {
                "greeting": "",
                "tasks": [{
                    "intent": fallback_intent,
                    "entities": tickers,
                    "period": period,
                    "measures": []
                }],
                "checks": ["use_whitelist", "bind_params", "limit_results"],
                "error": f"Failed to parse LLM response: {str(e)}"
            }
    
    def _build_few_shot_examples(self) -> str:
        """Build few-shot examples from catalog"""
        examples_text = "\n\n## Examples:\n\n"
        
        for i, example in enumerate(self.examples[:5], 1):  # Use first 5 examples
            examples_text += f"### Example {i}:\n"
            examples_text += f"Question: {example['question']}\n"
            examples_text += f"Output: {json.dumps(example['expected_output'], indent=2)}\n\n"
        
        return examples_text
