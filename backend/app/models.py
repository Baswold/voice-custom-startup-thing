"""
Database models for EchoForge voice cloning platform
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VoiceProfile(Base):
    """Voice profile for a cloned voice"""
    __tablename__ = "voice_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # File paths
    reference_audio_path = Column(String(512), nullable=False)
    model_path = Column(String(512), nullable=True)  # For fine-tuned models

    # Metadata
    duration_seconds = Column(Float, nullable=False)
    sample_rate = Column(Integer, default=22050)
    language = Column(String(10), default="en")

    # Consent and ethics
    consent_verified = Column(Boolean, default=False)
    consent_phrase = Column(String(512), nullable=True)
    consent_audio_path = Column(String(512), nullable=True)

    # Watermarking
    watermark_embedded = Column(Boolean, default=True)
    watermark_metadata = Column(JSON, nullable=True)

    # License and sharing
    is_public = Column(Boolean, default=False)
    license_type = Column(String(50), default="private")  # private, cc-by, cc-by-sa, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="voice_profiles")
    jobs = relationship("Job", back_populates="voice_profile")

    def __repr__(self):
        return f"<VoiceProfile(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class User(Base):
    """User account"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Subscription tier
    tier = Column(String(50), default="free")  # free, pro, enterprise

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    voice_profiles = relationship("VoiceProfile", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    consent_logs = relationship("ConsentLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"


class Job(Base):
    """Voice processing job"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    voice_profile_id = Column(Integer, ForeignKey("voice_profiles.id"), nullable=True)

    # Job details
    status = Column(String(20), default=JobStatus.PENDING.value)
    job_type = Column(String(50), nullable=False)  # "clone_voice", "fine_tune", "synthesize"

    # Input/output
    input_data = Column(JSON, nullable=True)  # Job-specific input parameters
    output_data = Column(JSON, nullable=True)  # Job results

    # Progress tracking
    progress_percent = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)

    # Compute metrics
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    compute_time_seconds = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="jobs")
    voice_profile = relationship("VoiceProfile", back_populates="jobs")

    def __repr__(self):
        return f"<Job(id={self.id}, type='{self.job_type}', status='{self.status}')>"


class ConsentLog(Base):
    """Consent verification log for ethical compliance"""
    __tablename__ = "consent_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Consent details
    consent_phrase = Column(String(512), nullable=False)
    spoken_phrase = Column(String(512), nullable=True)  # ASR transcription
    audio_path = Column(String(512), nullable=False)

    # Verification
    is_verified = Column(Boolean, default=False)
    verification_method = Column(String(50), default="manual")  # manual, asr, hybrid
    verification_score = Column(Float, nullable=True)  # Confidence score

    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="consent_logs")

    def __repr__(self):
        return f"<ConsentLog(id={self.id}, user_id={self.user_id}, verified={self.is_verified})>"


class VoiceLibraryEntry(Base):
    """Public voice library entries (opt-in community voices)"""
    __tablename__ = "voice_library"

    id = Column(Integer, primary_key=True, index=True)
    voice_profile_id = Column(Integer, ForeignKey("voice_profiles.id"), nullable=False, unique=True)

    # Display info
    display_name = Column(String(255), nullable=False)
    creator_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    preview_audio_path = Column(String(512), nullable=True)

    # Categorization
    tags = Column(JSON, nullable=True)  # ["male", "deep", "american", etc.]
    language = Column(String(10), default="en")

    # License
    license_type = Column(String(50), nullable=False)  # cc-by, cc-by-sa, etc.
    attribution_required = Column(Boolean, default=True)
    commercial_use = Column(Boolean, default=False)

    # Stats
    download_count = Column(Integer, default=0)
    rating_average = Column(Float, nullable=True)
    rating_count = Column(Integer, default=0)

    # Revenue sharing (future feature)
    revenue_share_enabled = Column(Boolean, default=False)
    revenue_share_percent = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<VoiceLibraryEntry(id={self.id}, name='{self.display_name}')>"
