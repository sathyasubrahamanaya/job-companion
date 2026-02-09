import uuid
from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field, Relationship, Index


class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: Optional[str] = None
    role: Optional[str] = None

# -----------------------------------------
# ENUMERATIONS
# -----------------------------------------


class SenderType(str, Enum):
    USER = "USER"
    AI = "AI"

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

class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class ChatType(str, Enum):
    INTERVIEW = "INTERVIEW"
    CASUAL = "CASUAL"

class NotificationType(str, Enum):
    INVITE = "INVITE"
    REMINDER = "REMINDER"
    APPLICATION_UPDATE = "APPLICATION_UPDATE"
    SYSTEM = "SYSTEM"

# Helper for current UTC time
def utc_now():
    return datetime.now(timezone.utc)

# -----------------------------------------
# USERS
# -----------------------------------------
class User(SQLModel, table=True):
    __tablename__ = "users" # type: ignore

    user_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    name: str
   
    email: str = Field(unique=True, index=True)
    hashed_password: str
    phone: Optional[str] = None
    role: UserRole
    profile_image: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)

    # Relationships
    candidate_profile: Optional["CandidateProfile"] = Relationship(back_populates="user")
    employer_profile: Optional["EmployerProfile"] = Relationship(back_populates="user")


# -----------------------------------------
# CANDIDATE PROFILE
# -----------------------------------------
class CandidateProfile(SQLModel, table=True):
    __tablename__ = "candidate_profiles" # type: ignore

    candidate_id: uuid.UUID = Field(
        foreign_key="users.user_id", primary_key=True
    )
    resume_id: Optional[str] = None
    skills: List[str] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=list,
    )
    experience_years: int
    educations: List[str] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=list,
    )
    preferred_roles: List[str] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=list,
    )
    preferred_locations: List[str] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=list,
    )
    expected_salary: Optional[float] = None

    # Relationships
    user: User = Relationship(back_populates="candidate_profile")
    applications: List["JobApplication"] = Relationship(back_populates="candidate")
    recommendations: List["JobRecommendation"] = Relationship(back_populates="candidate")


# -----------------------------------------
# EMPLOYER PROFILE
# -----------------------------------------
class EmployerProfile(SQLModel, table=True):
    __tablename__ = "employer_profiles" # type: ignore

    employer_id: uuid.UUID = Field(
        foreign_key="users.user_id", primary_key=True
    )
    company_name: str
    company_description: str
    industry: str
    location: str

    # Relationships
    user: User = Relationship(back_populates="employer_profile")
    jobs: List["Job"] = Relationship(back_populates="employer")
    shortlisted_candidates: List["ShortlistedCandidate"] = Relationship(
        back_populates="employer"
    )


# -----------------------------------------
# JOB
# -----------------------------------------
class Job(SQLModel, table=True):
    __tablename__ = "jobs" # type: ignore

    job_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    employer_id: uuid.UUID = Field(foreign_key="employer_profiles.employer_id")
    title: str
    description: str
    required_skills: List[str] = Field(
        sa_column=Column(JSON, nullable=False),
        default_factory=list,
    )
    experience_required: int
    location: str
    salary_range: Optional[str] = None
    job_type: JobType
    created_at: datetime = Field(default_factory=utc_now)

    # Relationships
    employer: EmployerProfile = Relationship(back_populates="jobs")
    applications: List["JobApplication"] = Relationship(back_populates="job")
    recommendations: List["JobRecommendation"] = Relationship(back_populates="job")


# -----------------------------------------
# JOB APPLICATION
# -----------------------------------------
class JobApplication(SQLModel, table=True):
    __tablename__ = "job_applications" # type: ignore
    __table_args__ = (Index("ix_applicant_job", "candidate_id", "job_id", unique=True),)

    application_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    job_id: uuid.UUID = Field(foreign_key="jobs.job_id")
    candidate_id: uuid.UUID = Field(foreign_key="candidate_profiles.candidate_id")
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED)
    ai_match_score: float = Field(default=0.0)
    applied_at: datetime = Field(default_factory=utc_now)

    # Relationships
    job: Job = Relationship(back_populates="applications")
    candidate: CandidateProfile = Relationship(back_populates="applications")


# -----------------------------------------
# JOB RECOMMENDATION
# -----------------------------------------
class JobRecommendation(SQLModel, table=True):
    __tablename__ = "job_recommendations" # type: ignore
    __table_args__ = (Index("ix_candidate_job_reco", "candidate_id", "job_id"),)

    recommendation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True
    )
    job_id: uuid.UUID = Field(foreign_key="jobs.job_id")
    candidate_id: uuid.UUID = Field(foreign_key="candidate_profiles.candidate_id")
    match_score: float
    reason: str
    created_at: datetime = Field(default_factory=utc_now)

    # Relationships
    job: Job = Relationship(back_populates="recommendations")
    candidate: CandidateProfile = Relationship(back_populates="recommendations")


# -----------------------------------------
# SHORTLISTED CANDIDATES
# -----------------------------------------
class ShortlistedCandidate(SQLModel, table=True):
    __tablename__ = "shortlisted_candidates" # type: ignore
    __table_args__ = (
        Index("ix_shortlisted", "candidate_id", "employer_id", unique=True),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    candidate_id: uuid.UUID = Field(foreign_key="candidate_profiles.candidate_id")
    employer_id: uuid.UUID = Field(foreign_key="employer_profiles.employer_id")

    # Relationships
    candidate: CandidateProfile = Relationship()
    employer: EmployerProfile = Relationship(back_populates="shortlisted_candidates")


# -----------------------------------------
# CHAT HISTORY
# -----------------------------------------
class ChatHistory(SQLModel, table=True):
    __tablename__ = "chat_history" # type: ignore

    chat_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_message: str
    ai_message: str
    chat_time: datetime = Field(default_factory=utc_now)
    chat_type: ChatType
    sender: SenderType
    
    
class InterviewSession(SQLModel, table=True):
    # FIX: Added ': str' to satisfy Pylance
    __tablename__ = "interview_sessions" #type: ignore
    
    session_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    candidate_id: uuid.UUID = Field(foreign_key="users.user_id")
    job_id: uuid.UUID = Field(foreign_key="jobs.job_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="active") 
    
    # Relationships
    messages: List["ChatMessage"] = Relationship(back_populates="session")

class ChatMessage(SQLModel, table=True):
    # FIX: Added ': str' to satisfy Pylance
    __tablename__ = "chat_messages" #type: ignore
    
    message_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(foreign_key="interview_sessions.session_id")
    role: str # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    session: Optional[InterviewSession] = Relationship(back_populates="messages")

# -----------------------------------------
# NOTIFICATIONS
# -----------------------------------------
class Notification(SQLModel, table=True):
    __tablename__ = "notifications" # type: ignore
    
    notification_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    recipient_id: uuid.UUID = Field(foreign_key="users.user_id", index=True)
    sender_id: uuid.UUID = Field(foreign_key="users.user_id")
    job_id: Optional[uuid.UUID] = Field(default=None, foreign_key="jobs.job_id")
    type: NotificationType
    title: str
    message: str
    is_read: bool = Field(default=False)
    invitation_status: Optional[InvitationStatus] = Field(default=None)
    memo_candidate: Optional[str] = Field(default=None)
    memo_employer: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)

    # Relationships
    recipient: User = Relationship(sa_relationship_kwargs={"foreign_keys": "[Notification.recipient_id]"})
    sender: User = Relationship(sa_relationship_kwargs={"foreign_keys": "[Notification.sender_id]"})
    job: Optional[Job] = Relationship()