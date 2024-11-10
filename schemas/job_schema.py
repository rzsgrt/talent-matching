from pydantic import BaseModel
from typing import List


class Budget(BaseModel):
    min: int
    max: int
    currency: str


class JobCreate(BaseModel):
    job_title: str
    job_description: str
    budget: Budget
    location: str
    company_name: str
    employment_type: str
    required_skills: List[str]
