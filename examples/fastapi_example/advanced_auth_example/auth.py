"""
Session-based Authentication for Monglo Admin
Simple session storage with cookies (use Redis in production)
"""

from fastapi import Request, HTTPException, status

# In-memory session storage (use Redis/database in production)
sessions = {}


def create_session(username: str) -> str:
    """Create a new session and return session ID"""
    import secrets
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {"username": username}
    return session_id


def get_session(session_id: str) -> dict | None:
    """Get session data if valid"""
    return sessions.get(session_id)


def delete_session(session_id: str) -> None:
    """Delete/logout a session"""
    if session_id in sessions:
        del sessions[session_id]


# FastAPI auth dependency for Monglo
async def require_auth(request: Request) -> str:
    """
    Auth dependency for Monglo admin panel
    Checks for session cookie
    Raises HTTPException(401) if not authenticated
    Returns username if authenticated
    """
    session_id = request.cookies.get("monglo_session")
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    session = get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    return session["username"]
