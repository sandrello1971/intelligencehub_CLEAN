// MODIFICA TEST - Se vedi questo nella build, Vite funziona
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './components/auth/Login';
import ChangePassword from './components/auth/ChangePassword';
import AdminDashboard from './components/admin/AdminDashboard';
import ProtectedRoute from './components/auth/ProtectedRoute';
import DocumentsPage from './pages/rag/DocumentsPage';
import IntelliChatPage from './pages/rag/IntelliChatPage';
import GoogleAuthSuccess from './components/auth/GoogleAuthSuccess';

const App: React.FC = () => {
  console.log("App.tsx loaded with auth/success route");
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/change-password" element={<ChangePassword />} />
          <Route path="/auth/success" element={<GoogleAuthSuccess />} />
          <Route path="/admin" element={
            <ProtectedRoute>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="/documents" element={
            <ProtectedRoute>
              <DocumentsPage />
            </ProtectedRoute>
          } />
          <Route path="/intellichat" element={
            <ProtectedRoute>
              <IntelliChatPage />
            </ProtectedRoute>
          } />
          <Route path="/" element={<Navigate to="/admin" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
