"""
Hashtags and associations for categorization
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Table
#from sqlalchemy.orm import relationship
from .base import Base

class Hashtag(Base):
    __tablename__ = "hashtags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)

# Association tables for many-to-many relationships
task_hashtag = Table(
    'task_hashtag',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'), primary_key=True)
)

ticket_hashtag = Table(
    'ticket_hashtag', 
    Base.metadata,
    Column('ticket_id', Integer, ForeignKey('tickets.id'), primary_key=True),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'), primary_key=True)
)
