from fastapi import FastAPI
from database import Base, engine
from routes import auth_router, admin_router, rider_router, agent_router, customer_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(rider_router, prefix="/rider", tags=["Rider"])
app.include_router(agent_router, prefix="/agent", tags=["Agent"])
app.include_router(customer_router, prefix="/customer", tags=["Customer"])

@app.get("/")
def home():
    return {"message": "Welcome to Dropu Logistics Management System API"}
