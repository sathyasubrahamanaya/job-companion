from pydantic import BaseModel
from datetime import datetime
from typing import List
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    CANDIDATE = "CANDIDATE"
    EMPLOYER = "EMPLOYER"
    ADMIN = "ADMIN"


class JobType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    INTERNSHIP = "INTERNSHIP"


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"


class SenderType(str, Enum):
    USER = "USER"
    AI = "AI"


class DifficultyLevel(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ChatType(str,Enum):
    INTERVIEW = "INTERVIEW",
    CASUAL  = "CASUAL" 
      








class ChatHistory(BaseModel):
    chat_id:int
    ai_message:str
    user_message:str
    chat_time:datetime
    chat_type:ChatType




class CandidateProfile(BaseModel):
    candidate_id: str
    resume_id: Optional[str] = None
    skills: List[str]
    experience_years: int
    educations: List[str]
    preferred_roles: List[str]
    preferred_locations: List[str]
    expected_salary: Optional[float] = None



class ShortListedCandidates(BaseModel):
    candidate_id :str 
    employer_id:str    


class EmployerProfile(BaseModel):
    employer_id: str
    company_name: str
    company_description: str
    industry: str
    location: str


class Job(BaseModel):
    job_id: str
    employer_id: str
    title: str
    description: str
    required_skills: List[str]
    experience_required: int
    location: str
    salary_range: Optional[str] = None
    job_type: JobType
    created_at: datetime


class JobApplication(BaseModel):
    application_id: str
    job_id: str
    candidate_id: str
    status: ApplicationStatus
    ai_match_score: float
    applied_at: datetime


class JobRecommendation(BaseModel):
    recommendation_id: str
    job_id: str
    candidate_id: str
    match_score: float
    reason: str
    created_at: datetime


class User(BaseModel):
    user_id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    profile_image: Optional[str] = None
    created_at: datetime