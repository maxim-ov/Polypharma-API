from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)


class Drug(Base):
    __tablename__ = "drugs"

    id = Column(String, primary_key=True, index=True)  # DDInterID
    name = Column(String, nullable=False, index=True)
    rxcui = Column(String, index=True, nullable=True)


class DrugInteraction(Base):
    __tablename__ = "drug_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    drug_a_id = Column(String, ForeignKey("drugs.id"), nullable=False, index=True)
    drug_b_id = Column(String, ForeignKey("drugs.id"), nullable=False, index=True)
    level = Column(String, nullable=False) # Minor, Moderate, Major
    category = Column(String, nullable=False) # A, B, D, H, L, P, R, V

    # Define relationships to Drug (Optional but helpful if using ORM joins)
    drug_a = relationship("Drug", foreign_keys=[drug_a_id])
    drug_b = relationship("Drug", foreign_keys=[drug_b_id])


class DrugLog(Base):
    __tablename__ = "drug_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    drug_id = Column(String, ForeignKey("drugs.id"), nullable=False, index=True)
    dosage = Column(String, nullable=False)
    datetime = Column(DateTime, default=datetime.utcnow, nullable=False)

    drug = relationship("Drug")
