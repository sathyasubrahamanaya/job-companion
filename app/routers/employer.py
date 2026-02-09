import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Form
from fastapi.responses import FileResponse
# FIX 1: Import 'col' to fix the .in_() type error
from sqlmodel import Session, select, col
from app.db.session import get_session
from app.db.datamodels import User, EmployerProfile, UserRole
from app.schemas.response import APIResponse
from app.dependencies import get_current_user
from app.utils.security import get_password_hash
from app.utils.vector_store import search_candidates_by_vector 
from app.db.datamodels import Job, Notification, NotificationType

router = APIRouter()

# --- 1. SIGNUP (Public) ---
@router.post("/signup", response_model=APIResponse[Dict[str, Any]])
async def employer_signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:
    
    # Check if user exists
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    try:
        # Create User with EMPLOYER role
        new_user = User(
            name=name,
            email=email,
            hashed_password=get_password_hash(password),
            role=UserRole.EMPLOYER
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={"user_id": str(new_user.user_id), "email": new_user.email},
        Message="Employer account created. Please login to onboard."
    )

# --- 2. CREATE PROFILE (Onboard) ---
@router.post("/onboard", response_model=APIResponse[Dict[str, Any]])
async def onboard_employer(
    company_name: str = Body(..., embed=True),
    company_description: str = Body(..., embed=True),
    industry: str = Body(..., embed=True),
    location: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:
    
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can create company profiles.")

    if current_user.employer_profile:
         raise HTTPException(status_code=400, detail="Employer profile already exists.")

    try:
        new_employer = EmployerProfile(
            employer_id=current_user.user_id,
            company_name=company_name,
            company_description=company_description,
            industry=industry,
            location=location
        )
        session.add(new_employer)
        session.commit()
        session.refresh(new_employer)
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={
            "user_id": str(current_user.user_id),
            "employer_profile": new_employer.model_dump()
        },
        Message="Employer profile created successfully"
    )

# --- 3. READ PROFILE (Get) ---
@router.get("/profile", response_model=APIResponse[Dict[str, Any]])
async def get_employer_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:

    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Not authorized.")

    profile = session.get(EmployerProfile, current_user.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Please onboard first.")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={
            "user": current_user.model_dump(exclude={"hashed_password"}),
            "employer_profile": profile.model_dump()
        },
        Message="Profile retrieved"
    )

