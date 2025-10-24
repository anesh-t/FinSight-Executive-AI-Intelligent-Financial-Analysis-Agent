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
    
    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0):
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
        """Build prompt with allowlist and schema info"""
        allowed_surfaces = get_allowed_surfaces()
        
        # Replace placeholder in template
        prompt = self.sql_prompt_template.replace(
            '{SURFACES_FROM_ALLOWLIST}',
            ', '.join(allowed_surfaces)
        )
        
        # Add schema info for relevant surfaces
        surfaces = context.get('surfaces', [])
        if surfaces:
            schema_info = "\n\n## Available Columns:\n\n"
            for surface in surfaces:
                columns = get_schema_for_surface(surface)
                if columns:
                    schema_info += f"**{surface}**: {', '.join(columns[:20])}\n"  # Show first 20 columns
            prompt += schema_info
        
        # Add context
        prompt += f"\n\n## Context:\n"
        prompt += f"- Intent: {context.get('intent')}\n"
        prompt += f"- Surfaces: {', '.join(surfaces)}\n"
        
        entities = context.get('entities_resolved', {})
        if entities:
            prompt += f"- Entities: {entities}\n"
        
        params = context.get('params', {})
        if params:
            prompt += f"- Parameters available: {', '.join(params.keys())}\n"
        
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
