import { AuthProvider } from "./contexts/AuthContext";
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './components/auth/LoginPage';
import GoogleAuthSuccess from './components/auth/GoogleAuthSuccess';
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
import TaskManagement from "./components/tasks/TaskManagement";
import ModelliTicket from "./components/templates/ModelliTicket";
import ServiziTemplate from "./components/servizi-template/ServiziTemplate";
import ModelliTicket from "./components/templates/ModelliTicket";
import ServiziTemplate from "./components/servizi-template/ServiziTemplate";
import EmailCenter from './components/email/EmailCenter';
import Articles from "./components/articles/Articles";
import TipologieServizi from "./components/tipologie-servizi/TipologieServizi";
import Partner from "./components/partner/Partner";
import KitCommerciali from "./components/kit-commerciali/KitCommerciali";
import CommercialTickets from "./pages/dashboard/CommercialTickets";
import TasksGlobalManagement from "./components/workflow/TasksGlobalManagement";
import WorkflowManagement from "./components/workflow/WorkflowManagement";
import TaskDetailPage from "./pages/tasks/TaskDetailPage";
import TicketDetailPage from "./pages/tickets/TicketDetailPage";
import WikiPage from "./pages/wiki/WikiPage";
import WikiPageViewer from "./components/wiki/WikiPageViewer";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/success" element={<GoogleAuthSuccess />} />
          
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
            <Route path="ticket-commerciali" element={<CommercialTickets />} />
            <Route path="tipologie-servizi" element={<TipologieServizi />} />
            <Route path="partner" element={<Partner />} />
            <Route path="tasks-global" element={<TasksGlobalManagement />} />
            <Route path="workflow-management" element={<WorkflowManagement />} />
            <Route path="tasks" element={<TaskManagement />} />
            <Route path="tasks/:taskId" element={<TaskDetailPage />} />
            <Route path="tickets/:ticketId" element={<TicketDetailPage />} />
            <Route path="modelli-ticket" element={<ModelliTicket />} />
            <Route path="chat" element={<IntelliChat />} />
            <Route path="documents" element={<DocumentsRAG />} />
            <Route path="web-scraping" element={<WebScraping />} />
            <Route path="assessment" element={<Assessment />} />
            <Route path="email-center" element={<EmailCenter />} />
            <Route path="wiki" element={<WikiPage />} />
            <Route path="wiki/pages/:slug" element={<WikiPageViewer />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

// Importa il componente Workflow Management
import WorkflowManagement from "./components/workflow/WorkflowManagement";
import TaskDetailPage from "./pages/tasks/TaskDetailPage";
import TicketDetailPage from "./pages/tickets/TicketDetailPage";
