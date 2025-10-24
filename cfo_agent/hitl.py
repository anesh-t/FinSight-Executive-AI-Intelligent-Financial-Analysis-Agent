"""
Human-in-the-loop gate for query approval
"""
from typing import Dict, Tuple
import json


class HITLGate:
    """Human-in-the-loop approval gate"""
    
    def __init__(self, enabled: bool = False, always_approve_templates: bool = True):
        self.enabled = enabled
        self.always_approve_templates = always_approve_templates
    
    async def approve_plan(self, plan: Dict, is_generative: bool = False) -> Tuple[bool, str]:
        """
        Request approval for execution plan
        
        Args:
            plan: Execution plan with SQL and params
            is_generative: Whether this is generative SQL
            
        Returns:
            (approved, reason)
        """
        # If HITL is disabled, auto-approve
        if not self.enabled:
            return True, "HITL disabled"
        
        # If template-based and auto-approve is on, approve
        if not is_generative and self.always_approve_templates:
            return True, "Template auto-approved"
        
        # For generative SQL, always require approval when HITL is enabled
        if is_generative:
            return await self._request_approval(plan, "Generative SQL requires approval")
        
        # Default: approve
        return True, "Approved"
    
    async def approve_sql(self, sql: str, params: Dict, is_generative: bool = False) -> Tuple[bool, str]:
        """
        Request approval for SQL execution
        
        Args:
            sql: SQL query
            params: Query parameters
            is_generative: Whether this is generative SQL
            
        Returns:
            (approved, reason)
        """
        # If HITL is disabled, auto-approve
        if not self.enabled:
            return True, "HITL disabled"
        
        # For generative SQL, require approval
        if is_generative:
            return await self._request_approval(
                {'sql': sql, 'params': params},
                "Generative SQL execution requires approval"
            )
        
        # Default: approve
        return True, "Approved"
    
    async def _request_approval(self, context: Dict, message: str) -> Tuple[bool, str]:
        """
        Request human approval (stub for UI integration)
        
        In production, this would:
        1. Send approval request to UI
        2. Wait for human response
        3. Return approval status
        
        For now, this is a stub that auto-approves with a warning
        """
        print(f"\n⚠️ HITL APPROVAL REQUIRED: {message}")
        print(f"Context: {json.dumps(context, indent=2, default=str)}")
        print("Note: Auto-approving for development (integrate with UI for production)\n")
        
        # In production, replace this with actual approval mechanism
        # For now, auto-approve
        return True, "Auto-approved (development mode)"
    
    def enable(self):
        """Enable HITL"""
        self.enabled = True
    
    def disable(self):
        """Disable HITL"""
        self.enabled = False


# Global HITL gate instance
hitl_gate = HITLGate(enabled=False)  # Disabled by default
