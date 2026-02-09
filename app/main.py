import os
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.db.session import create_db_and_tables
from app.routers import candidate, employer, jobs,auth
from app.schemas.response import APIResponse
from app.routers import interview



@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # 1. Create DB Tables
        create_db_and_tables()
        
        # 2. Create Uploads Directory if it doesn't exist
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            print("Created 'uploads' directory.")
            
        print("System initialized successfully.")
    except Exception as e:
        print(f"Startup Failure: {e}")
    yield

app = FastAPI(title="Job AI Companion", lifespan=lifespan)

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL EXCEPTION HANDLERS ---

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    response = APIResponse[None](
        ErrorCode=exc.status_code,
        Data=None,
        Message=str(exc.detail)
    )
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = APIResponse[str](
        ErrorCode=422,
        Data=str(exc.errors()), 
        Message="Validation Error"
    )
    return JSONResponse(status_code=422, content=response.model_dump())

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    response = APIResponse[None](
        ErrorCode=500,
        Data=None,
        Message=f"Internal Server Error: {str(exc)}"
    )
    return JSONResponse(status_code=500, content=response.model_dump())

# --- ROUTERS ---
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(candidate.router, prefix="/api/v1/candidate", tags=["Candidate"])

app.include_router(employer.router, prefix="/api/v1/employer", tags=["Employer"])
app.include_router(interview.router, prefix="/api/v1/interview", tags=["Interview"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])





@app.get("/health", response_model=APIResponse[Dict[str, Any]])
def health():
    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={"version": settings.VERSION},
        Message="System Healthy"
    )