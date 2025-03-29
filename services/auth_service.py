from sqlalchemy.orm import Session
from models import Admin, Rider, Agent, Customer
from schemas.auth_schema import AuthLogin, UserRegistration, UserResponse
from utils.security import hash_password, verify_password
from fastapi import HTTPException

def authenticate_user(db: Session, request: AuthLogin):
    admin = db.query(Admin).filter(Admin.email == request.email).first()
    if admin and verify_password(request.password, admin.password):
        return {"user_id": admin.id, "role": admin.role}  # Use admin.role instead of hardcoding "admin"
    
    rider = db.query(Rider).filter(Rider.email == request.email).first()
    if rider and verify_password(request.password, rider.password):
        return {"user_id": rider.id, "role": "rider"}
    
    agent = db.query(Agent).filter(Agent.email == request.email).first()
    if agent and verify_password(request.password, agent.password):
        return {"user_id": agent.id, "role": "agent"}
    
    customer = db.query(Customer).filter(Customer.email == request.email).first()
    if customer and verify_password(request.password, customer.password):
        return {"user_id": customer.id, "role": "customer"}
    
    return None

def register_user(db: Session, request: UserRegistration):
    if db.query(Admin).filter(Admin.email == request.email).first():
        return None
    if db.query(Rider).filter(Rider.email == request.email).first():
        return None
    if db.query(Agent).filter(Agent.email == request.email).first():
        return None
    if db.query(Customer).filter(Customer.email == request.email).first():
        return None
    
    if request.role in ["rider", "agent", "admin"]:  # Include "admin" in restricted roles
        raise HTTPException(
            status_code=403,
            detail=f"Role '{request.role}' cannot be registered directly. Admins must be created by the super admin."
        )
    
    if request.role not in ["customer"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role: {request.role}. Only 'customer' role can register directly."
        )
    
    hashed_password = hash_password(request.password)
    
    if request.role == "customer":
        user = Customer(
            name=request.name,
            email=request.email,
            password=hashed_password
        )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, email=user.email, role=request.role)

def register_rider_by_admin(db: Session, request: UserRegistration):
    if db.query(Admin).filter(Admin.email == request.email).first():
        return None
    if db.query(Rider).filter(Rider.email == request.email).first():
        return None
    if db.query(Agent).filter(Agent.email == request.email).first():
        return None
    if db.query(Customer).filter(Customer.email == request.email).first():
        return None
    
    hashed_password = hash_password(request.password)
    user = Rider(
        name=request.name,
        email=request.email,
        password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, email=user.email, role="rider")

def register_agent_by_admin(db: Session, request: UserRegistration):
    if db.query(Admin).filter(Admin.email == request.email).first():
        return None
    if db.query(Rider).filter(Rider.email == request.email).first():
        return None
    if db.query(Agent).filter(Agent.email == request.email).first():
        return None
    if db.query(Customer).filter(Customer.email == request.email).first():
        return None
    
    hashed_password = hash_password(request.password)
    user = Agent(
        name=request.name,
        email=request.email,
        password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, email=user.email, role="agent")