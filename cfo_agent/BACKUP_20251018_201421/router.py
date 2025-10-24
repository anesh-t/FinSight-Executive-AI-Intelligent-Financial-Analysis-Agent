"""
Intent router: classify tasks and select appropriate surfaces
"""
import json
from typing import Dict, List


class IntentRouter:
    """Routes tasks to appropriate database surfaces based on intent"""
    
    def __init__(self):
        # Load templates
        with open('catalog/templates.json', 'r') as f:
            self.templates = json.load(f)['templates']
        
        # Intent to surface mapping
        self.intent_surface_map = {
            template['intent']: template['surface']
            for template in self.templates.values()
        }
    
    def route_task(self, task: Dict) -> Dict:
        """
        Route a task to appropriate surface(s) and template
        
        Args:
            task: Task dict with 'intent', 'entities', 'period', 'measures'
            
        Returns:
            Dict with 'intent', 'template_name', 'surfaces', 'entities', 'period', 'measures'
        """
        intent = task.get('intent', 'quarter_snapshot')
        
        # Find matching template
        template_name = None
        template = None
        
        for name, tmpl in self.templates.items():
            if tmpl['intent'] == intent:
                template_name = name
                template = tmpl
                break
        
        if not template:
            # Fallback to quarter_snapshot
            template_name = 'quarter_snapshot'
            template = self.templates['quarter_snapshot']
        
        # Extract surfaces
        surfaces = [s.strip() for s in template['surface'].split(',')]
        
        return {
            'intent': intent,
            'template_name': template_name,
            'template': template,
            'surfaces': surfaces,
            'entities': task.get('entities', []),
            'period': task.get('period', {'latest': True, 'fy': None, 'fq': None}),
            'measures': task.get('measures', [])
        }
    
    def route_all_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Route multiple tasks"""
        return [self.route_task(task) for task in tasks]
    
    def get_template(self, template_name: str) -> Dict:
        """Get template by name"""
        return self.templates.get(template_name)
    
    def list_intents(self) -> List[str]:
        """List all available intents"""
        return list(set(tmpl['intent'] for tmpl in self.templates.values()))
