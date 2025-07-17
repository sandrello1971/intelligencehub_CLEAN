"""
Intelligence AI Chat Module - Schemas
Pydantic models for AI chat interface
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field


# ===== CHAT SCHEMAS =====

class ChatRequest(BaseModel):
    session_id: Union[str, UUID] = Field(..., description="Session ID for conversation")
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    auto_execute: Optional[bool] = Field(False, description="Auto-execute suggested actions")

class AIAction(BaseModel):
    type: str = Field(..., description="Action type")
    data: Dict[str, Any] = Field(..., description="Action data")
    confidence: float = Field(..., description="AI confidence score")
    needs_approval: Optional[bool] = Field(True, description="Whether action needs approval")

class ExecutedAction(BaseModel):
    action: str = Field(..., description="Action type that was executed")
    success: bool = Field(..., description="Whether execution was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution result")
    error: Optional[str] = Field(None, description="Error message if failed")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response text")
    actions: List[AIAction] = Field(default=[], description="Suggested actions")
    executed_actions: Optional[List[ExecutedAction]] = Field(None, description="Executed actions")
    session_id: Union[str, UUID] = Field(..., description="Session ID")
    needs_approval: Optional[bool] = Field(False, description="Whether response needs approval")
    usage: Optional[Dict[str, Any]] = Field(None, description="API usage statistics")
    error: Optional[bool] = Field(False, description="Whether an error occurred")
    error_details: Optional[str] = Field(None, description="Error details")

class ChatAdvancedRequest(BaseModel):
    session_id: Union[str, UUID]
    message: str
    context: Optional[Dict[str, Any]] = None
    auto_execute: Optional[bool] = False
    response_format: Optional[str] = Field("conversational", description="Response format")
    include_insights: Optional[bool] = Field(False, description="Include AI insights")


# ===== KPI & DASHBOARD SCHEMAS =====

class TaskStatusBreakdown(BaseModel):
    aperto: Optional[int] = 0
    chiuso: Optional[int] = 0
    sospeso: Optional[int] = 0

class KPIDashboard(BaseModel):
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    open_tasks: int = Field(..., description="Number of open tasks")
    active_users: int = Field(..., description="Number of active users")
    open_tickets: int = Field(..., description="Number of open tickets")
    total_tickets: int = Field(..., description="Total number of tickets")
    companies_count: int = Field(..., description="Number of companies")
    completion_rate: float = Field(..., description="Task completion rate percentage")
    task_status_breakdown: Dict[str, int] = Field(..., description="Breakdown by task status")
    database_name: str = Field(..., description="Database name")
    last_update: str = Field(..., description="Last update timestamp")
    error: Optional[str] = Field(None, description="Error message if any")

class AIInsight(BaseModel):
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed insight description")
    type: str = Field(..., description="Insight type: positive, warning, neutral")
    priority: str = Field(..., description="Priority: high, medium, low")
    suggested_action: str = Field(..., description="Suggested action to take")

class InsightsResponse(BaseModel):
    insights: List[AIInsight] = Field(..., description="List of AI-generated insights")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    timeframe: Optional[str] = Field("last_30_days", description="Analysis timeframe")


# ===== SESSION MANAGEMENT =====

class SessionInfo(BaseModel):
    session_id: Union[str, UUID]
    created_at: datetime
    last_activity: datetime
    message_count: int
    user_id: Optional[int] = None

class ClearSessionRequest(BaseModel):
    session_id: Union[str, UUID]

class ClearSessionResponse(BaseModel):
    success: bool
    session_id: Union[str, UUID]
    message: str


# ===== ADVANCED AI FEATURES =====

class ContextualRequest(BaseModel):
    query: str = Field(..., description="User query")
    context: Dict[str, Any] = Field(..., description="Business context")
    analysis_type: Optional[str] = Field("general", description="Type of analysis requested")

class BusinessAnalysisResponse(BaseModel):
    analysis: str = Field(..., description="AI analysis result")
    recommendations: List[str] = Field(default=[], description="AI recommendations")
    confidence: float = Field(..., description="Analysis confidence score")
    data_sources: List[str] = Field(default=[], description="Data sources used")
