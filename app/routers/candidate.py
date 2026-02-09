import os
import uuid
import shutil
from typing import Any, cast, Dict, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Body
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.datamodels import User, CandidateProfile, UserRole, Notification
from app.utils.file_parser import extract_text_from_pdf
from app.agents.resume_agent import get_resume_agent, ResumeAnalysis 
from app.schemas.response import APIResponse 
from app.utils.security import get_password_hash
from app.dependencies import get_current_user
from app.utils.vector_store import search_jobs_by_vector  
from typing import List
from app.utils.vector_store import search_jobs_by_vector, upsert_candidate_embedding

router = APIRouter()

# --- 1. SIGNUP (Public) ---
@router.post("/signup", response_model=APIResponse[Dict[str, Any]])
async def candidate_signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]: 
    
    # 1. Check if user exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    # 2. Process Resume File
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    resume_text = await extract_text_from_pdf(file)
    if not resume_text.strip():
         raise HTTPException(status_code=400, detail="The PDF appears to be empty.")

    # 3. AI Extraction
    try:
        agent = get_resume_agent()
        response = agent.run(f"Extract data from this resume:\n\n{resume_text}") # type: ignore
    except Exception as e:
        error_msg = str(e).lower()
        # Check for quota exceeded errors
        if "quota" in error_msg or "rate limit" in error_msg or "resource exhausted" in error_msg:
            raise HTTPException(
                status_code=503, 
                detail="AI service quota exceeded. Please try again later or contact support. The service will be available once the API quota is renewed."
            )
        raise HTTPException(status_code=500, detail=f"AI Engine Failure: {str(e)}")
    
    # FIX: 'response' is RunOutput type, so it's not None. We only check content.
    if response.content is None:
        raise HTTPException(status_code=500, detail="AI failed to process resume.")
    
    parsed_data = cast(ResumeAnalysis, response.content)

    # 4. Save to Database & Disk
    file_path: Optional[str] = None  # FIX: Initialize scope variable
    
    try:
        # A. Create User with HASHED PASSWORD
        new_user = User(
            name=name, 
            email=email, 
            hashed_password=get_password_hash(password),
            role=UserRole.CANDIDATE
        )
        session.add(new_user)
        session.flush()
        # B. Save File to Disk
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{new_user.user_id}_{file.filename}"
        
        await file.seek(0)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # C. Create Candidate Profile
        new_profile = CandidateProfile(
            candidate_id=new_user.user_id,
            skills=parsed_data.skills,
            experience_years=parsed_data.experience_years,
            educations=parsed_data.educations,
            preferred_roles=parsed_data.preferred_roles,
            preferred_locations=parsed_data.preferred_locations,
            resume_id=file_path 
        )
        session.add(new_profile)
        session.commit()
        upsert_candidate_embedding(
            candidate_id=new_user.user_id,
            skills=parsed_data.skills,
            experience_years=parsed_data.experience_years,
            roles=parsed_data.preferred_roles,
            locations=parsed_data.preferred_locations
        )
        
    except Exception as e:
        session.rollback()
        # FIX: Safe cleanup check
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0, 
        Data={"user_id": str(new_user.user_id), "email": new_user.email}, 
        Message="Candidate registered successfully"
    )

# --- 2. GET PROFILE (Protected) ---
@router.get("/profile", response_model=APIResponse[Dict[str, Any]])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:
    
    if current_user.role != UserRole.CANDIDATE:
         raise HTTPException(status_code=403, detail="Not authorized as Candidate")

    profile = session.get(CandidateProfile, current_user.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={
            "user": current_user.model_dump(exclude={"hashed_password"}), 
            "profile": profile.model_dump()
        },
        Message="Profile retrieved"
    )

