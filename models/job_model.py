import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import UUID, Boolean, Column, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JobModel(Base):
    __tablename__ = "jobs"

    job_id = Column(UUID, primary_key=True, default=uuid.uuid4)
    previous_version_id = Column(UUID)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    status = Column(Text, nullable=False, default="active")
    job_title = Column(Text, nullable=False)
    job_description = Column(Text, nullable=False)
    budget_min = Column(Integer)
    budget_max = Column(Integer)
    budget_currency = Column(Text)
    location = Column(Text)
    company_name = Column(Text)
    employment_type = Column(Text)
    required_skills = Column(Text, nullable=False)
    is_bachelor = Column(Boolean, default=False)
    is_master = Column(Boolean, default=False)
    bachelor_program = Column(Text)
    master_program = Column(Text)
    tenure = Column(Integer)
    job_embedding = Column(Vector(32), nullable=False)
