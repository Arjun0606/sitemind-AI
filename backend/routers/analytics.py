"""
SiteMind Analytics Router
Usage analytics and dashboard statistics
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from utils.database import get_async_session
from models.database import Builder, Project, Blueprint, ChatLog, UsageMetric
from models.schemas import DashboardStats, ProjectAnalytics, ChatLogResponse


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_async_session),
):
    """Get overall dashboard statistics"""
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    
    # Total builders
    builders_count = await db.execute(select(func.count(Builder.id)))
    total_builders = builders_count.scalar()
    
    # Total and active projects
    projects_count = await db.execute(select(func.count(Project.id)))
    total_projects = projects_count.scalar()
    
    active_projects_count = await db.execute(
        select(func.count(Project.id))
        .where(Project.status == "active")
    )
    active_projects = active_projects_count.scalar()
    
    # Queries today
    queries_today_result = await db.execute(
        select(func.count(ChatLog.id))
        .where(func.date(ChatLog.created_at) == today)
    )
    queries_today = queries_today_result.scalar()
    
    # Queries this month
    queries_month_result = await db.execute(
        select(func.count(ChatLog.id))
        .where(ChatLog.created_at >= datetime.combine(month_start, datetime.min.time()))
    )
    queries_month = queries_month_result.scalar()
    
    # Average response time (last 7 days)
    avg_response_result = await db.execute(
        select(func.avg(ChatLog.response_time_ms))
        .where(ChatLog.created_at >= datetime.utcnow() - timedelta(days=7))
    )
    avg_response_time = avg_response_result.scalar() or 0
    
    # Total revenue (sum of monthly fees from active builders)
    revenue_result = await db.execute(
        select(func.sum(Builder.monthly_fee))
        .where(Builder.subscription_status == "active")
    )
    total_revenue = revenue_result.scalar() or 0
    
    return DashboardStats(
        total_builders=total_builders or 0,
        total_projects=total_projects or 0,
        active_projects=active_projects or 0,
        total_queries_today=queries_today or 0,
        total_queries_month=queries_month or 0,
        total_revenue=float(total_revenue),
        avg_response_time_ms=float(avg_response_time),
    )


@router.get("/projects/{project_id}", response_model=ProjectAnalytics)
async def get_project_analytics(
    project_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """Get analytics for a specific project"""
    today = datetime.utcnow().date()
    
    # Get project
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        return {"error": "Project not found"}
    
    # Total queries
    total_queries_result = await db.execute(
        select(func.count(ChatLog.id))
        .where(ChatLog.project_id == project_id)
    )
    total_queries = total_queries_result.scalar()
    
    # Queries today
    queries_today_result = await db.execute(
        select(func.count(ChatLog.id))
        .where(and_(
            ChatLog.project_id == project_id,
            func.date(ChatLog.created_at) == today
        ))
    )
    queries_today = queries_today_result.scalar()
    
    # Average response time
    avg_response_result = await db.execute(
        select(func.avg(ChatLog.response_time_ms))
        .where(ChatLog.project_id == project_id)
    )
    avg_response_time = avg_response_result.scalar() or 0
    
    # Unique users
    unique_users_result = await db.execute(
        select(func.count(func.distinct(ChatLog.user_phone)))
        .where(ChatLog.project_id == project_id)
    )
    unique_users = unique_users_result.scalar()
    
    # Positive feedback rate
    positive_result = await db.execute(
        select(func.count(ChatLog.id))
        .where(and_(
            ChatLog.project_id == project_id,
            ChatLog.feedback_rating >= 4
        ))
    )
    positive_count = positive_result.scalar() or 0
    
    total_feedback_result = await db.execute(
        select(func.count(ChatLog.id))
        .where(and_(
            ChatLog.project_id == project_id,
            ChatLog.feedback_rating.isnot(None)
        ))
    )
    total_feedback = total_feedback_result.scalar() or 1
    
    positive_rate = (positive_count / total_feedback) * 100 if total_feedback > 0 else 0
    
    # Estimate cost (rough calculation)
    # Assuming average of 500 tokens per query at $0.20/1M tokens
    estimated_cost = (total_queries or 0) * 500 * 0.20 / 1_000_000
    
    return ProjectAnalytics(
        project_id=project_id,
        project_name=project.name,
        total_queries=total_queries or 0,
        queries_today=queries_today or 0,
        avg_response_time_ms=float(avg_response_time),
        unique_users=unique_users or 0,
        positive_feedback_rate=positive_rate,
        total_cost_usd=round(estimated_cost, 2),
    )


@router.get("/projects/{project_id}/chats", response_model=List[ChatLogResponse])
async def get_project_chat_history(
    project_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_phone: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """Get chat history for a project"""
    query = select(ChatLog).where(ChatLog.project_id == project_id)
    
    if user_phone:
        query = query.where(ChatLog.user_phone == user_phone)
    
    query = query.order_by(desc(ChatLog.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/usage/daily")
async def get_daily_usage(
    days: int = Query(30, ge=1, le=90),
    project_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """Get daily usage statistics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = (
        select(
            func.date(ChatLog.created_at).label('date'),
            func.count(ChatLog.id).label('total_queries'),
            func.count(func.distinct(ChatLog.user_phone)).label('unique_users'),
            func.avg(ChatLog.response_time_ms).label('avg_response_time'),
        )
        .where(ChatLog.created_at >= start_date)
    )
    
    if project_id:
        query = query.where(ChatLog.project_id == project_id)
    
    query = query.group_by(func.date(ChatLog.created_at)).order_by(func.date(ChatLog.created_at))
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return {
        "data": [
            {
                "date": row.date.isoformat() if row.date else None,
                "total_queries": row.total_queries,
                "unique_users": row.unique_users,
                "avg_response_time_ms": float(row.avg_response_time) if row.avg_response_time else 0,
            }
            for row in rows
        ]
    }


@router.get("/usage/by-type")
async def get_usage_by_message_type(
    project_id: Optional[UUID] = None,
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_async_session),
):
    """Get usage breakdown by message type (text, voice, image)"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = (
        select(
            ChatLog.message_type,
            func.count(ChatLog.id).label('count'),
        )
        .where(ChatLog.created_at >= start_date)
    )
    
    if project_id:
        query = query.where(ChatLog.project_id == project_id)
    
    query = query.group_by(ChatLog.message_type)
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return {
        "data": {row.message_type: row.count for row in rows}
    }


@router.post("/feedback/{chat_log_id}")
async def submit_feedback(
    chat_log_id: UUID,
    rating: int = Query(..., ge=1, le=5),
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
):
    """Submit feedback for a chat response"""
    result = await db.execute(
        select(ChatLog).where(ChatLog.id == chat_log_id)
    )
    chat_log = result.scalar_one_or_none()
    
    if not chat_log:
        return {"error": "Chat log not found"}
    
    chat_log.feedback_rating = rating
    chat_log.feedback_comment = comment
    await db.commit()
    
    return {"status": "feedback_recorded", "rating": rating}

