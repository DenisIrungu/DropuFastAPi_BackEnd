from sqlalchemy.orm import Session
from models import Agent
from schemas import AgentCreate

def create_agent(db: Session, agent_data: AgentCreate):
    """Create a new agent."""
    new_agent = Agent(
        name=agent_data.name,
        email=agent_data.email,
        password=agent_data.password,
        station_location=agent_data.station_location
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent

def get_agents(db: Session):
    """Retrieve all agents."""
    return db.query(Agent).all()