# --- 4. UPDATE PROFILE (Put) ---
@router.put("/update", response_model=APIResponse[Dict[str, Any]])
async def update_employer_profile(
    company_name: Optional[str] = Body(None, embed=True),
    company_description: Optional[str] = Body(None, embed=True),
    industry: Optional[str] = Body(None, embed=True),
    location: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:

    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Not authorized.")

    profile = session.get(EmployerProfile, current_user.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    try:
        if company_name is not None: profile.company_name = company_name
        if company_description is not None: profile.company_description = company_description
        if industry is not None: profile.industry = industry
        if location is not None: profile.location = location

        session.add(profile)
        session.commit()
        session.refresh(profile)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data=profile.model_dump(),
        Message="Profile updated successfully"
    )

# --- 5. DELETE PROFILE (Delete) ---
@router.delete("/delete", response_model=APIResponse[None])
async def delete_employer_account(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Not authorized.")

    try:
        # Delete Profile first (if it exists)
        profile = session.get(EmployerProfile, current_user.user_id)
        if profile:
            session.delete(profile)
        
        # Delete User Account
        session.delete(current_user)
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

    return APIResponse[None](
        ErrorCode=0,
        Data=None,
        Message="Employer account deleted successfully"
    )
    

@router.post("/search-candidates", response_model=APIResponse[List[Dict[str, Any]]])
async def search_candidates(
    query: str = Form(...),
    limit: int = Form(10),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[List[Dict[str, Any]]]:

    if current_user.role != UserRole.EMPLOYER:
         raise HTTPException(status_code=403, detail="Not authorized. Only Employers can search for talent.")

    if not current_user.employer_profile:
        raise HTTPException(status_code=400, detail="Please complete your company profile first.")

    try:
        # 1. Perform Semantic Search (Get IDs + Skills from Qdrant)
        matches = search_candidates_by_vector(query, limit=limit)
        
        # 2. Extract IDs to query the Database
        # FIX 2: Explicitly type the list as UUIDs
        candidate_ids: List[uuid.UUID] = []
        for m in matches:
            c_id = m.get("candidate_id")
            if c_id:
                try:
                    candidate_ids.append(uuid.UUID(str(c_id)))
                except ValueError:
                    continue 

        # 3. Fetch User Names in Bulk
        # FIX 3: Use col(User.user_id) to resolve the .in_() error
        statement = select(User).where(col(User.user_id).in_(candidate_ids))
        users = session.exec(statement).all()
        
        # 4. Create a Lookup Dictionary: { uuid: "John Doe" }
        user_map = {u.user_id: u.name for u in users}
        
        # 5. Attach Names to the Result List
        # FIX 4: Explicitly type the results list
        enriched_results: List[Dict[str, Any]] = []
        
        for match in matches:
            c_id_str = match.get("candidate_id")
            if c_id_str:
                try:
                    c_uuid = uuid.UUID(str(c_id_str))
                    match["name"] = user_map.get(c_uuid, "Unknown Candidate")
                except ValueError:
                    match["name"] = "Unknown Candidate"
            
            enriched_results.append(match)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    return APIResponse[List[Dict[str, Any]]](
        ErrorCode=0,
        Data=enriched_results,
        Message="Here are the most relevant candidates."
    )

@router.get("/potential-candidates/{job_id}", response_model=APIResponse[List[Dict[str, Any]]])
async def get_potential_candidates_for_job(
    job_id: uuid.UUID,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[List[Dict[str, Any]]]:
    """
    Automatically finds the best candidates for a specific job post
    by matching the Job Description against Candidate Resumes.
    """
    
    # 1. Verification
    if current_user.role != UserRole.EMPLOYER:
         raise HTTPException(status_code=403, detail="Not authorized.")

    # 2. Fetch the Job
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    # 3. Security Check: Ensure the Employer owns this job
    if job.employer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only view candidates for your own jobs.")

    try:
        # 4. Construct the AI Search Query
        # We combine Title, Skills, and Description to create a rich semantic query vector
        query_text = f"{job.title} {', '.join(job.required_skills)} {job.description}"
        
        # 5. Perform Vector Search (Reusing your existing search logic)
        matches = search_candidates_by_vector(query_text, limit=limit)
        
        # --- ENRICHMENT LOGIC (Same as your manual search) ---
        
        # 0. Check for existing invites for this job
        statement = select(Notification).where(
            Notification.job_id == job_id,
            Notification.type == NotificationType.INVITE
        )
        existing_invites = session.exec(statement).all()
        invite_map = {inv.recipient_id: inv for inv in existing_invites}
        existing_invite_ids = set(invite_map.keys())

        # 6. Extract IDs
        candidate_ids: List[uuid.UUID] = []
        for m in matches:
            c_id = m.get("candidate_id")
            if c_id:
                try:
                    candidate_ids.append(uuid.UUID(str(c_id)))
                except ValueError:
                    continue 

        # 7. Fetch Names
        statement = select(User).where(col(User.user_id).in_(candidate_ids))
        users = session.exec(statement).all()
        user_map = {u.user_id: u.name for u in users}
        
        # 8. Attach Names
        enriched_results: List[Dict[str, Any]] = []
        for match in matches:
            c_uuid = None
            c_id_str = match.get("candidate_id")
            if c_id_str:
                try:
                    c_uuid = uuid.UUID(str(c_id_str))
                    match["name"] = user_map.get(c_uuid, "Unknown Candidate")
                except ValueError:
                    match["name"] = "Unknown Candidate"
            
            # 9. Set invitation info
            match["is_invited"] = (c_uuid is not None) and (c_uuid in existing_invite_ids)
            if match["is_invited"] and c_uuid:
                match["invitation_id"] = str(invite_map[c_uuid].notification_id)
                match["invitation_status"] = invite_map[c_uuid].invitation_status
                match["memo_candidate"] = invite_map[c_uuid].memo_candidate
                match["memo_employer"] = invite_map[c_uuid].memo_employer
            
            enriched_results.append(match)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Matching failed: {str(e)}")

    return APIResponse[List[Dict[str, Any]]](
        ErrorCode=0,
        Data=enriched_results,
        Message=f"Found {len(enriched_results)} potential candidates for '{job.title}'."
    )

@router.post("/invite/{candidate_id}/{job_id}", response_model=APIResponse[None])
async def invite_candidate(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    """
    Sends an interview invitation to a candidate for a specific job.
    """
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can send invites.")

    # 1. Verify Job Ownership
    job = session.get(Job, job_id)
    if not job or job.employer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Job not found or not owned by you.")

    # 2. Verify Candidate Exists
    candidate = session.get(User, candidate_id)
    if not candidate or candidate.role != UserRole.CANDIDATE:
         raise HTTPException(status_code=404, detail="Candidate not found.")

    # 3. Create Notification
    try:
        new_notification = Notification(
            recipient_id=candidate_id,
            sender_id=current_user.user_id,
            job_id=job_id,
            type=NotificationType.INVITE,
            title="Interview Invitation",
            message=f"You have been invited to interview for the position: {job.title} at {current_user.employer_profile.company_name if current_user.employer_profile else 'a company'}."
        )
        session.add(new_notification)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send invite: {str(e)}")

    return APIResponse[None](
        ErrorCode=0,
        Data=None,
        Message=f"Interview invitation sent to {candidate.name}."
    )

@router.get("/resume/{candidate_id}", response_class=FileResponse)
async def get_candidate_resume(
    candidate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Serves the resume PDF for a specific candidate.
    """
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can view resumes.")

    from app.db.datamodels import CandidateProfile
    profile = session.get(CandidateProfile, candidate_id)
    if not profile or not profile.resume_id:
        raise HTTPException(status_code=404, detail="Resume not found.")

    import os
    if not os.path.exists(profile.resume_id):
        raise HTTPException(status_code=404, detail="Resume file not found on server.")

    return FileResponse(
        path=profile.resume_id,
        filename=os.path.basename(profile.resume_id),
        media_type="application/pdf"
    )

@router.post("/remind/{candidate_id}/{job_id}", response_model=APIResponse[None])
async def remind_candidate(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    """
    Sends a reminder notification to a candidate about an existing interview invitation.
    """
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only employers can send reminders.")

    # 1. Verify Job Ownership
    job = session.get(Job, job_id)
    if not job or job.employer_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Job not found or not owned by you.")

    # 2. Verify Candidate Exists
    candidate = session.get(User, candidate_id)
    if not candidate or candidate.role != UserRole.CANDIDATE:
         raise HTTPException(status_code=404, detail="Candidate not found.")

    # 3. Create Reminder Notification
    try:
        new_notification = Notification(
            recipient_id=candidate_id,
            sender_id=current_user.user_id,
            job_id=job_id,
            type=NotificationType.REMINDER,
            title="Interview Reminder",
            message=f"Reminder: You have an outstanding interview invitation for {job.title} at {current_user.employer_profile.company_name if current_user.employer_profile else 'our company'}."
        )
        session.add(new_notification)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send reminder: {str(e)}")

    return APIResponse[None](
        ErrorCode=0,
        Data=None,
        Message=f"Reminder sent to {candidate.name}."
    )

@router.put("/notifications/{notification_id}/memo", response_model=APIResponse[None])
async def update_employer_memo(
    notification_id: uuid.UUID,
    memo: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:
    """
    Allows employer to update their memo on an invitation.
    """
    notification = session.get(Notification, notification_id)
    if not notification or notification.sender_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    
    notification.memo_employer = memo
    notification.is_read = False  # Mark as unread so candidate sees the update
    session.add(notification)
    session.commit()
    return APIResponse[None](ErrorCode=0, Data=None, Message="Employer memo updated.")