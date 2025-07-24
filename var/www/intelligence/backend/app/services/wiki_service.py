"""
Wiki Service for Intelligence HUB v5.0
Integrates with existing RAG system
"""
import os
import uuid
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.wiki import WikiPage, WikiSection, WikiCategory
from app.schemas.wiki import (
    WikiPageCreate, WikiPageUpdate, WikiPageResponse,
    WikiSectionCreate, WikiSectionResponse,
    WikiCategoryCreate, WikiCategoryResponse
)
from app.modules.rag_engine.vector_service import VectorRAGService
from app.modules.rag_engine.document_processor import DocumentProcessor

class WikiService:
    """
    Wiki service integrato con RAG Qdrant esistente
    """
    
    def __init__(self):
        self.vector_service = VectorRAGService()
        self.doc_processor = DocumentProcessor()
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    # ===== CATEGORY METHODS =====
    def get_categories(self, db: Session) -> List[WikiCategoryResponse]:
        """Get all wiki categories"""
        categories = db.query(WikiCategory).order_by(WikiCategory.sort_order, WikiCategory.name).all()
        return [WikiCategoryResponse.from_orm(cat) for cat in categories]
    
    def create_category(self, db: Session, category_data: WikiCategoryCreate) -> WikiCategoryResponse:
        """Create new wiki category"""
        category = WikiCategory(**category_data.dict())
        db.add(category)
        db.commit()
        db.refresh(category)
        return WikiCategoryResponse.from_orm(category)
    
    # ===== PAGE METHODS =====
    def get_pages(
        self, 
        db: Session, 
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WikiPageResponse]:
        """Get wiki pages with filters"""
        query = db.query(WikiPage)
        
        if status:
            query = query.filter(WikiPage.status == status)
        if category:
            query = query.filter(WikiPage.category == category)
        
        pages = query.order_by(desc(WikiPage.updated_at)).offset(offset).limit(limit).all()
        return [WikiPageResponse.from_orm(page) for page in pages]
    
    def get_page_by_slug(self, db: Session, slug: str) -> Optional[WikiPageResponse]:
        """Get wiki page by slug"""
        page = db.query(WikiPage).filter(WikiPage.slug == slug).first()
        if page:
            # Increment view count
            page.view_count += 1
            page.last_viewed_at = datetime.utcnow()
            db.commit()
            return WikiPageResponse.from_orm(page)
        return None
    
    def create_page(self, db: Session, page_data: WikiPageCreate, author_id: str) -> WikiPageResponse:
        """Create new wiki page"""
        # Generate slug if not provided
        if not page_data.slug:
            page_data.slug = self._generate_slug(page_data.title)
        
        # Ensure unique slug
        page_data.slug = self._ensure_unique_slug(db, page_data.slug)
        
        page = WikiPage(
            **page_data.dict(exclude={'source_document_id'}),
            source_document_id=uuid.UUID(page_data.source_document_id) if page_data.source_document_id else None,
            author_id=author_id,
            editor_id=author_id
        )
        
        db.add(page)
        db.commit()
        db.refresh(page)
        
        return WikiPageResponse.from_orm(page)
    
    def update_page(self, db: Session, page_id: int, page_data: WikiPageUpdate, editor_id: str) -> Optional[WikiPageResponse]:
        """Update wiki page"""
        page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
        if not page:
            return None
        
        # Update fields
        for field, value in page_data.dict(exclude_unset=True).items():
            setattr(page, field, value)
        
        page.editor_id = editor_id
        page.updated_at = datetime.utcnow()
        
        # If publishing, set published_at
        if page_data.status == "published" and not page.published_at:
            page.published_at = datetime.utcnow()
        
        db.commit()
        db.refresh(page)
        
        return WikiPageResponse.from_orm(page)
    
    def delete_page(self, db: Session, page_id: int) -> bool:
        """Delete wiki page"""
        page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
        if not page:
            return False
        
        # Remove from vector database
        try:
            self._remove_page_from_vector_db(page_id)
        except Exception as e:
            print(f"Warning: Could not remove from vector DB: {e}")
        
        db.delete(page)
        db.commit()
        return True
    
    # ===== DOCUMENT PROCESSING =====
    async def process_document_for_wiki(
        self, 
        file_path: str, 
        title: str,
        category: Optional[str] = None,
        author_id: str = "system"
    ) -> Dict[str, Any]:
        """Process uploaded document for wiki creation"""
        try:
            # Extract content
            extraction_result = await self.doc_processor.extract_text(file_path)
            if not extraction_result['success']:
                return {
                    'success': False,
                    'error': extraction_result.get('error', 'Failed to extract content')
                }
            
            content = extraction_result['text']
            
            # Generate sections automatically
            sections = self._auto_generate_sections(content)
            
            # Generate HTML preview
            html_preview = self._generate_html_preview(content, sections)
            
            # Generate excerpt
            excerpt = self._generate_excerpt(content)
            
            return {
                'success': True,
                'content': content,
                'sections': sections,
                'html_preview': html_preview,
                'excerpt': excerpt,
                'metadata': {
                    'file_path': file_path,
                    'original_title': title,
                    'suggested_category': category,
                    'word_count': len(content.split()),
                    'estimated_reading_time': max(1, len(content.split()) // 200)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Processing failed: {str(e)}"
            }
    
    async def create_page_from_document(
        self,
        db: Session,
        processing_result: Dict[str, Any],
        page_data: WikiPageCreate,
        author_id: str
    ) -> WikiPageResponse:
        """Create wiki page from processed document"""
        # Create the page
        page = self.create_page(db, page_data, author_id)
        
        # Create sections if provided
        if 'sections' in processing_result:
            for i, section_data in enumerate(processing_result['sections']):
                section = WikiSection(
                    page_id=page.id,
                    section_title=section_data.get('title', f"Section {i+1}"),
                    content_markdown=section_data.get('content', ''),
                    section_order=i,
                    section_level=section_data.get('level', 1),
                    section_type='text'
                )
                db.add(section)
        
        db.commit()
        
        # Add to vector database
        if page.content_markdown:
            await self._add_page_to_vector_db(page)
        
        return page
    
    # ===== SEARCH METHODS =====
    async def search_wiki(
        self, 
        query: str, 
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search wiki content using vector similarity"""
        try:
            # Use existing RAG service for semantic search
            search_results = await self.vector_service.semantic_search(
                query=query,
                top_k=limit,
                filter_metadata={'content_type': 'wiki'}
            )
            
            # Enrich with page information
            enriched_results = []
            for result in search_results:
                metadata = result.get('metadata', {})
                page_id = metadata.get('wiki_page_id')
                
                if page_id:
                    page = db.query(WikiPage).filter(WikiPage.id == page_id).first()
                    if page:
                        enriched_results.append({
                            'score': result.get('score', 0),
                            'text': result.get('text', ''),
                            'page': {
                                'id': page.id,
                                'slug': page.slug,
                                'title': page.title,
                                'excerpt': page.excerpt,
                                'category': page.category,
                                'status': page.status
                            }
                        })
            
            return enriched_results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    # ===== PRIVATE HELPER METHODS =====
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug.strip())
        return slug[:255]
    
    def _ensure_unique_slug(self, db: Session, slug: str) -> str:
        """Ensure slug is unique by appending number if needed"""
        original_slug = slug
        counter = 1
        
        while db.query(WikiPage).filter(WikiPage.slug == slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _auto_generate_sections(self, content: str) -> List[Dict[str, Any]]:
        """Auto-generate sections from content structure"""
        sections = []
        
        # Simple section detection based on line breaks and headers
        lines = content.split('\n')
        current_section = {'title': 'Introduction', 'content': '', 'level': 1}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headers (simple heuristic)
            if (len(line) < 100 and 
                (line.isupper() or 
                 line.startswith('#') or 
                 any(keyword in line.lower() for keyword in ['capitolo', 'sezione', 'parte']))):
                
                # Save previous section
                if current_section['content'].strip():
                    sections.append(current_section.copy())
                
                # Start new section
                current_section = {
                    'title': line.replace('#', '').strip(),
                    'content': '',
                    'level': line.count('#') if line.startswith('#') else 1
                }
            else:
                current_section['content'] += line + '\n'
        
        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections if sections else [{'title': 'Content', 'content': content, 'level': 1}]
    
    def _generate_html_preview(self, content: str, sections: List[Dict[str, Any]]) -> str:
        """Generate HTML preview from content and sections"""
        html = "<div class='wiki-preview'>"
        
        for section in sections:
            level = section.get('level', 1)
            title = section.get('title', 'Untitled')
            section_content = section.get('content', '')
            
            html += f"<h{level}>{title}</h{level}>"
            html += f"<div class='section-content'>{section_content.replace(chr(10), '<br>')}</div>"
        
        html += "</div>"
        return html
    
    def _generate_excerpt(self, content: str, max_length: int = 300) -> str:
        """Generate excerpt from content"""
        words = content.split()
        if len(' '.join(words)) <= max_length:
            return content
        
        excerpt = ''
        for word in words:
            if len(excerpt + ' ' + word) > max_length:
                break
            excerpt += ' ' + word if excerpt else word
        
        return excerpt + '...' if len(content) > max_length else excerpt
    
    async def _add_page_to_vector_db(self, page: WikiPage):
        """Add wiki page to vector database"""
        content = page.content_markdown or page.content_html or ''
        if not content:
            return
        
        # Create chunks
        chunks = self._create_chunks(content)
        
        # Add to Qdrant with wiki metadata
        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_chunk_id(page.id, i)
            metadata = {
                'content_type': 'wiki',
                'wiki_page_id': page.id,
                'page_slug': page.slug,
                'page_title': page.title,
                'category': page.category,
                'chunk_index': i,
                'created_at': datetime.utcnow().isoformat()
            }
            
            await self.vector_service.add_point(chunk_id, chunk, metadata)
    
    def _remove_page_from_vector_db(self, page_id: int):
        """Remove wiki page from vector database"""
        # This would need to be implemented in VectorRAGService
        # For now, we'll leave it as placeholder
        pass
    
    def _create_chunks(self, content: str) -> List[str]:
        """Create chunks from content"""
        chunks = []
        for i in range(0, len(content), self.chunk_size - self.chunk_overlap):
            chunk = content[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def _generate_chunk_id(self, page_id: int, chunk_index: int) -> int:
        """Generate unique chunk ID for Qdrant"""
        combined = f"wiki_{page_id}_{chunk_index}"
        hash_obj = hashlib.md5(combined.encode())
        return int.from_bytes(hash_obj.digest()[:8], byteorder='big') % (2**31 - 1)
