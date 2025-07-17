import { AuthProvider } from "./contexts/AuthContext";
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './components/auth/LoginPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import MainLayout from './components/layout/MainLayout';

// Import componenti reali
import Dashboard from './components/dashboard/Dashboard';
import UserManagementComplete from './components/users/UserManagementComplete';
import Companies from './components/companies/Companies';
import IntelliChat from './components/chat/IntelliChat';
import DocumentsRAG from './components/documents/DocumentsRAG';
import WebScraping from './components/webscraping/WebScraping';
import Assessment from './components/assessment/Assessment';
import EmailCenter from './components/email/EmailCenter';
import Articles from "./components/articles/Articles";
import TipologieServizi from "./components/tipologie-servizi/TipologieServizi";
import Partner from "./components/partner/Partner";
import KitCommerciali from "./components/kit-commerciali/KitCommerciali";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="users" element={<UserManagementComplete />} />
            <Route path="aziende" element={<Companies />} />
            <Route path="articoli" element={<Articles />} />
            <Route path="kit-commerciali" element={<KitCommerciali />} />
            <Route path="tipologie-servizi" element={<TipologieServizi />} />
            <Route path="partner" element={<Partner />} />
            <Route path="chat" element={<IntelliChat />} />
            <Route path="documents" element={<DocumentsRAG />} />
            <Route path="web-scraping" element={<WebScraping />} />
            <Route path="assessment" element={<Assessment />} />
            <Route path="email-center" element={<EmailCenter />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
