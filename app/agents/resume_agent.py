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




from agno.agent import Agent
from agno.models.google import Gemini
from app.config import settings
from app.schemas.resume import ResumeData

def get_resume_builder_agent() -> Agent:
    return Agent(
        model=Gemini(id=settings.GEMINI_MODEL_NAME, api_key=settings.GEMINI_API_KEY),
        description="You are an expert Executive Resume Writer and Career Coach.",
        instructions=[
            "You will receive raw resume data in JSON format.",
            "Your task is to POLISH and ENHANCE this data into a top-tier professional resume.",
            "1. PROFESSIONAL SUMMARY: If provided, improve its flow. If missing, generate a strong 3-sentence summary based on the experience and skills provided.",
            "2. EXPERIENCE: Rewrite the user's rough bullet points into impactful, action-oriented achievements (e.g., change 'Fixed bugs' to 'Resolved critical production issues, reducing downtime by 15%').",
            "3. SKILLS: Group or refine the skills list if necessary.",
            "4. TONE: Ensure a consistent, professional, and active voice throughout.",
            "5. OUTPUT: Return strictly typed JSON matching the ResumeData schema.",
            "6. Do not invent new jobs or degrees. Only enhance the phrasing of what is provided."
            "7. IMPORTANT: If the input JSON contains a 'photo_url', you MUST include it exactly as is in the output JSON. Do not alter or remove the URL."
        
        ],
        output_schema=ResumeData, 
    )