import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  username: string;
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // CALCOLA isAuthenticated AUTOMATICAMENTE
  const isAuthenticated = Boolean(user);
  console.log("🔍 AuthContext - isAuthenticated:", isAuthenticated, "user:", user, "token:", localStorage.getItem("access_token"));

  useEffect(() => {
    // Check se già loggato
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (e) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      console.log('🔐 Starting login...'); // DEBUG
      
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: email, password })
      });

      const data = await response.json();
      console.log('📨 Backend response:', data); // DEBUG

      if (response.ok && data.access_token) {
        // CREA USER OBJECT FORZATO
        const userData: User = {
          id: data.user_id || "stefano-andrello-001",
          username: email,
          email: data.email || email,
          name: data.name || "Stefano Andrello", 
          role: data.role || "admin"
        };

        console.log('👤 Created user object:', userData); // DEBUG

        // SALVA TUTTO
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(userData));
        
        // AGGIORNA STATE
        setUser(userData);
        
        console.log('✅ Login completed, user set:', userData); // DEBUG
        
        return { success: true };
      } else {
        return { success: false, error: 'Credenziali non valide' };
      }
    } catch (error) {
      console.error('❌ Login error:', error); // DEBUG
      return { success: false, error: 'Errore di connessione' };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
