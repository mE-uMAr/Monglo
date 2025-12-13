from __future__ import annotations

import secrets
from typing import Any


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, dict[str, Any]] = {}
    
    def create(self, data: dict[str, Any]) -> str:
        """Create a new session and return session ID"""
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = data
        return session_id
    
    def get(self, session_id: str) -> dict[str, Any] | None:
        """Get session data by ID"""
        return self._sessions.get(session_id)
    
    def update(self, session_id: str, data: dict[str, Any]) -> None:
        """Update session data"""
        if session_id in self._sessions:
            self._sessions[session_id].update(data)
    
    def delete(self, session_id: str) -> None:
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def clear_all(self) -> None:
        """Clear all sessions"""
        self._sessions.clear()


# Global session store instance
_session_store = SessionStore()


def get_session_store() -> SessionStore:
    """Get the global session store instance"""
    return _session_store
