from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime,Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from database import Base


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    profile_picture = Column(String(255), nullable=True) 
    last_login = Column(DateTime, nullable=True)
    preferences = Column(JSON, nullable=True, default={})

class Rider(Base):
    __tablename__ = "riders"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    vehicle_number = Column(String(50), unique=True, nullable=True)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    station_location = Column(String(255), nullable=True)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    
class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=False)
    urgency = Column(Boolean, default=False)  
    timestamp = Column(DateTime, default=datetime.utcnow)  
    status = Column(String(20), default="open")

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_type = Column(String(20), nullable=False) 
    message = Column(String(1000), nullable=False)  
    timestamp = Column(DateTime, default=datetime.utcnow)
