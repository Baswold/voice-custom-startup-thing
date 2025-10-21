"""
FastAPI main application for EchoForge
"""
import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

from . import __version__
from .database import get_db, init_db
from .models import User, VoiceProfile, Job, ConsentLog, JobStatus
from .schemas import (
    UserCreate, UserLogin, UserResponse,
    VoiceProfileCreate, VoiceProfileResponse,
    JobResponse, SynthesizeRequest, SynthesizeResponse,
    VoiceUploadResponse, HealthCheckResponse,
    ConsentLogResponse
)
from .api import auth, utils
from .worker.voice_processor import VoiceProcessor


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print("🚀 Starting EchoForge...")
    init_db()
    print("✅ Database initialized")

    # Create necessary directories
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/models", exist_ok=True)
    os.makedirs("data/outputs", exist_ok=True)
    print("✅ Data directories created")

    yield

    # Shutdown
    print("👋 Shutting down EchoForge...")


# Create FastAPI app
app = FastAPI(
    title="EchoForge API",
    description="Local voice cloning platform - Your voice, your device.",
    version=__version__,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("data/outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="data/outputs"), name="outputs")


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.utcnow()
    }


# User endpoints
@app.post("/api/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    # Hash password
    hashed_password = auth.hash_password(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/api/users/login")
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Generate token (simplified for MVP - use JWT in production)
    token = auth.create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    return current_user


# Voice profile endpoints
@app.post("/api/voices/upload", response_model=VoiceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_voice(
    audio_file: UploadFile = File(...),
    consent_audio: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(None),
    consent_phrase: str = Form(...),
    language: str = Form("en"),
    is_public: bool = Form(False),
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload voice recording and create voice profile.
    Requires both reference audio and consent recording.
    """
    # Validate file types
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid audio file type"
        )

    if not consent_audio.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid consent audio file type"
        )

    # Save uploaded files
    upload_dir = f"data/uploads/user_{current_user.id}"
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    audio_path = f"{upload_dir}/voice_{timestamp}.wav"
    consent_path = f"{upload_dir}/consent_{timestamp}.wav"

    # Save files
    with open(audio_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)

    with open(consent_path, "wb") as f:
        content = await consent_audio.read()
        f.write(content)

    # Get audio duration
    duration = utils.get_audio_duration(audio_path)

    # Validate duration (should be between 10-120 seconds for best results)
    if duration < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice recording too short. Please record at least 10 seconds."
        )

    # Create consent log
    consent_log = ConsentLog(
        user_id=current_user.id,
        consent_phrase=consent_phrase,
        audio_path=consent_path,
        is_verified=False,  # Will be verified by worker
        verification_method="asr"
    )
    db.add(consent_log)
    db.commit()
    db.refresh(consent_log)

    # Create voice profile
    voice_profile = VoiceProfile(
        user_id=current_user.id,
        name=name,
        description=description,
        reference_audio_path=audio_path,
        duration_seconds=duration,
        language=language,
        consent_phrase=consent_phrase,
        consent_audio_path=consent_path,
        consent_verified=False,  # Will be verified by worker
        is_public=is_public
    )
    db.add(voice_profile)
    db.commit()
    db.refresh(voice_profile)

    # Create processing job
    job = Job(
        user_id=current_user.id,
        voice_profile_id=voice_profile.id,
        job_type="clone_voice",
        status=JobStatus.PENDING.value,
        input_data={
            "audio_path": audio_path,
            "consent_path": consent_path,
            "consent_phrase": consent_phrase,
            "language": language
        }
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "status": "pending",
        "message": f"Voice profile '{name}' created. Processing started."
    }


@app.get("/api/voices", response_model=List[VoiceProfileResponse])
async def list_voice_profiles(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """List all voice profiles for current user"""
    profiles = db.query(VoiceProfile).filter(
        VoiceProfile.user_id == current_user.id
    ).all()
    return profiles


@app.get("/api/voices/{voice_id}", response_model=VoiceProfileResponse)
async def get_voice_profile(
    voice_id: int,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific voice profile"""
    profile = db.query(VoiceProfile).filter(
        VoiceProfile.id == voice_id,
        VoiceProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice profile not found"
        )

    return profile


# Job endpoints
@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: int,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Get job status"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job


@app.get("/api/jobs", response_model=List[JobResponse])
async def list_jobs(
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """List all jobs for current user"""
    jobs = db.query(Job).filter(
        Job.user_id == current_user.id
    ).order_by(Job.created_at.desc()).limit(limit).all()
    return jobs


# Synthesis endpoint
@app.post("/api/synthesize", response_model=SynthesizeResponse)
async def synthesize_speech(
    request: SynthesizeRequest,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Synthesize speech from text using a voice profile.
    Returns a job ID - poll /api/jobs/{job_id} for results.
    """
    # Verify voice profile exists and belongs to user
    profile = db.query(VoiceProfile).filter(
        VoiceProfile.id == request.voice_profile_id,
        VoiceProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice profile not found"
        )

    if not profile.consent_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice profile consent not yet verified"
        )

    # Create synthesis job
    job = Job(
        user_id=current_user.id,
        voice_profile_id=profile.id,
        job_type="synthesize",
        status=JobStatus.PENDING.value,
        input_data={
            "text": request.text,
            "language": request.language,
            "speed": request.speed,
            "reference_audio": profile.reference_audio_path
        }
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "status": "pending",
        "message": "Synthesis job created. Check job status for results."
    }


# Worker processing endpoint
@app.post("/api/worker/process")
async def process_pending_jobs(db: Session = Depends(get_db)):
    """
    Process pending jobs. This endpoint should be called by a background worker
    or cron job. In production, use Celery or similar task queue.
    """
    # Get all pending jobs
    pending_jobs = db.query(Job).filter(
        Job.status == JobStatus.PENDING.value
    ).limit(10).all()

    if not pending_jobs:
        return {"message": "No pending jobs", "processed": 0}

    processor = VoiceProcessor(db)
    processed_count = 0

    for job in pending_jobs:
        try:
            processor.process_job(job)
            processed_count += 1
        except Exception as e:
            print(f"Error processing job {job.id}: {e}")
            job.status = JobStatus.FAILED.value
            job.error_message = str(e)
            db.commit()

    return {
        "message": f"Processed {processed_count} jobs",
        "processed": processed_count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
