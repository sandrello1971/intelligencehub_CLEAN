"""
Wiki Schemas for Intelligence HUB v5.0
Pydantic schemas for wiki API validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WikiStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class SectionType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    CHART = "chart"
    IMAGE = "image"
    CODE = "code"

# ===== CATEGORY SCHEMAS =====
class WikiCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    sort_order: int = Field(default=0)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)

class WikiCategoryCreate(WikiCategoryBase):
    pass

class WikiCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    sort_order: Optional[int] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)

class WikiCategoryResponse(WikiCategoryBase):
    id: int
    page_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== SECTION SCHEMAS =====
class WikiSectionBase(BaseModel):
    section_title: Optional[str] = Field(None, max_length=255)
    content_markdown: Optional[str] = None
    content_html: Optional[str] = None
    section_order: int = Field(default=0)
    section_level: int = Field(default=1, ge=1, le=6)
    section_type: SectionType = Field(default=SectionType.TEXT)
    vector_chunk_ids: Optional[List[str]] = None

class WikiSectionCreate(WikiSectionBase):
    page_id: int

class WikiSectionUpdate(BaseModel):
    section_title: Optional[str] = Field(None, max_length=255)
    content_markdown: Optional[str] = None
    content_html: Optional[str] = None
    section_order: Optional[int] = None
    section_level: Optional[int] = Field(None, ge=1, le=6)
    section_type: Optional[SectionType] = None

class WikiSectionResponse(WikiSectionBase):
    id: int
    page_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== PAGE SCHEMAS =====
class WikiPageBase(BaseModel):
    title: str = Field(..., max_length=500)
    content_markdown: Optional[str] = None
    content_html: Optional[str] = None
    excerpt: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    status: WikiStatus = Field(default=WikiStatus.DRAFT)
    meta_description: Optional[str] = Field(None, max_length=500)
    search_keywords: Optional[str] = None

    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v

class WikiPageCreate(WikiPageBase):
    slug: Optional[str] = Field(None, max_length=255)
    source_document_id: Optional[str] = None  # UUID as string
    
    @validator('slug')
    def validate_slug(cls, v, values):
        if not v and 'title' in values:
            # Auto-generate slug from title
            import re
            title = values['title']
            slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
            slug = re.sub(r'\s+', '-', slug.strip())
            return slug[:255]
        return v

class WikiPageUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content_markdown: Optional[str] = None
    content_html: Optional[str] = None
    excerpt: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    status: Optional[WikiStatus] = None
    meta_description: Optional[str] = Field(None, max_length=500)
    search_keywords: Optional[str] = None
    editor_id: Optional[str] = None

    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v

class WikiPageResponse(WikiPageBase):
    id: int
    slug: str
    source_document_id: Optional[str] = None
    published_at: Optional[datetime] = None
    author_id: Optional[str] = None
    editor_id: Optional[str] = None
    view_count: int
    last_viewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    sections: Optional[List[WikiSectionResponse]] = None
    
    class Config:
        from_attributes = True

# ===== WIKI UPLOAD SCHEMAS =====
class WikiDocumentUpload(BaseModel):
    title: str = Field(..., max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    auto_publish: bool = Field(default=False)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v

class WikiProcessingResult(BaseModel):
    document_id: str
    wiki_page_id: Optional[int] = None
    processing_status: str
    sections_created: int
    chunks_created: int
    preview_html: Optional[str] = None
    errors: List[str] = []

# ===== WIKI CHAT SCHEMAS =====
class WikiChatQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    wiki_only: bool = Field(default=False)
    include_sources: bool = Field(default=True)

class WikiChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[Dict[str, Any]] = []
    wiki_pages_referenced: List[int] = []
    response_time_ms: int
    confidence_score: Optional[float] = None

# ===== WIKI STATS SCHEMAS =====
class WikiStats(BaseModel):
    total_pages: int
    published_pages: int
    draft_pages: int
    total_categories: int
    total_views: int
    recent_activity: Dict[str, Any]
