from agno.agent import Agent
from agno.models.google import Gemini
from agno.db.sqlite import SqliteDb
from app.config import settings

# Initialize the persistent database connection
agent_db = SqliteDb(db_file="agent_memory.db")

def get_interviewer_agent(session_id: str, user_id: str, job_title: str, job_description: str, candidate_summary: str) -> Agent:
    """
    Creates an Interviewer Agent with persistent memory and learning capabilities.
    """
    return Agent(
        model=Gemini(id=settings.GEMINI_MODEL_NAME, api_key=settings.GEMINI_API_KEY),
        description="You are an expert Technical Recruiter and Hiring Manager.",
        
        # --- IDENTITY & MEMORY ---
        session_id=session_id,          # Binds this agent instance to the specific chat session
        user_id=user_id,                # Binds the memory to the specific candidate
        db=agent_db,                    # Persistent storage (SQLite)
        
        # --- CONTEXT MANAGEMENT ---
        add_history_to_context=True,    # Auto-inject chat history into prompts
        num_history_runs=3,             # Only remember the last 3 exchanges (Efficiency)
        
        # --- LEARNING ---
        # "learning=True" enables the agent to extract and save facts about the user 
        # (e.g., "User knows Python", "User prefers remote work") into a vector memory.
        learning=True,
        
        instructions=[
            f"Your name is Jobby"
            f"You are interviewing a candidate for the role of {job_title}.",
            f"Job Description: {job_description}",
            f"Candidate Summary: {candidate_summary}",
            "---",
            "Your Goal: Assess the candidate's technical skills and cultural fit.",
            "Guidelines:",
            "1. Ask ONE question at a time.",
            "2. Start by asking them to introduce themselves.",
            "3. If they give a vague answer, ask follow-up questions.",
            "4. Be professional but encouraging.",
            "5. Keep your responses concise (under 3 sentences)."
        ],
      
    )