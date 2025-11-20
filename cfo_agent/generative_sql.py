"""
Generative SQL builder with validation and dry-run
"""
from typing import List, Tuple, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from db.whitelist import get_allowed_surfaces, get_schema_for_surface

# Load environment variables
load_dotenv()


class GenerativeSQLBuilder:
    """Generates SQL using LLM with safety constraints"""
    
    def __init__(self, model: str = "gpt-5.1", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        
        # Load generative SQL prompt
        with open('prompts/generative_sql_prompt.md', 'r') as f:
            self.sql_prompt_template = f.read()
    
    async def generate_sql(self, context: Dict) -> List[Tuple[str, Dict]]:
        """
        Generate SQL candidates for a given context
        
        Args:
            context: Dict with 'intent', 'surfaces', 'entities_resolved', 'params'
            
        Returns:
            List of (sql, params) tuples (up to 2 candidates)
        """
        # Build prompt with context
        prompt = self._build_prompt(context)
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Generate SQL for intent: {context.get('intent', 'unknown')}")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # Parse response (may contain 1 or 2 candidates separated by ----)
        sql_candidates = self._parse_candidates(response.content)
        
        # Build params for each candidate
        params = context.get('params', {})
        
        return [(sql, params.copy()) for sql in sql_candidates]
    
    def _build_prompt(self, context: Dict) -> str:
        """Build comprehensive prompt with database schema and context"""
        allowed_surfaces = get_allowed_surfaces()
        
        # Replace placeholder in template
        prompt = self.sql_prompt_template.replace(
            '{SURFACES_FROM_ALLOWLIST}',
            ', '.join(allowed_surfaces)
        )
        
        # Add detailed schema info for ALL relevant surfaces
        prompt += "\n\n## 📋 DETAILED SCHEMA INFORMATION:\n\n"
        
        # Group surfaces by category
        combined_views = [s for s in allowed_surfaces if 'company_complete' in s or 'company_macro' in s or 'company_full' in s]
        financial_tables = [s for s in allowed_surfaces if 'financials' in s or 'fact_financials' in s]
        ratio_tables = [s for s in allowed_surfaces if 'ratios' in s]
        growth_tables = [s for s in allowed_surfaces if 'growth' in s]
        stock_tables = [s for s in allowed_surfaces if 'stock' in s]
        macro_tables = [s for s in allowed_surfaces if 'macro' in s and 'sensitivity' not in s]
        sensitivity_tables = [s for s in allowed_surfaces if 'sensitivity' in s]
        peer_tables = [s for s in allowed_surfaces if 'peer' in s]
        
        # Show schema for each category
        if combined_views:
            prompt += "### Combined Views (Use These First!):\n"
            for surface in combined_views[:6]:  # Show top 6
                columns = get_schema_for_surface(surface)
                if columns:
                    prompt += f"**{surface}**: {', '.join(columns[:30])}\n"
        
        if financial_tables:
            prompt += "\n### Financial Tables:\n"
            for surface in financial_tables[:3]:
                columns = get_schema_for_surface(surface)
                if columns:
                    prompt += f"**{surface}**: {', '.join(columns[:25])}\n"
        
        if ratio_tables:
            prompt += "\n### Ratio Tables:\n"
            for surface in ratio_tables[:3]:
                columns = get_schema_for_surface(surface)
                if columns:
                    prompt += f"**{surface}**: {', '.join(columns[:15])}\n"
        
        if growth_tables:
            prompt += "\n### Growth Tables:\n"
            for surface in growth_tables[:3]:
                columns = get_schema_for_surface(surface)
                if columns:
                    prompt += f"**{surface}**: {', '.join(columns[:15])}\n"
        
        # Add user query context
        prompt += f"\n\n## 🎯 YOUR TASK:\n\n"
        prompt += f"**User Question Intent:** {context.get('intent', 'unknown')}\n\n"
        
        entities = context.get('entities_resolved', {})
        if entities:
            prompt += f"**Entities Identified:**\n"
            for entity, ticker in entities.items():
                prompt += f"  - {entity} → {ticker}\n"
        
        params = context.get('params', {})
        if params:
            prompt += f"\n**Parameters Available:**\n"
            for param, value in params.items():
                if value is not None:
                    prompt += f"  - :{param} = {value}\n"
                else:
                    prompt += f"  - :{param} = NULL (use latest)\n"
        
        # Add specific guidance based on intent
        intent = context.get('intent', '').lower()
        prompt += f"\n**Recommended Approach:**\n"
        
        if 'multiple' in intent or 'several' in intent:
            prompt += "→ Use `vw_company_complete_quarter` (has 70+ columns)\n"
        elif 'macro' in intent or 'economic' in intent or 'gdp' in intent or 'cpi' in intent:
            prompt += "→ Use `vw_company_macro_context_quarter` (includes macro indicators)\n"
        elif 'sensitivity' in intent or 'correlation' in intent or 'beta' in intent:
            prompt += "→ Use `vw_company_full_quarter` (includes sensitivity betas)\n"
        elif 'growth' in intent or 'yoy' in intent or 'qoq' in intent:
            prompt += "→ Use `vw_growth_quarter` or JOIN with growth view\n"
        elif 'compare' in intent or 'peer' in intent or 'rank' in intent:
            prompt += "→ Use `vw_peer_stats_quarter` for peer comparisons\n"
        elif 'annual' in intent or 'yearly' in intent or 'fy' in str(params.get('fy', '')):
            prompt += "→ Use `mv_company_complete_annual` (annual aggregates)\n"
        else:
            prompt += "→ Start with `vw_company_complete_quarter` (most comprehensive)\n"
        
        prompt += "\n**Remember:**\n"
        prompt += "- Always add `LIMIT :limit`\n"
        prompt += "- Use table aliases (e.g., `cc.revenue`)\n"
        prompt += "- Protect division with NULLIF()\n"
        prompt += "- Format: billions (/1e9), percentages (*100)\n"
        
        return prompt
    
    def _parse_candidates(self, response: str) -> List[str]:
        """Parse SQL candidates from LLM response"""
        # Split by ---- separator
        parts = response.split('----')
        
        candidates = []
        for part in parts:
            # Clean up
            sql = part.strip()
            
            # Remove markdown code blocks if present
            if sql.startswith('```'):
                lines = sql.split('\n')
                sql = '\n'.join(lines[1:-1]) if len(lines) > 2 else sql
            
            sql = sql.strip()
            
            if sql and sql.upper().startswith('SELECT'):
                candidates.append(sql)
        
        # Return up to 2 candidates
        return candidates[:2] if candidates else []
