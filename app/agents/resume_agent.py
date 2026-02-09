from agno.agent import Agent
from agno.models.google import Gemini
from pydantic import BaseModel, Field
from app.config import settings

# --- Data Model for Structured Output ---
# This must match the fields in your SQL Database (CandidateProfile)
class ResumeAnalysis(BaseModel):
    name: str = Field(description="Candidate's full name")
    email: str = Field(description="Candidate's email address")
    skills: list[str] = Field(description="List of technical skills (e.g., Python, SQL)")
    experience_years: int = Field(description="Total years of experience (estimate if not explicit)")
    educations: list[str] = Field(description="List of degrees and universities")
    preferred_roles: list[str] = Field(description="3-5 job titles this candidate is best suited for")
    preferred_locations: list[str] = Field(description="Locations mentioned or 'Remote' if applicable")
    summary: str = Field(description="A brief 2-sentence summary of the candidate's profile")

# --- Agent Factory ---
def get_resume_agent() -> Agent:
    return Agent(
        model=Gemini(id=settings.GEMINI_MODEL_NAME, api_key=settings.GEMINI_API_KEY),
        description="You are an expert technical recruiter and resume parser.",
        instructions=[
            "Analyze the provided resume text.",
            "Extract the details strictly into the expected JSON format.",
            "Normalize skills (e.g., 'ReactJS' -> 'React').",
            "If a field is missing, use reasonable defaults or empty strings.",
        ],
        # Using output_schema as you requested
        output_schema=ResumeAnalysis, 
    )