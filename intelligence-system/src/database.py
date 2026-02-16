from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class FireRiskReading(Base):
    __tablename__ = "fire_risk_readings"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    risk_score = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
