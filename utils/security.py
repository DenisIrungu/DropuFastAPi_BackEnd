from fastapi import Response
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if a plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_session(response: Response, user_id: int, role: str):
    """Create a session cookie for the user."""
    session_data = f"{user_id}|{role}"
    response.set_cookie(key="session", value=session_data, httponly=True, secure=True, samesite="Lax")

def destroy_session(response: Response):
    """Destroy the session cookie."""
    response.delete_cookie("session")
