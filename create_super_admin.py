from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import Admin
from utils.security import hash_password

# Create the database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a database session
db: Session = SessionLocal()

# Check if a super admin already exists
if db.query(Admin).filter(Admin.role == "super_admin").first():
    print("Super admin already exists. Exiting.")
    db.close()
    exit()

# Super admin details
super_admin_email = "superkihara@gmail.com"
super_admin_password = "1234"  
super_admin_name = "kihara"

# Hash the password
hashed_password = hash_password(super_admin_password)

# Create the super admin
super_admin = Admin(
    name=super_admin_name,
    email=super_admin_email,
    password=hashed_password,
    role="super_admin"
)

# Add to the database
db.add(super_admin)
db.commit()
db.refresh(super_admin)

print(f"Super admin created successfully with email: {super_admin_email}")
db.close()