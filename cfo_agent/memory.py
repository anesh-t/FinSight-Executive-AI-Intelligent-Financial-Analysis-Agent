"""
Short-term session memory for context retention
"""
from typing import Dict, List, Optional


class SessionMemory:
    """Manages short-term session memory for the agent"""
    
    def __init__(self, max_tickers: int = 3):
        self.max_tickers = max_tickers
        self.sessions: Dict[str, Dict] = {}
    
    def get_or_create_session(self, session_id: str) -> Dict:
        """Get or create a session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'last_tickers': [],
                'last_period': None,
                'last_surfaces': [],
                'alias_resolutions': {},
                'query_count': 0
            }
        return self.sessions[session_id]
    
    def update_tickers(self, session_id: str, tickers: List[str]):
        """Update last used tickers"""
        session = self.get_or_create_session(session_id)
        
        # Add new tickers, keep only last N
        for ticker in tickers:
            if ticker and ticker not in session['last_tickers']:
                session['last_tickers'].append(ticker)
        
        # Keep only last max_tickers
        session['last_tickers'] = session['last_tickers'][-self.max_tickers:]
    
    def update_period(self, session_id: str, period: Dict):
        """Update last used period"""
        session = self.get_or_create_session(session_id)
        session['last_period'] = period
    
    def update_surfaces(self, session_id: str, surfaces: List[str]):
        """Update last used surfaces"""
        session = self.get_or_create_session(session_id)
        session['last_surfaces'] = surfaces
    
    def add_alias_resolution(self, session_id: str, alias: str, ticker: str):
        """Remember an alias resolution"""
        session = self.get_or_create_session(session_id)
        session['alias_resolutions'][alias] = ticker
    
    def increment_query_count(self, session_id: str):
        """Increment query count"""
        session = self.get_or_create_session(session_id)
        session['query_count'] += 1
    
    def get_last_tickers(self, session_id: str) -> List[str]:
        """Get last used tickers"""
        session = self.get_or_create_session(session_id)
        return session['last_tickers']
    
    def get_last_period(self, session_id: str) -> Optional[Dict]:
        """Get last used period"""
        session = self.get_or_create_session(session_id)
        return session['last_period']
    
    def get_context_summary(self, session_id: str) -> str:
        """Get a summary of session context"""
        session = self.get_or_create_session(session_id)
        
        parts = []
        if session['last_tickers']:
            parts.append(f"Recent tickers: {', '.join(session['last_tickers'])}")
        if session['last_period']:
            parts.append(f"Last period: {session['last_period']}")
        if session['query_count'] > 0:
            parts.append(f"Queries in session: {session['query_count']}")
        
        return " | ".join(parts) if parts else "New session"
    
    def clear_session(self, session_id: str):
        """Clear a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global memory instance
session_memory = SessionMemory()
