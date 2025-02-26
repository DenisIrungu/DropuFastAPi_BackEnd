from sqlalchemy.orm import Session
from models import Customer
from schemas import CustomerCreate

def create_customer(db: Session, customer_data: CustomerCreate):
    """Create a new customer."""
    new_customer = Customer(
        name=customer_data.name,
        email=customer_data.email,
        password=customer_data.password,
        address=customer_data.address
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

def get_customers(db: Session):
    """Retrieve all customers."""
    return db.query(Customer).all()
