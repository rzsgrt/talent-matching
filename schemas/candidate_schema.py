from datetime import date
from typing import List, Optional
from pydantic import BaseModel


class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    year_of_graduation: Optional[int] = None


class CandidateCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate: Optional[date] = None
    age: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[List[str]] = None
    experiences: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None
