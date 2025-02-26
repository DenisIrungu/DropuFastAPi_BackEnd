from sqlalchemy.orm import Session
from models import Rider
from schemas import RiderCreate

def create_rider(db: Session, rider_data: RiderCreate):
    """Create a new rider."""
    new_rider = Rider(
        name=rider_data.name,
        email=rider_data.email,
        password=rider_data.password,
        vehicle_number=rider_data.vehicle_number
    )
    db.add(new_rider)
    db.commit()
    db.refresh(new_rider)
    return new_rider

def get_riders(db: Session):
    """Retrieve all riders."""
    return db.query(Rider).all()
