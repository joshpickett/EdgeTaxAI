import React from 'react';
import { DocumentStatus } from '../../types/documents';

interface RequiredDocumentsListProps {
  documents: Array<{
    id: string;
    name: string;
    description: string;
    required: boolean;
    status: DocumentStatus;
  }>;
}

export const RequiredDocumentsList: React.FC<RequiredDocumentsListProps> = ({
  documents
}) => {
  return (
    <div className="required-documents-list">
      <h3>Required Documents</h3>
      <div className="documents-grid">
        {documents.map(doc => (
          <div 
            key={doc.id} 
            className={`document-item ${doc.required ? 'required' : 'optional'}`}
          >
            <div className="document-status">
              <span className={`status-indicator ${doc.status.toLowerCase()}`} />
            </div>
            <div className="document-info">
              <h4>{doc.name}</h4>
              <p>{doc.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
