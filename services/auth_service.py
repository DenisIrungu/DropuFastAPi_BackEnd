from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Admin, Rider, Agent, Customer
from schemas.auth_schema import AuthLogin, UserRegistration
from utils.security import hash_password, verify_password

def authenticate_user(db: Session, login_data: AuthLogin):
    """Authenticate user and return their role if valid."""
    email = login_data.email
    password = login_data.password 

    user = (
        db.query(Admin).filter(Admin.email == email).first() or
        db.query(Rider).filter(Rider.email == email).first() or
        db.query(Agent).filter(Agent.email == email).first() or
        db.query(Customer).filter(Customer.email == email).first()
    )

    if user and verify_password(password, user.password):
        if isinstance(user, Admin):
            return {"role": "admin", "user": user}
        elif isinstance(user, Rider):
            return {"role": "rider", "user": user}
        elif isinstance(user, Agent):
            return {"role": "agent", "user": user}
        elif isinstance(user, Customer):
            return {"role": "customer", "user": user}

    return None  

def create_user(db: Session, user_data: UserRegistration):
    """Create a new user while preventing duplicate emails."""
    email = user_data.email

    existing_user = (
        db.query(Admin).filter(Admin.email == email).first() or
        db.query(Rider).filter(Rider.email == email).first() or
        db.query(Agent).filter(Agent.email == email).first() or
        db.query(Customer).filter(Customer.email == email).first()
    )

    if existing_user:
        return {"error": "Email is already registered"}


    hashed_password = hash_password(user_data.password)


    role_model = {
        "admin": Admin,
        "rider": Rider,
        "agent": Agent,
        "customer": Customer
    }.get(user_data.role.lower())

    if not role_model:
        raise HTTPException(status_code=400, detail="Invalid role provided")


    # Create and save user
    new_user = role_model(
        email=user_data.email,
        password=hashed_password,  
        name=user_data.name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}
