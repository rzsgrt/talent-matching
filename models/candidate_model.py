import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import UUID, Boolean, Column, Date, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CandidateModel(Base):
    __tablename__ = "candidates"

    candidate_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text)
    birthdate = Column(Date)
    email = Column(Text, nullable=False)
    phone = Column(Text)
    address = Column(Text)
    skills = Column(Text, nullable=False)

    # Current Experience
    current_company = Column(Text)
    current_job_role = Column(Text)  # Using quoted column name
    current_start_date = Column(Date)
    current_end_date = Column(Date)

    # Previous Experience
    previous_company = Column(Text)
    previous_job_role = Column(Text)
    previous_start_date = Column(Date)
    previous_end_date = Column(Date)

    # Education
    bachelor_institution = Column(Text)
    bachelor_degree = Column(Text)
    bachelor_graduation_year = Column(Integer)
    has_bachelor = Column(Boolean, default=False)

    master_institution = Column(Text)
    master_degree = Column(Text)
    master_graduation_year = Column(Integer)
    has_master = Column(Boolean, default=False)

    candidate_tenure = Column(Integer)
    candidate_embedding = Column(Vector(32), nullable=False)
