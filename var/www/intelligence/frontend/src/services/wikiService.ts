// services/wikiService.ts
// Wiki API Service for Intelligence HUB Frontend

import { apiClient } from './api';

export interface WikiCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parent_category_id?: number;
  sort_order: number;
  color?: string;
  icon?: string;
  page_count: number;
  created_at: string;
}

export interface WikiSection {
  id: number;
  page_id: number;
  section_title?: string;
  content_markdown?: string;
  content_html?: string;
  section_order: number;
  section_level: number;
  section_type: string;
  vector_chunk_ids?: any;
  created_at: string;
}

export interface WikiPage {
  id: number;
  slug: string;
  title: string;
  content_markdown?: string;
  content_html?: string;
  excerpt?: string;
  source_document_id?: string;
  category?: string;
  tags: string[];
  status: 'draft' | 'review' | 'published' | 'archived';
  published_at?: string;
  author_id?: string;
  editor_id?: string;
  meta_description?: string;
  search_keywords?: string;
  view_count: number;
  last_viewed_at?: string;
  created_at: string;
  updated_at: string;
  sections?: WikiSection[];
}

export interface WikiUploadResult {
  document_id: string;
  wiki_page_id?: number;
  processing_status: string;
  sections_created: number;
  chunks_created: number;
  preview_html?: string;
  errors: string[];
}

export interface WikiStats {
  total_pages: number;
  published_pages: number;
  draft_pages: number;
  total_categories: number;
  total_views: number;
  recent_activity: any;
}

export interface WikiSearchResult {
  query: string;
  results: Array<{
    score: number;
    text: string;
    page: {
      id: number;
      slug: string;
      title: string;
      excerpt?: string;
      category?: string;
      status: string;
    };
  }>;
  total: number;
}

class WikiService {
  private baseURL = '/api/v1/wiki';

  // Categories
  async getCategories() {
    return apiClient.get<WikiCategory[]>(`${this.baseURL}/categories`);
  }

  async createCategory(data: Partial<WikiCategory>) {
    return apiClient.post<WikiCategory>(`${this.baseURL}/categories`, data);
  }

  // Pages
  async getPages(params?: {
    status?: string;
    category?: string;
    limit?: number;
    offset?: number;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append("status", params.status);
    if (params?.category) searchParams.append("category", params.category);
    if (params?.limit) searchParams.append("limit", params.limit.toString());
    if (params?.offset) searchParams.append("offset", params.offset.toString());
    
    const queryString = searchParams.toString();
    const url = queryString ? `/api/v1/wiki/pages?${queryString}` : "/api/v1/wiki/pages";
    
    try {
      const response = await fetch(`https://intelligencehub.enduser-digital.com${url}`);
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getPageBySlug(slug: string) {
    try {
      const response = await fetch(`https://intelligencehub.enduser-digital.com/api/v1/wiki/pages/${slug}`);
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async createPage(data: Partial<WikiPage>) {
    return apiClient.post<WikiPage>(`${this.baseURL}/pages`, data);
  }

  async updatePage(pageId: number, data: Partial<WikiPage>) {
    return apiClient.put<WikiPage>(`${this.baseURL}/pages/${pageId}`, data);
  }

  async deletePage(pageId: number) {
    return apiClient.delete(`${this.baseURL}/pages/${pageId}`);
  }

  // Upload
  async uploadDocument(
    file: File,
    title: string,
    category?: string,
    tags?: string[],
    autoPublish: boolean = false
  ) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (category) formData.append('category', category);
    if (tags) formData.append('tags', JSON.stringify(tags));
    formData.append('auto_publish', autoPublish.toString());

    const response = await fetch(`${this.baseURL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json() as Promise<WikiUploadResult>;
  }

  // Search
  async search(query: string, limit: number = 10) {
    const searchParams = new URLSearchParams();
    searchParams.append('q', query);
    searchParams.append('limit', limit.toString());
    
    return apiClient.get<WikiSearchResult>(`${this.baseURL}/search?${searchParams.toString()}`);
  }

  // Stats
  async getStats() {
    return apiClient.get<WikiStats>(`${this.baseURL}/stats`);
  }

  // Chat (future implementation)
  async chat(query: string, sessionId?: string) {
    return apiClient.post(`${this.baseURL}/chat`, {
      query,
      session_id: sessionId,
      wiki_only: true,
      include_sources: true
    });
  }

  // Unified search for chat integration
  async searchForChat(query: string) {
    try {
      const response = await fetch(`https://intelligencehub.enduser-digital.com/api/v1/wiki/search?q=${encodeURIComponent(query)}&limit=5`);
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Chat with wiki content
  async chatWithWiki(query: string, sessionId?: string) {
    try {
      const response = await fetch("https://intelligencehub.enduser-digital.com/api/v1/wiki/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          session_id: sessionId,
          wiki_only: false,
          include_sources: true
        })
      });
      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

export const wikiService = new WikiService();
export default wikiService;
