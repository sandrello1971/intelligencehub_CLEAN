"""
Wiki Models for Intelligence HUB v5.0
SQLAlchemy models for wiki functionality
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.core.database import Base

class WikiCategory(Base):
    """
    Wiki categories model
    """
    __tablename__ = "wiki_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_category_id = Column(Integer, ForeignKey('wiki_categories.id'))
    
    # Visual and ordering
    sort_order = Column(Integer, default=0)
    color = Column(String(7))  # HEX color
    icon = Column(String(50))
    page_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())    
    def __repr__(self):
        return f"<WikiCategory(id={self.id}, name='{self.name}', slug='{self.slug}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'parent_category_id': self.parent_category_id,
            'sort_order': self.sort_order,
            'color': self.color,
            'icon': self.icon,
            'page_count': self.page_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WikiPage(Base):
    """
    Main wiki page model
    """
    __tablename__ = "wiki_pages"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    
    # Content
    content_markdown = Column(Text)
    content_html = Column(Text)
    excerpt = Column(Text)
    
    # Source document reference (UUID)
    source_document_id = Column(UUID, ForeignKey('knowledge_documents.id'))
    
    # Categorization
    category = Column(String(100), index=True)
    tags = Column(ARRAY(String))
    
    # Publication status
    status = Column(String(50), default='draft', index=True)
    published_at = Column(DateTime, index=True)
    
    # Authors
    author_id = Column(String(100))
    editor_id = Column(String(100))
    
    # SEO and discovery
    meta_description = Column(String(500))
    search_keywords = Column(Text)
    
    # Statistics
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sections = relationship("WikiSection", back_populates="page", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WikiPage(id={self.id}, slug='{self.slug}', title='{self.title}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'content_markdown': self.content_markdown,
            'content_html': self.content_html,
            'excerpt': self.excerpt,
            'source_document_id': str(self.source_document_id) if self.source_document_id else None,
            'category': self.category,
            'tags': self.tags or [],
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author_id': self.author_id,
            'editor_id': self.editor_id,
            'meta_description': self.meta_description,
            'search_keywords': self.search_keywords,
            'view_count': self.view_count,
            'last_viewed_at': self.last_viewed_at.isoformat() if self.last_viewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WikiSection(Base):
    """
    Wiki page sections model
    """
    __tablename__ = "wiki_sections"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey('wiki_pages.id', ondelete='CASCADE'), nullable=False)
    
    # Section structure
    section_title = Column(String(255))
    content_markdown = Column(Text)
    content_html = Column(Text)
    section_order = Column(Integer, default=0)
    section_level = Column(Integer, default=1)  # 1=h1, 2=h2, etc.
    
    # Vector chunks reference
    vector_chunk_ids = Column(JSONB)  # Array of chunk IDs in Qdrant
    
    # Content type
    section_type = Column(String(50), default='text')  # text, table, chart, image, code
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    page = relationship("WikiPage", back_populates="sections")
    
    def __repr__(self):
        return f"<WikiSection(id={self.id}, page_id={self.page_id}, title='{self.section_title}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'section_title': self.section_title,
            'content_markdown': self.content_markdown,
            'content_html': self.content_html,
            'section_order': self.section_order,
            'section_level': self.section_level,
            'vector_chunk_ids': self.vector_chunk_ids,
            'section_type': self.section_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