# --- 3. UPDATE RESUME (Protected) ---
@router.put("/update-resume", response_model=APIResponse[None])
async def update_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    
    if current_user.role != UserRole.CANDIDATE:
         raise HTTPException(status_code=403, detail="Not authorized")

    if not file.filename:
         raise HTTPException(status_code=400, detail="Invalid filename")

    # 1. Parse New Resume
    resume_text = await extract_text_from_pdf(file)
    agent = get_resume_agent()
    
    try:
        response = agent.run(f"Extract data from this resume:\n\n{resume_text}") #type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    # FIX: Removed 'if response is None' check
    if response.content is None:
         raise HTTPException(status_code=500, detail="AI failed to parse new resume")
    
    new_data = cast(ResumeAnalysis, response.content)

    # 2. Update Database
    profile = session.get(CandidateProfile, current_user.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found to update")

    try:
        # Update fields
        profile.skills = new_data.skills
        profile.experience_years = new_data.experience_years
        profile.educations = new_data.educations
        profile.preferred_roles = new_data.preferred_roles
        profile.preferred_locations = new_data.preferred_locations
        
        # Overwrite file
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{current_user.user_id}_{file.filename}"
        
        await file.seek(0)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        profile.resume_id = file_path
        
        session.add(profile)
        session.commit()
        upsert_candidate_embedding(
            candidate_id=current_user.user_id,
            skills=new_data.skills,
            experience_years=new_data.experience_years,
            roles=new_data.preferred_roles,
            locations=new_data.preferred_locations
        )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    return APIResponse[None](
        ErrorCode=0, 
        Data=None, 
        Message="Resume and Profile updated successfully"
    )
    
    
    
@router.post("/search-jobs", response_model=APIResponse[List[Dict[str, Any]]])
async def search_jobs(
    query: str = Form(...),
    limit: int = Form(10), # Optional limit parameter
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[List[Dict[str, Any]]]:

    if current_user.role != UserRole.CANDIDATE:
         raise HTTPException(status_code=403, detail="Not authorized as Candidate")

    try:
        # Perform Hybrid Search (Semantic + Keyword)
        matches = search_jobs_by_vector(query, limit=limit)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    return APIResponse[List[Dict[str, Any]]](
        ErrorCode=0,
        Data=matches,
        Message="Here are the most relevant jobs based on your query."
    )

@router.get("/notifications", response_model=APIResponse[List[Notification]])
async def get_notifications(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[List[Notification]]:
    """
    Fetches all notifications for the current candidate.
    """
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Only candidates can view notifications.")

    statement = select(Notification).where(Notification.recipient_id == current_user.user_id).order_by(Notification.created_at.desc())
    results = session.exec(statement).all()
    
    return APIResponse[List[Notification]](
        ErrorCode=0,
        Data=list(results),
        Message="Notifications retrieved."
    )

@router.put("/notifications/{notification_id}/read", response_model=APIResponse[None])
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    """
    Marks a specific notification as read.
    """
    notification = session.get(Notification, notification_id)
    if not notification or notification.recipient_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Notification not found.")

    notification.is_read = True
    session.add(notification)
    session.commit()
    return APIResponse[None](
        ErrorCode=0,
        Data=None,
        Message="Notification marked as read."
    )

@router.put("/notifications/{notification_id}/accept", response_model=APIResponse[None])
async def accept_invitation(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    from app.db.datamodels import InvitationStatus
    notification = session.get(Notification, notification_id)
    if not notification or notification.recipient_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    
    notification.invitation_status = InvitationStatus.ACCEPTED
    session.add(notification)
    session.commit()
    return APIResponse[None](ErrorCode=0, Data=None, Message="Invitation accepted.")

@router.put("/notifications/{notification_id}/reject", response_model=APIResponse[None])
async def reject_invitation(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    from app.db.datamodels import InvitationStatus
    notification = session.get(Notification, notification_id)
    if not notification or notification.recipient_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    
    notification.invitation_status = InvitationStatus.REJECTED
    session.add(notification)
    session.commit()
    return APIResponse[None](ErrorCode=0, Data=None, Message="Invitation rejected.")

@router.put("/notifications/{notification_id}/memo", response_model=APIResponse[None])
async def update_candidate_memo(
    notification_id: uuid.UUID,
    memo: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    notification = session.get(Notification, notification_id)
    if not notification or notification.recipient_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    
    notification.memo_candidate = memo
    notification.is_read = False  # Mark as unread so employer sees the update
    session.add(notification)
    session.commit()
    return APIResponse[None](ErrorCode=0, Data=None, Message="Memo updated.")