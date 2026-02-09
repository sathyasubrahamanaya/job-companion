import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from app.db.session import get_session
from app.db.datamodels import User, UserRole, Job, CandidateProfile, InterviewSession, ChatMessage
from app.schemas.response import APIResponse
from app.dependencies import get_current_user
from app.agents.interview_agent import get_interviewer_agent

router = APIRouter()

# --- 1. START INTERVIEW ---
@router.post("/start/{job_id}", response_model=APIResponse[Dict[str, Any]])
async def start_interview(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:
    
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Only candidates can start interviews.")

    # A. Fetch Context
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    profile = session.get(CandidateProfile, current_user.user_id)
    if not profile:
        raise HTTPException(status_code=400, detail="Please upload your resume first.")

    # B. Create Session Record
    new_session = InterviewSession(candidate_id=current_user.user_id, job_id=job_id)
    session.add(new_session)
    session.commit()
    session.refresh(new_session)

    # C. Initialize Agent (With Session & User ID)
    candidate_summary = f"The Candidate background is {profile.model_dump()}"
    
    agent = get_interviewer_agent(
        session_id=str(new_session.session_id),
        user_id=str(current_user.user_id), # <--- Bind memory to this user
        job_title=job.title,
        job_description=job.description,
        candidate_summary=candidate_summary
    )
    
    try:
        # We don't need to manually inject history or context anymore.
        # The agent is "fresh" here, so we just give the trigger command.
        ai_response = agent.run("Start the interview. Introduce yourself and ask the first question.") #type: ignore
        ai_content = str(ai_response.content) if ai_response and ai_response.content else "Hello! Let's begin."
    except Exception:
        ai_content = "Hello! I am ready to interview you. Please introduce yourself."

    # D. Save AI Message (For UI Display)
    welcome_msg = ChatMessage(
        session_id=new_session.session_id,
        role="assistant",
        content=ai_content
    )
    session.add(welcome_msg)
    session.commit()

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={
            "session_id": str(new_session.session_id),
            "message": ai_content
        },
        Message="Interview started"
    )

# --- 2. SEND MESSAGE ---
@router.post("/chat/{session_id}", response_model=APIResponse[Dict[str, Any]])
async def chat_interaction(
    session_id: uuid.UUID,
    user_message: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:
    
    # A. Validate Session
    interview_session = db.get(InterviewSession, session_id)
    if not interview_session or interview_session.candidate_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    # B. Save User Message (For UI Display)
    new_user_msg = ChatMessage(session_id=session_id, role="user", content=user_message)
    db.add(new_user_msg)
    db.commit()

    # C. Reconstruct Agent
    job = db.get(Job, interview_session.job_id)
    profile = db.get(CandidateProfile, current_user.user_id)
    
    if not job or not profile:
         raise HTTPException(status_code=400, detail="Data missing.")

    candidate_summary = f"Skills: {profile.skills}."
    
    # D. Wake up the Agent (Same IDs = Same Memory)
    agent = get_interviewer_agent(
        session_id=str(session_id),          # <--- Finds the previous chat history
        user_id=str(current_user.user_id),   # <--- Finds the user's learned facts
        job_title=job.title,
        job_description=job.description,
        candidate_summary=candidate_summary
    )
    
    try:
        # Simple run() call. The agent pulls history from SqliteDb automatically.
        ai_response = agent.run(user_message) #type: ignore
        ai_content = str(ai_response.content) if ai_response and ai_response.content else "Could you please repeat that?"
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

    # E. Save AI Response (For UI Display)
    new_ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_content)
    db.add(new_ai_msg)
    db.commit()

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={"response": ai_content},
        Message="Message sent"
    )