from sqlalchemy.orm import Session
from models import Admin
from schemas import AdminCreate

def create_admin(db: Session, admin_data: AdminCreate):
    """Create a new admin."""
    new_admin = Admin(
        name=admin_data.name,
        email=admin_data.email,
        password=admin_data.password 
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

def get_admins(db: Session):
    """Retrieve all admins."""
    return db.query(Admin).all()
