// API Response Types
export interface APIResponse<T> {
    ErrorCode: number;
    Data: T | null;
    Message: string;
}

// Auth Types
export interface LoginRequest {
    email: string;
    password: string;
}

export interface Token {
    access_token: string;
    token_type: string;
}

// Enums
export enum NotificationType {
    INVITE = 'INVITE',
    REMINDER = 'REMINDER',
    APPLICATION_UPDATE = 'APPLICATION_UPDATE',
    SYSTEM = 'SYSTEM'
}

export enum InvitationStatus {
    PENDING = 'PENDING',
    ACCEPTED = 'ACCEPTED',
    REJECTED = 'REJECTED'
}
export enum UserRole {
    CANDIDATE = 'CANDIDATE',
    EMPLOYER = 'EMPLOYER',
    ADMIN = 'ADMIN'
}

export enum JobType {
    FULL_TIME = 'FULL_TIME',
    PART_TIME = 'PART_TIME',
    INTERNSHIP = 'INTERNSHIP'
}

export enum ApplicationStatus {
    APPLIED = 'APPLIED',
    SHORTLISTED = 'SHORTLISTED',
    REJECTED = 'REJECTED'
}

export enum SenderType {
    USER = 'USER',
    AI = 'AI'
}

export enum DifficultyLevel {
    EASY = 'EASY',
    MEDIUM = 'MEDIUM',
    HARD = 'HARD'
}

export enum ChatType {
    INTERVIEW = 'INTERVIEW',
    CASUAL = 'CASUAL'
}

// User Types
export interface User {
    user_id: string;
    name: string;
    email: string;
    phone?: string;
    role: UserRole;
    profile_image?: string;
    created_at: string;
}

// Candidate Types
export interface CandidateProfile {
    candidate_id: string;
    resume_id?: string;
    skills: string[];
    experience_years: number;
    educations: string[];
    preferred_roles: string[];
    preferred_locations: string[];
    expected_salary?: number;
}

export interface CandidateSignupForm {
    name: string;
    email: string;
    password: string;
    file: File;
}

// Employer Types
export interface EmployerProfile {
    employer_id: string;
    company_name: string;
    company_description: string;
    industry: string;
    location: string;
}

export interface EmployerSignupForm {
    name: string;
    email: string;
    password: string;
}

export interface EmployerOnboardForm {
    company_name: string;
    company_description: string;
    industry: string;
    location: string;
}

// Job Types
export interface Job {
    job_id: string;
    employer_id: string;
    title: string;
    description: string;
    required_skills: string[];
    experience_required: number;
    location: string;
    salary_range?: string;
    job_type: JobType;
    created_at: string;
}

export interface JobPostForm {
    title: string;
    description: string;
    required_skills: string[];
    experience_required: number;
    location: string;
    job_type: JobType;
    salary_range?: string;
}

export interface JobUpdateForm {
    title?: string;
    description?: string;
    required_skills?: string[];
    experience_required?: number;
    location?: string;
    job_type?: JobType;
    salary_range?: string;
}

// Interview Types
export interface InterviewSession {
    session_id: string;
    job_id: string;
    candidate_id: string;
    started_at: string;
}

export interface ChatMessage {
    user_message?: string;
    ai_message?: string;
}

// Search Types
export interface SearchJobsRequest {
    query: string;
    limit?: number;
}

export interface SearchCandidatesRequest {
    query: string;
    limit?: number;
}
export interface PotentialCandidate {
    candidate_id: string;
    name: string;
    skills: string[];
    experience_years: number;
    roles: string[];
    locations: string[];
    match_score: number;
    is_invited?: boolean;
    invitation_id?: string;
    invitation_status?: InvitationStatus;
    memo_candidate?: string;
    memo_employer?: string;
}

export interface Notification {
    notification_id: string;
    recipient_id: string;
    sender_id: string;
    job_id?: string;
    type: NotificationType;
    title: string;
    message: string;
    is_read: boolean;
    invitation_status?: InvitationStatus;
    memo_candidate?: string;
    memo_employer?: string;
    created_at: string;
}
