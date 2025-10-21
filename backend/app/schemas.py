"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    tier: str
    created_at: datetime

    class Config:
        from_attributes = True


# Voice Profile schemas
class VoiceProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    language: str = Field(default="en", max_length=10)
    is_public: bool = False
    license_type: str = Field(default="private", max_length=50)


class VoiceProfileCreate(VoiceProfileBase):
    consent_phrase: str = Field(..., min_length=10, max_length=512)


class VoiceProfileResponse(VoiceProfileBase):
    id: int
    user_id: int
    duration_seconds: float
    sample_rate: int
    consent_verified: bool
    watermark_embedded: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Job schemas
class JobBase(BaseModel):
    job_type: str = Field(..., max_length=50)
    input_data: Optional[Dict[str, Any]] = None


class JobCreate(JobBase):
    pass


class JobResponse(JobBase):
    id: int
    user_id: int
    voice_profile_id: Optional[int] = None
    status: str
    progress_percent: float
    error_message: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    compute_time_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Consent Log schemas
class ConsentLogCreate(BaseModel):
    consent_phrase: str = Field(..., min_length=10, max_length=512)


class ConsentLogResponse(BaseModel):
    id: int
    user_id: int
    consent_phrase: str
    spoken_phrase: Optional[str] = None
    is_verified: bool
    verification_method: str
    verification_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Voice Library schemas
class VoiceLibraryEntryBase(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)
    creator_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    language: str = Field(default="en", max_length=10)
    license_type: str = Field(..., max_length=50)
    attribution_required: bool = True
    commercial_use: bool = False


class VoiceLibraryEntryResponse(VoiceLibraryEntryBase):
    id: int
    voice_profile_id: int
    preview_audio_path: Optional[str] = None
    download_count: int
    rating_average: Optional[float] = None
    rating_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Upload schemas
class VoiceUploadResponse(BaseModel):
    """Response after uploading voice audio"""
    job_id: int
    status: str
    message: str


class SynthesizeRequest(BaseModel):
    """Request to synthesize speech from text"""
    voice_profile_id: int
    text: str = Field(..., min_length=1, max_length=5000)
    language: Optional[str] = "en"
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class SynthesizeResponse(BaseModel):
    """Response after synthesizing speech"""
    job_id: int
    status: str
    message: str


# Status and health check schemas
class HealthCheckResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
