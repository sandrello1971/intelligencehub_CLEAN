# schemas/admin/__init__.py
# Pydantic schemas per Admin module - IntelligenceHUB

from .tipi_commesse import (
    TipoCommessa,
    TipoCommessaCreate,
    TipoCommessaUpdate,
    TipoCommessaInDB
)

from .milestones import (
    Milestone,
    MilestoneCreate,
    MilestoneUpdate,
    MilestoneInDB
)

from .modelli_task import (
    ModelloTask,
    ModelloTaskCreate,
    ModelloTaskUpdate,
    ModelloTaskInDB
)

__all__ = [
    "TipoCommessa",
    "TipoCommessaCreate", 
    "TipoCommessaUpdate",
    "TipoCommessaInDB",
    "Milestone",
    "MilestoneCreate",
    "MilestoneUpdate", 
    "MilestoneInDB",
    "ModelloTask",
    "ModelloTaskCreate",
    "ModelloTaskUpdate",
    "ModelloTaskInDB"
]
