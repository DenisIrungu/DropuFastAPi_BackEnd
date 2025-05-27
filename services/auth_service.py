import os
from sqlalchemy.orm import Session
from models import Admin, Rider, Agent, Customer, ResetToken
from schemas.auth_schema import AuthLogin, UserRegistration, UserResponse, RiderRegistration
from utils.security import hash_password, verify_password, generate_random_password
from utils.email_service import send_welcome_email
from fastapi import HTTPException
from datetime import datetime, timedelta

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
    
    if request.role in ["rider", "agent", "admin"]:
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

def register_rider_by_admin(db: Session, request: RiderRegistration, admin_id: int):
    # Check for duplicate email across all user types
    if db.query(Admin).filter(Admin.email == request.email).first():
        return None
    if db.query(Rider).filter(Rider.email == request.email).first():
        return None
    if db.query(Agent).filter(Agent.email == request.email).first():
        return None
    if db.query(Customer).filter(Customer.email == request.email).first():
        return None

    # Handle file uploads
    static_dir = "static/uploads/riders"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    timestamp = int(datetime.utcnow().timestamp())
    temp_id = db.query(Rider).count() + 1

    files = [
        (request.id_document, "id_document"),
        (request.driving_license, "driving_license"),
        (request.insurance, "insurance")
    ]
    file_paths = {}
    for file, file_type in files:
        filename = f"rider-{temp_id}-{file_type}-{timestamp}.pdf"
        file_path = os.path.join(static_dir, filename)
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        file_paths[file_type] = f"/{file_path}"

    # Generate temporary password
    temp_password = generate_random_password()
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # Create rider record
    rider = Rider(
        name=f"{request.first_name} {request.last_name}",
        email=request.email,
        password=hash_password(temp_password),
        bike_number=request.plate_number,
        phone_number=request.phone_number,
        bike_model=request.bike_model,
        bike_color=request.bike_color,
        license=request.license,
        id_document=file_paths["id_document"],
        driving_license=file_paths["driving_license"],
        insurance=file_paths["insurance"],
        emergency_contact_name=request.emergency_contact_name,
        emergency_contact_phone=request.emergency_contact_phone,
        emergency_contact_relationship=request.emergency_contact_relationship,
        created_by=admin_id,
        status="active"
    )
    db.add(rider)
    db.flush()

    # Store temporary password
    reset_token = ResetToken(
        rider_id=rider.id,
        token=temp_password,
        expires_at=expires_at
    )
    db.add(reset_token)
    db.commit()
    db.refresh(rider)

    # Send welcome email with updated reset link
    reset_link = f"https://yourapp.com/rider/reset-password?token={temp_password}"
    send_welcome_email(rider.email, rider.name, temp_password, reset_link)

    return UserResponse(
        id=rider.id,
        email=rider.email,
        role="rider",
        message="Saved successfully"
    )

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

def resend_rider_verification_email(db: Session, rider_email: str, admin_id: int):
    # Check if the rider exists
    rider = db.query(Rider).filter(Rider.email == rider_email).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    # Generate a new temporary password
    temp_password = generate_random_password()
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # Delete any existing reset tokens for this rider
    db.query(ResetToken).filter(ResetToken.rider_id == rider.id).delete()
    db.commit()

    # Create a new reset token
    reset_token = ResetToken(
        rider_id=rider.id,
        token=temp_password,
        expires_at=expires_at
    )
    db.add(reset_token)

    # Update rider's password with the new temporary password
    rider.password = hash_password(temp_password)
    db.commit()
    db.refresh(rider)

    # Send welcome email with the new reset link
    reset_link = f"https://yourapp.com/rider/reset-password?token={temp_password}"
    if not send_welcome_email(rider.email, rider.name, temp_password, reset_link):
        raise HTTPException(status_code=500, detail="Failed to send verification email")

    return UserResponse(
        id=rider.id,
        email=rider.email,
        role="rider",
        message="Verification email resent successfully"
    )