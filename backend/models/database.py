"""
SiteMind Database Models
SQLAlchemy ORM models for PostgreSQL
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, 
    DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum"""
    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class ProjectStatus(str, enum.Enum):
    """Project status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"


class MessageType(str, enum.Enum):
    """Message type enum"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    DOCUMENT = "document"


class BlueprintCategory(str, enum.Enum):
    """Blueprint category enum"""
    ARCHITECTURAL = "architectural"
    STRUCTURAL = "structural"
    MEP = "mep"
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    HVAC = "hvac"
    LANDSCAPE = "landscape"
    OTHER = "other"


class Builder(Base):
    """
    Builder/Client model
    Represents a construction company that subscribes to SiteMind
    """
    __tablename__ = "builders"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    
    subscription_status: Mapped[str] = mapped_column(
        String(20), 
        default=SubscriptionStatus.TRIAL.value
    )
    monthly_fee: Mapped[Optional[float]] = mapped_column(Float)
    sites_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship(
        "Project", 
        back_populates="builder",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Builder {self.name}>"


class Project(Base):
    """
    Project/Site model
    Represents a construction site being monitored by SiteMind
    """
    __tablename__ = "projects"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    builder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("builders.id", ondelete="CASCADE"),
        nullable=False
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(500))
    
    # WhatsApp integration
    whatsapp_number: Mapped[Optional[str]] = mapped_column(
        String(20), 
        unique=True, 
        index=True
    )
    
    status: Mapped[str] = mapped_column(
        String(20), 
        default=ProjectStatus.ACTIVE.value
    )
    
    # Supermemory integration
    supermemory_namespace: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Project details
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expected_completion: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    project_value: Mapped[Optional[float]] = mapped_column(Float)  # In INR Crores
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    builder: Mapped["Builder"] = relationship("Builder", back_populates="projects")
    blueprints: Mapped[List["Blueprint"]] = relationship(
        "Blueprint", 
        back_populates="project",
        cascade="all, delete-orphan"
    )
    chat_logs: Mapped[List["ChatLog"]] = relationship(
        "ChatLog", 
        back_populates="project",
        cascade="all, delete-orphan"
    )
    site_engineers: Mapped[List["SiteEngineer"]] = relationship(
        "SiteEngineer",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Project {self.name}>"


class Blueprint(Base):
    """
    Blueprint model
    Represents an uploaded blueprint/drawing PDF
    """
    __tablename__ = "blueprints"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # File info
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)  # S3 URL
    file_size: Mapped[Optional[int]] = mapped_column(Integer)  # In bytes
    
    # Gemini integration
    gemini_file_id: Mapped[Optional[str]] = mapped_column(String(255))
    gemini_file_uri: Mapped[Optional[str]] = mapped_column(Text)
    
    # Classification
    category: Mapped[str] = mapped_column(
        String(20), 
        default=BlueprintCategory.OTHER.value
    )
    revision: Mapped[Optional[str]] = mapped_column(String(50))
    drawing_number: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Processing status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="blueprints")
    
    def __repr__(self):
        return f"<Blueprint {self.filename}>"


class SiteEngineer(Base):
    """
    Site Engineer model
    Represents an authorized user who can query SiteMind
    """
    __tablename__ = "site_engineers"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    role: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "Site Engineer", "Project Manager"
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Usage tracking
    daily_query_count: Mapped[int] = mapped_column(Integer, default=0)
    total_query_count: Mapped[int] = mapped_column(Integer, default=0)
    last_query_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="site_engineers")
    
    def __repr__(self):
        return f"<SiteEngineer {self.name} ({self.phone_number})>"


class ChatLog(Base):
    """
    Chat Log model
    Stores all conversations with site engineers
    """
    __tablename__ = "chat_logs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # User info
    user_phone: Mapped[str] = mapped_column(String(20), index=True)
    user_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Message details
    message_type: Mapped[str] = mapped_column(
        String(20), 
        default=MessageType.TEXT.value
    )
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    user_message_media_url: Mapped[Optional[str]] = mapped_column(Text)  # For voice/image
    
    # Transcription (for voice messages)
    transcription: Mapped[Optional[str]] = mapped_column(Text)
    
    # Response
    bot_response: Mapped[str] = mapped_column(Text, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer)
    
    # AI metadata
    model_used: Mapped[Optional[str]] = mapped_column(String(50))
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Referenced blueprints
    blueprints_referenced: Mapped[Optional[dict]] = mapped_column(JSON)  # List of blueprint IDs
    
    # Feedback
    feedback_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 or thumbs up/down
    feedback_comment: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="chat_logs")
    
    def __repr__(self):
        return f"<ChatLog {self.id} from {self.user_phone}>"


class UsageMetric(Base):
    """
    Usage Metrics model
    Tracks daily usage statistics per project
    """
    __tablename__ = "usage_metrics"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    
    # Query counts
    total_queries: Mapped[int] = mapped_column(Integer, default=0)
    text_queries: Mapped[int] = mapped_column(Integer, default=0)
    voice_queries: Mapped[int] = mapped_column(Integer, default=0)
    image_queries: Mapped[int] = mapped_column(Integer, default=0)
    
    # Performance
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float)
    
    # Costs (in USD)
    gemini_cost: Mapped[float] = mapped_column(Float, default=0.0)
    whisper_cost: Mapped[float] = mapped_column(Float, default=0.0)
    whatsapp_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    # User engagement
    unique_users: Mapped[int] = mapped_column(Integer, default=0)
    positive_feedback: Mapped[int] = mapped_column(Integer, default=0)
    negative_feedback: Mapped[int] = mapped_column(Integer, default=0)
    
    def __repr__(self):
        return f"<UsageMetric {self.project_id} on {self.date}>"

