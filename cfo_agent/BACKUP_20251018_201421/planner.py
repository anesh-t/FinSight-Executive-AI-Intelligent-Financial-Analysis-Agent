"""
Task planner: create structured execution plan with parameters
"""
from typing import Dict, List
from db.resolve import resolve_entities, get_latest_period


class TaskPlanner:
    """Creates structured execution plans for routed tasks"""
    
    async def plan_task(self, routed_task: Dict) -> Dict:
        """
        Create execution plan for a routed task
        
        Args:
            routed_task: Output from router with template and entities
            
        Returns:
            Dict with 'sql', 'params', 'surfaces', 'entities_resolved'
        """
        template = routed_task['template']
        entities = routed_task['entities']
        period = routed_task['period']
        
        # Resolve entities to tickers
        entities_resolved = await resolve_entities(entities) if entities else {}
        
        # Build parameters
        params = await self._build_params(
            template,
            entities_resolved,
            period,
            routed_task.get('measures', [])
        )
        
        # Get SQL from template
        sql = template['sql']
        
        return {
            'sql': sql,
            'params': params,
            'surfaces': routed_task['surfaces'],
            'entities_resolved': entities_resolved,
            'template_name': routed_task['template_name'],
            'intent': routed_task['intent']
        }
    
    async def _build_params(self, template: Dict, entities_resolved: Dict, period: Dict, measures: List) -> Dict:
        """Build parameter dict for SQL execution"""
        params = {}
        
        # Get template params and defaults
        template_params = template.get('params', [])
        default_params = template.get('default_params', {})
        
        # Start with defaults
        params.update(default_params)
        
        # Add ticker if needed
        if 'ticker' in template_params:
            if entities_resolved:
                # Use first resolved ticker
                ticker = list(entities_resolved.values())[0]
                if ticker:
                    params['ticker'] = ticker
        
        # Add t1, t2 for comparison queries
        if 't1' in template_params and 't2' in template_params:
            tickers = [t for t in entities_resolved.values() if t]
            if len(tickers) >= 2:
                params['t1'] = tickers[0]
                params['t2'] = tickers[1]
        
        # Add period params - simplified logic
        # If year is specified, use it; otherwise leave as NULL for latest
        if period.get('fy'):
            params['fy'] = period['fy']
        else:
            params['fy'] = None
            
        if period.get('fq'):
            params['fq'] = period['fq']
        else:
            params['fq'] = None
        
        # Ensure limit is set
        if 'limit' not in params:
            params['limit'] = 10
        
        # Cap limit at 200
        if params.get('limit', 0) > 200:
            params['limit'] = 200
        
        return params
    
    async def plan_all_tasks(self, routed_tasks: List[Dict]) -> List[Dict]:
        """Plan multiple tasks"""
        plans = []
        for task in routed_tasks:
            plan = await self.plan_task(task)
            plans.append(plan)
        return plans
