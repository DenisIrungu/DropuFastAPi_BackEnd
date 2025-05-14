from fastapi import Request, HTTPException

def get_current_user(request: Request):
    print(f"Request cookies: {request.cookies}")  # Add this
    session = request.cookies.get("session")
    print(f"Session cookie: {session}")  # Add this
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        user_id, role = session.split("|")
        user_id = int(user_id)
        if role not in ["admin", "super_admin", "rider", "agent", "customer"]:  
            raise ValueError("Invalid role")
        print(f"Authenticated user: user_id={user_id}, role={role}")  # Add this
        return {"user_id": user_id, "role": role}
    except (ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid session")