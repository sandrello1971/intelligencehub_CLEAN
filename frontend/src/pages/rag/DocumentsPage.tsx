import React from 'react';
import DocumentManager from '../../components/rag/DocumentManager';

const DocumentsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <DocumentManager />
    </div>
  );
};

export default DocumentsPage;
