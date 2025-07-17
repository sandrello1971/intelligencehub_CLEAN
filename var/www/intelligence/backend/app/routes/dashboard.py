from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.routes.auth import get_current_user_dep
from app.schemas.dashboard import (
    SystemStats, UserPerformance, CompanyPerformance, 
    SLAStatus, ProjectOverview, MilestoneTimeline, 
    TemplateUsage, DashboardResponse
)
from app.models.users import User
from app.models.commesse import Commessa, Milestone
from app.models.ticket import Ticket
from app.models.task import Task
from app.models.company import Company

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Statistiche generali del sistema"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    stats = SystemStats(
        total_users=db.query(User).count(),
        active_users=db.query(User).filter(User.is_active == True).count(),
        total_companies=db.query(Company).count(),
        total_commesse=db.query(Commessa).count(),
        active_commesse=db.query(Commessa).filter(Commessa.status == 'active').count(),
        total_milestones=db.query(Milestone).count(),
        completed_milestones=db.query(Milestone).filter(Milestone.status == 'completed').count(),
        total_tickets=db.query(Ticket).count(),
        open_tickets=db.query(Ticket).filter(Ticket.status.in_(['open', 'in_progress'])).count(),
        total_tasks=db.query(Task).count(),
        completed_tasks=db.query(Task).filter(Task.status == 'completed').count()
    )
    
    return stats

@router.get("/user-performance", response_model=List[UserPerformance])
async def get_user_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Performance utenti"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Query per performance utenti
    user_stats = db.query(
        User.id,
        User.username,
        func.count(Task.id).label('total_tasks'),
        func.sum(case((Task.status == 'completed', 1), else_=0)).label('completed_tasks'),
        func.count(Ticket.id).label('active_tickets')
    ).outerjoin(Task, User.id == Task.owner)\
     .outerjoin(Ticket, User.id == Ticket.owner_id)\
     .group_by(User.id, User.username)\
     .all()
    
    performance_list = []
    for stat in user_stats:
        completion_rate = (stat.completed_tasks / stat.total_tasks * 100) if stat.total_tasks > 0 else 0
        performance_list.append(UserPerformance(
            user_id=stat.id,
            username=stat.username,
            total_tasks=stat.total_tasks,
            completed_tasks=stat.completed_tasks,
            completion_rate=completion_rate,
            active_tickets=stat.active_tickets
        ))
    
    return performance_list

@router.get("/company-performance", response_model=List[CompanyPerformance])
async def get_company_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Performance aziende"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    company_stats = db.query(
        Company.id,
        Company.nome,
        func.count(Commessa.id).label('total_commesse'),
        func.sum(case((Commessa.status == 'active', 1), else_=0)).label('active_commesse'),
        func.sum(Commessa.budget).label('total_value')
    ).outerjoin(Commessa, Company.id == Commessa.company_id)\
     .group_by(Company.id, Company.nome)\
     .all()
    
    performance_list = []
    for stat in company_stats:
        completion_rate = ((stat.total_commesse - stat.active_commesse) / stat.total_commesse * 100) if stat.total_commesse > 0 else 0
        performance_list.append(CompanyPerformance(
            company_id=stat.id,
            company_name=stat.nome,
            total_commesse=stat.total_commesse,
            active_commesse=stat.active_commesse,
            total_value=float(stat.total_value) if stat.total_value else None,
            completion_rate=completion_rate
        ))
    
    return performance_list

@router.get("/sla-status", response_model=SLAStatus)
async def get_sla_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Status SLA sistema"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    now = datetime.now()
    
    # Conta milestone per status SLA
    milestones = db.query(Milestone).filter(
        Milestone.data_scadenza.isnot(None),
        Milestone.status != 'completed'
    ).all()
    
    total_items = len(milestones)
    overdue = sum(1 for m in milestones if m.data_scadenza and m.data_scadenza < now)
    at_risk = sum(1 for m in milestones if m.data_scadenza and m.data_scadenza < now + timedelta(days=3) and m.data_scadenza >= now)
    on_time = total_items - overdue - at_risk
    
    sla_performance = (on_time / total_items * 100) if total_items > 0 else 100
    
    return SLAStatus(
        total_items=total_items,
        on_time=on_time,
        overdue=overdue,
        at_risk=at_risk,
        sla_performance=sla_performance
    )

@router.get("/project-overview", response_model=List[ProjectOverview])
async def get_project_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Overview progetti attivi"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    projects = db.query(
        Commessa.id,
        Commessa.titolo,
        Company.nome.label('company_name'),
        Commessa.status,
        Commessa.budget,
        func.count(Milestone.id).label('total_milestones'),
        func.sum(case((Milestone.status == 'completed', 1), else_=0)).label('completed_milestones')
    ).join(Company, Commessa.company_id == Company.id)\
     .outerjoin(Milestone, Commessa.id == Milestone.commessa_id)\
     .group_by(Commessa.id, Commessa.titolo, Company.nome, Commessa.status, Commessa.budget)\
     .limit(20)\
     .all()
    
    overview_list = []
    for project in projects:
        progress = (project.completed_milestones / project.total_milestones * 100) if project.total_milestones > 0 else 0
        overview_list.append(ProjectOverview(
            commessa_id=project.id,
            titolo=project.titolo,
            company_name=project.company_name,
            status=project.status,
            progress=progress,
            milestones_completed=project.completed_milestones,
            milestones_total=project.total_milestones,
            budget=float(project.budget) if project.budget else None
        ))
    
    return overview_list

@router.get("/milestone-timeline", response_model=List[MilestoneTimeline])
async def get_milestone_timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Timeline milestone"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    now = datetime.now()
    
    milestones = db.query(
        Milestone.id,
        Milestone.titolo,
        Commessa.titolo.label('commessa_title'),
        Milestone.data_scadenza,
        Milestone.status
    ).join(Commessa, Milestone.commessa_id == Commessa.id)\
     .filter(Milestone.data_scadenza.isnot(None))\
     .order_by(Milestone.data_scadenza)\
     .limit(20)\
     .all()
    
    timeline_list = []
    for milestone in milestones:
        days_remaining = None
        if milestone.data_scadenza:
            days_remaining = (milestone.data_scadenza - now).days
        
        timeline_list.append(MilestoneTimeline(
            milestone_id=milestone.id,
            titolo=milestone.titolo,
            commessa_title=milestone.commessa_title,
            data_scadenza=milestone.data_scadenza,
            status=milestone.status,
            days_remaining=days_remaining
        ))
    
    return timeline_list

@router.get("/template-usage", response_model=List[TemplateUsage])
async def get_template_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Statistiche utilizzo template"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Placeholder - da implementare quando avremo dati di utilizzo
    return []

@router.get("/", response_model=DashboardResponse)
async def get_dashboard_complete(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    """Dashboard completa"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Chiamata a tutti gli endpoint per dashboard completa
    stats = await get_system_stats(db, current_user)
    user_performance = await get_user_performance(db, current_user)
    company_performance = await get_company_performance(db, current_user)
    sla_status = await get_sla_status(db, current_user)
    project_overview = await get_project_overview(db, current_user)
    milestone_timeline = await get_milestone_timeline(db, current_user)
    template_usage = await get_template_usage(db, current_user)
    
    return DashboardResponse(
        stats=stats,
        user_performance=user_performance,
        company_performance=company_performance,
        sla_status=sla_status,
        project_overview=project_overview,
        milestone_timeline=milestone_timeline,
        template_usage=template_usage,
        last_updated=datetime.now()
    )
