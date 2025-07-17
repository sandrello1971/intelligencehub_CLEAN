import React, { useState } from 'react';
import AdminLayout from './AdminLayout';
import UserManagement from './UserManagement';
import IntelliChat from './IntelliChat';
import DocumentManager from '../rag/DocumentManager';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('users');

  const renderContent = () => {
    switch (activeTab) {
      case 'users':
        return <UserManagement />;
      case 'chat':
        return <IntelliChat />;
      case 'documents':
        return <DocumentManager />;
      case 'dashboard':
        return <div className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Dashboard</h2>
          <p className="text-gray-600">Dashboard in arrivo...</p>
        </div>;
      case 'settings':
        return <div className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Impostazioni</h2>
          <p className="text-gray-600">Impostazioni in arrivo...</p>
        </div>;
      default:
        return <UserManagement />;
    }
  };

  return (
    <AdminLayout activeTab={activeTab} onTabChange={setActiveTab}>
      {renderContent()}
    </AdminLayout>
  );
};

export default AdminDashboard;
