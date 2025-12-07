from sqlalchemy import Column, Integer, String, Float
from app.db import Base

class LeadORM(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    restaurant_type = Column(String, nullable=False)
    city = Column(String, nullable=False)
    lat = Column(Float, nullable=True)
    longit = Column(Float, nullable=True)
    