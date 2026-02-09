import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.datamodels import Job, JobType, User, UserRole
from app.schemas.response import APIResponse
from app.dependencies import get_current_user
from app.utils.vector_store import upsert_job_embedding, delete_job_embedding
router = APIRouter()

# --- 1. CREATE (POST) ---
@router.post("/post", response_model=APIResponse[Dict[str, Any]])
async def post_job(
    title: str = Body(..., embed=True),
    description: str = Body(..., embed=True),
    required_skills: List[str] = Body(..., embed=True),
    experience_required: int = Body(..., embed=True),
    location: str = Body(..., embed=True),
    job_type: JobType = Body(..., embed=True),
    salary_range: str = Body(None, embed=True),
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:

    # A. Verification
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Only Employers can post jobs.")
        
    if not current_user.employer_profile:
        raise HTTPException(status_code=400, detail="Complete your Company Profile first.")

    try:
        # B. Create Job Record
        new_job = Job(
            employer_id=current_user.user_id, # Link to logged-in user
            title=title,
            description=description,
            required_skills=required_skills,
            experience_required=experience_required,
            location=location,
            job_type=job_type,
            salary_range=salary_range
        )
        session.add(new_job)
        session.commit()
        session.refresh(new_job)
        
        upsert_job_embedding(
            job_id=new_job.job_id,
            title=new_job.title,
            description=new_job.description,
            skills=new_job.required_skills,
            extra_payload={
                "location": new_job.location,
                "salary": new_job.salary_range,
                "job_type": new_job.job_type.value
            }
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to post job: {str(e)}")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={"job_id": str(new_job.job_id), "title": new_job.title},
        Message="Job posted successfully"
    )

# --- 2. READ ALL (GET) - For the Employer ---
@router.get("/my-jobs", response_model=APIResponse[List[Dict[str, Any]]])
async def get_my_jobs(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[List[Dict[str, Any]]]:
    
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Not authorized.")

    try:
        # Fetch jobs where employer_id matches current user
        statement = select(Job).where(Job.employer_id == current_user.user_id)
        results = session.exec(statement).all()
        
        # Convert to list of dicts
        jobs_data = [job.model_dump() for job in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch failed: {str(e)}")

    return APIResponse[List[Dict[str, Any]]](
        ErrorCode=0,
        Data=jobs_data,
        Message="Jobs retrieved successfully"
    )

# --- 3. READ ALL JOBS (GET) ---
@router.get("/all", response_model=APIResponse[List[Dict[str, Any]]])
async def get_all_jobs(
    current_user: User = Depends(get_current_user), # Authentication required
    session: Session = Depends(get_session)
) -> APIResponse[List[Dict[str, Any]]]:
    """
    Fetches all jobs in the database. 
    Accessible by both Candidates and Employers.
    """
    try:
        # Fetch ALL jobs without filtering by employer_id
        statement = select(Job)
        results = session.exec(statement).all()
        
        # Convert to list of dicts
        jobs_data = [job.model_dump() for job in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch failed: {str(e)}")

    return APIResponse[List[Dict[str, Any]]](
        ErrorCode=0,
        Data=jobs_data,
        Message="All jobs retrieved successfully"
    )

# --- 4. READ ONE (GET) ---
@router.get("/{job_id}", response_model=APIResponse[Dict[str, Any]])
async def get_job_details(
    job_id: uuid.UUID,
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:
    
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data=job.model_dump(),
        Message="Job details retrieved"
    )

# --- 4. UPDATE (PUT) ---
@router.put("/update/{job_id}", response_model=APIResponse[Dict[str, Any]])
async def update_job(
    job_id: uuid.UUID,
    title: Optional[str] = Body(None, embed=True),
    description: Optional[str] = Body(None, embed=True),
    required_skills: Optional[List[str]] = Body(None, embed=True),
    experience_required: Optional[int] = Body(None, embed=True),
    location: Optional[str] = Body(None, embed=True),
    job_type: Optional[JobType] = Body(None, embed=True),
    salary_range: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[Dict[str, Any]]:

    # A. Check Job Existence & Ownership
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.employer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own jobs.")

    try:
        # B. Apply Updates if provided
        if title is not None: job.title = title
        if description is not None: job.description = description
        if required_skills is not None: job.required_skills = required_skills
        if experience_required is not None: job.experience_required = experience_required
        if location is not None: job.location = location
        if job_type is not None: job.job_type = job_type
        if salary_range is not None: job.salary_range = salary_range

        session.add(job)
        session.commit()
        session.refresh(job)

        upsert_job_embedding(
            job_id=job.job_id,
            title=job.title,
            description=job.description,
            skills=job.required_skills,
            extra_payload={
                "location": job.location,
                "salary": job.salary_range,
                "job_type": job.job_type.value
            }
         )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data=job.model_dump(),
        Message="Job updated successfully"
    )

# --- 5. DELETE (DELETE) ---
@router.delete("/delete/{job_id}", response_model=APIResponse[None])
async def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> APIResponse[None]:

    # A. Check Job Existence & Ownership
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.employer_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own jobs.")

    try:
        # B. Delete Record
        session.delete(job)
        session.commit()

        delete_job_embedding(job.job_id)

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

    return APIResponse[None](
        ErrorCode=0,
        Data=None,
        Message="Job deleted successfully"
    )
    
