"""
Intelligence AI Chat Module
Core AI engine for conversational interface and task generation
"""
from .services import IntelliChatService
from .schemas import ChatRequest, ChatResponse, AIInsight, KPIDashboard

__all__ = [
    "IntelliChatService",
    "ChatRequest",
    "ChatResponse", 
    "AIInsight",
    "KPIDashboard"
]
