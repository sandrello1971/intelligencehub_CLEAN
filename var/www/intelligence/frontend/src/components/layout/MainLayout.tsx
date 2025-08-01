import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';

const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const menuItems = [
    { path: '/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/users', icon: '👥', label: 'Gestione Utenti' },
    { path: '/aziende', icon: '🏢', label: 'Aziende' },
    { path: '/articoli', icon: '📄', label: 'Articoli' },
    { path: '/partner', icon: '🤝', label: 'Partner' },
    { path: '/tipologie-servizi', icon: '🏷️', label: 'Tipologie Servizi' },
    { path: '/kit-commerciali', icon: '📦', label: 'Kit Commerciali' },
    { path: "/ticket-commerciali", icon: "🎫", label: "Ticket Customer Care" },
    { path: '/workflow-management', icon: '⚙️', label: 'Workflow Management' },
    { path: "/tasks", icon: "⏰", label: "Modelli Task" },
    { path: "/modelli-ticket", icon: "🎫", label: "Modelli Ticket" },
    { path: "/servizi-template", icon: "🔗", label: "Servizi-Template" },
    { path: '/chat', icon: '🤖', label: 'IntelliChatAI' },
    { path: '/documents', icon: '📚', label: 'Document RAG' },
    { path: '/web-scraping', icon: '🕷️', label: 'Web Scraping' },
    { path: '/assessment', icon: '📊', label: 'Assessment' },
    { path: '/email-center', icon: '📧', label: 'Email Center' },
    { path: '/wiki', icon: '📖', label: 'Wiki' },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
      {/* Sidebar */}
      <nav style={{
        width: '280px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '20px',
        boxShadow: '2px 0 10px rgba(0,0,0,0.1)'
      }}>
        {/* Header */}
        <div style={{ 
          paddingBottom: '20px', 
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          marginBottom: '20px'
        }}>
          <h1 style={{ fontSize: '22px', fontWeight: 700, margin: '0 0 5px 0' }}>
            🧠 IntelligenceHUB
          </h1>
          <p style={{ fontSize: '12px', opacity: 0.8, margin: 0 }}>
            v5.0 - AI Business Platform
          </p>
        </div>

        {/* Menu Items */}
        <div style={{ marginBottom: '20px' }}>
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                textDecoration: 'none',
                color: 'white',
                borderRadius: '8px',
                marginBottom: '8px',
                transition: 'all 0.2s',
                fontWeight: isActive(item.path) ? 600 : 500,
                fontSize: '14px',
                background: isActive(item.path) ? 'rgba(255,255,255,0.2)' : 'transparent'
              }}
              onMouseOver={(e) => {
                if (!isActive(item.path)) {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                  e.currentTarget.style.transform = 'translateX(4px)';
                }
              }}
              onMouseOut={(e) => {
                if (!isActive(item.path)) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.transform = 'translateX(0)';
                }
              }}
            >
              <span style={{ fontSize: '16px' }}>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>

        {/* User Info + Logout nella sidebar */}
        <div style={{
          paddingTop: '20px',
          borderTop: '1px solid rgba(255,255,255,0.1)'
        }}>
          <div style={{ marginBottom: '12px', fontSize: '12px' }}>
            <strong>Stefano Andrello</strong>
            <div style={{ opacity: 0.7 }}>
              s.andrello@enduser-italia.com
            </div>
          </div>
          
          <button
            onClick={handleLogout}
            style={{
              background: 'rgba(255,255,255,0.1)',
              border: '1px solid rgba(255,255,255,0.2)',
              color: 'white',
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '12px',
              cursor: 'pointer',
              width: '100%',
              fontWeight: 500,
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
            }}
          >
            🚪 Logout
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{
        flex: 1, padding: "20px",
        background: '#f8fafc',
        minHeight: '100vh'
      }}>
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
