from fastapi import HTTPException, Request

def get_current_user(request: Request):
    session = request.cookies.get("session")

    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_id, role = session.split("|")  
        return {"user_id": int(user_id), "role": role}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session format")
