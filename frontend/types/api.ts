export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ChatMessageRequest {
  message: string;
  conversation_id?: string;
  company_id?: number;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  timestamp: string;
}

export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  company_id?: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
  expires_in: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
