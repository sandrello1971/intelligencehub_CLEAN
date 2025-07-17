from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_companies: int
    total_commesse: int
    active_commesse: int
    total_milestones: int
    completed_milestones: int
    total_tickets: int
    open_tickets: int
    total_tasks: int
    completed_tasks: int
    
class UserPerformance(BaseModel):
    user_id: str
    username: str
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    avg_completion_time: Optional[float] = None
    active_tickets: int
    
class CompanyPerformance(BaseModel):
    company_id: int
    company_name: str
    total_commesse: int
    active_commesse: int
    total_value: Optional[float] = None
    completion_rate: float
    
class SLAStatus(BaseModel):
    total_items: int
    on_time: int
    overdue: int
    at_risk: int
    sla_performance: float
    
class ProjectOverview(BaseModel):
    commessa_id: int
    titolo: str
    company_name: str
    status: str
    progress: float
    milestones_completed: int
    milestones_total: int
    budget: Optional[float] = None
    
class MilestoneTimeline(BaseModel):
    milestone_id: int
    titolo: str
    commessa_title: str
    data_scadenza: Optional[datetime] = None
    status: str
    days_remaining: Optional[int] = None
    
class TemplateUsage(BaseModel):
    template_id: int
    template_name: str
    usage_count: int
    last_used: Optional[datetime] = None
    category: Optional[str] = None
    
class DashboardResponse(BaseModel):
    stats: SystemStats
    user_performance: List[UserPerformance]
    company_performance: List[CompanyPerformance]
    sla_status: SLAStatus
    project_overview: List[ProjectOverview]
    milestone_timeline: List[MilestoneTimeline]
    template_usage: List[TemplateUsage]
    last_updated: datetime
