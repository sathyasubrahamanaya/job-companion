from typing import List, Optional
from pydantic import BaseModel

# --- 1. SHARED MODELS ---
class WorkExperience(BaseModel):
    title: str
    company: str
    duration: str
    description: List[str]  # UI sends rough bullets, AI returns polished ones

class Education(BaseModel):
    degree: str
    institution: str
    year: str

class Project(BaseModel):
    name: str
    description: str
    tech_stack: List[str]

# --- 2. INPUT SCHEMA (What the UI sends) ---
class ResumeInput(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    # Users often struggle to write a summary, so we make this optional
    # and let the AI generate it from their experience if missing.
    professional_summary: Optional[str] = None 
    skills: List[str]
    experience: List[WorkExperience]
    education: List[Education]
    projects: List[Project]

# --- 3. OUTPUT SCHEMA (What the AI produces) ---
class ResumeData(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    professional_summary: str # AI MUST generate this if missing
    skills: List[str]
    experience: List[WorkExperience]
    education: List[Education]
    projects: List[Project]
    

from typing import List, Optional
from pydantic import BaseModel

# --- 1. SHARED MODELS ---
class WorkExperience(BaseModel):
    title: str
    company: str
    duration: str
    description: List[str]  # UI sends rough bullets, AI returns polished ones

class Education(BaseModel):
    degree: str
    institution: str
    year: str

class Project(BaseModel):
    name: str
    description: str
    tech_stack: List[str]

# --- 2. INPUT SCHEMA (What the UI sends) ---
class ResumeInput(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    photo_url: Optional[str] = None  # <--- NEW FIELD
    professional_summary: Optional[str] = None 
    skills: List[str]
    experience: List[WorkExperience]
    education: List[Education]
    projects: List[Project]

# --- 3. OUTPUT SCHEMA ---
class ResumeData(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    photo_url: Optional[str] = None  # <--- NEW FIELD
    professional_summary: str
    skills: List[str]
    experience: List[WorkExperience]
    education: List[Education]
    projects: List[Project]