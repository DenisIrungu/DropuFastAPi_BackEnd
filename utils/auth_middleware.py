from fastapi import Request, HTTPException

def get_current_user(request: Request):
    session = request.cookies.get("session")
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        user_id, role = session.split("|")
        user_id = int(user_id)
        if role not in ["admin", "super_admin", "rider", "agent", "customer"]:  
            raise ValueError("Invalid role")
        return {"user_id": user_id, "role": role}
    except (ValueError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid session")