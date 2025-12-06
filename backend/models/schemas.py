"""
SiteMind Pydantic Schemas
Request/Response models for API validation
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# ===========================================
# Builder Schemas
# ===========================================

class BuilderCreate(BaseModel):
    """Schema for creating a new builder"""
    name: str = Field(..., min_length=1, max_length=255)
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    monthly_fee: Optional[float] = None


class BuilderUpdate(BaseModel):
    """Schema for updating a builder"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    subscription_status: Optional[str] = None
    monthly_fee: Optional[float] = None


class BuilderResponse(BaseModel):
    """Schema for builder response"""
    id: UUID
    name: str
    contact_person: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    address: Optional[str]
    subscription_status: str
    monthly_fee: Optional[float]
    sites_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===========================================
# Project Schemas
# ===========================================

class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    builder_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    whatsapp_number: Optional[str] = None
    start_date: Optional[datetime] = None
    expected_completion: Optional[datetime] = None
    project_value: Optional[float] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    whatsapp_number: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    expected_completion: Optional[datetime] = None
    project_value: Optional[float] = None


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: UUID
    builder_id: UUID
    name: str
    description: Optional[str]
    location: Optional[str]
    whatsapp_number: Optional[str]
    status: str
    start_date: Optional[datetime]
    expected_completion: Optional[datetime]
    project_value: Optional[float]
    created_at: datetime
    blueprints_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# ===========================================
# Blueprint Schemas
# ===========================================

class BlueprintCreate(BaseModel):
    """Schema for creating a new blueprint"""
    project_id: UUID
    filename: str
    file_url: str
    category: Optional[str] = "other"
    revision: Optional[str] = None
    drawing_number: Optional[str] = None


class BlueprintResponse(BaseModel):
    """Schema for blueprint response"""
    id: UUID
    project_id: UUID
    filename: str
    file_url: str
    category: str
    revision: Optional[str]
    drawing_number: Optional[str]
    is_processed: bool
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# ===========================================
# Site Engineer Schemas
# ===========================================

class SiteEngineerCreate(BaseModel):
    """Schema for creating a site engineer"""
    project_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    role: Optional[str] = "Site Engineer"


class SiteEngineerResponse(BaseModel):
    """Schema for site engineer response"""
    id: UUID
    project_id: UUID
    name: str
    phone_number: str
    role: Optional[str]
    is_active: bool
    total_query_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===========================================
# WhatsApp Webhook Schemas
# ===========================================

class WhatsAppIncomingMessage(BaseModel):
    """Schema for incoming WhatsApp message (Twilio format)"""
    MessageSid: str
    AccountSid: Optional[str] = None
    From: str  # Phone number with "whatsapp:" prefix
    To: str
    Body: Optional[str] = ""
    NumMedia: Optional[str] = "0"
    MediaUrl0: Optional[str] = None
    MediaContentType0: Optional[str] = None
    ProfileName: Optional[str] = None


class WhatsAppResponse(BaseModel):
    """Schema for WhatsApp response"""
    status: str
    message_sid: Optional[str] = None
    response: Optional[str] = None
    response_time_ms: Optional[int] = None
    error: Optional[str] = None


# ===========================================
# Chat Schemas
# ===========================================

class ChatQuery(BaseModel):
    """Schema for a chat query"""
    project_id: UUID
    user_phone: str
    message: str
    message_type: str = "text"
    media_url: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chat response"""
    response: str
    confidence: Optional[float] = None
    blueprints_referenced: Optional[List[str]] = None
    response_time_ms: int


class ChatLogResponse(BaseModel):
    """Schema for chat log response"""
    id: UUID
    project_id: UUID
    user_phone: str
    message_type: str
    user_message: str
    bot_response: str
    response_time_ms: int
    feedback_rating: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===========================================
# Analytics Schemas
# ===========================================

class ProjectAnalytics(BaseModel):
    """Schema for project analytics"""
    project_id: UUID
    project_name: str
    total_queries: int
    queries_today: int
    avg_response_time_ms: float
    unique_users: int
    positive_feedback_rate: float
    total_cost_usd: float


class DashboardStats(BaseModel):
    """Schema for admin dashboard stats"""
    total_builders: int
    total_projects: int
    active_projects: int
    total_queries_today: int
    total_queries_month: int
    total_revenue: float
    avg_response_time_ms: float


# ===========================================
# Feedback Schemas
# ===========================================

class FeedbackCreate(BaseModel):
    """Schema for submitting feedback"""
    chat_log_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


# ===========================================
# Health Check
# ===========================================

class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    database: str
    gemini: str
    whisper: str
    whatsapp: str

