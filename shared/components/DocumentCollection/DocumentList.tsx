import React from 'react';
import { DocumentType, DocumentStatus } from '../../types/documents';

interface DocumentListProps {
  documents: Array<{
    id: string;
    type: DocumentType;
    status: DocumentStatus;
    fileName: string;
    version: number;
    metadata?: Record<string, any>;
  }>;
  onVersionSelect?: (documentId: string, version: number) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, onVersionSelect }) => {
  const getStatusColor = (status: DocumentStatus): string => {
    switch (status) {
      case DocumentStatus.PROCESSED:
        return 'green';
      case DocumentStatus.PROCESSING:
        return 'orange';
      case DocumentStatus.ERROR:
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <div className="document-list">
      {documents.map(doc => (
        <div key={doc.id} className="document-item">
          <span className="document-name">{doc.fileName}</span>
          <span 
            className="document-status"
            style={{ color: getStatusColor(doc.status) }}
          >
            {doc.status}
            {doc.version > 1 && (
              <span className="version-badge">
                v{doc.version}
              </span>
            )}
          </span>
          {doc.metadata && <div className="document-metadata">...</div>}
        </div>
      ))}
    </div>
  );
};
