import React, { useState } from 'react';
import { DocumentType, DocumentStatus } from '../../types/documents';
import { DocumentUploader } from './DocumentUploader';
import { DocumentList } from './DocumentList';
import { ImportOptions } from './ImportOptions';
import { StatusTracker } from './StatusTracker';
import { NotificationCenter } from './NotificationCenter';

interface DocumentCollectionViewProps {
  onDocumentUpload: (file: File, type: DocumentType) => Promise<void>;
  onImportSelect: (source: string) => Promise<void>;
  onStatusChange: (documentId: string, status: DocumentStatus) => void;
  onVersionChange: (documentId: string, version: number) => void;
  documents: Array<{
    id: string;
    type: DocumentType;
    status: DocumentStatus;
    fileName: string;
    version: number;
    metadata?: Record<string, any>;
    lastUpdated?: string;
  }>;
  isProcessing: boolean;
}

export const DocumentCollectionView: React.FC<DocumentCollectionViewProps> = ({
  onDocumentUpload,
  onImportSelect,
  onStatusChange,
  onVersionChange,
  documents,
  isProcessing
}) => {
  const [selectedImportSource, setSelectedImportSource] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  const handleImportSelect = async (source: string) => {
    setSelectedImportSource(source);
    await onImportSelect(source);
  };

  const handleResubmit = (documentId: string | null) => {
    if (documentId) {
      onVersionChange(documentId, documents.find(doc => doc.id === documentId)?.version || 1);
    }
  };

  return (
    <div className="document-collection-container">
      <section className="import-section">
        <h2>Import Documents</h2>
        <ImportOptions
          onSelect={handleImportSelect}
          selectedSource={selectedImportSource}
        />
      </section>

      <section className="upload-section">
        <h2>Upload Documents</h2>
        <DocumentUploader
          onUpload={onDocumentUpload}
          isProcessing={isProcessing}
        />
      </section>

      <section className="documents-section">
        <h2>Uploaded Documents</h2>
        <DocumentList documents={documents} />
        <div className="document-actions">
          <button 
            className="resubmit-button"
            onClick={() => handleResubmit(selectedDocument)}
          >
            Resubmit Document
          </button>
        </div>
        <StatusTracker 
          documents={documents}
          onStatusChange={onStatusChange}
        />
        <NotificationCenter
          documentUpdates={documents.filter(d => 
            d.status === DocumentStatus.NEEDS_REVIEW || d.status === DocumentStatus.REJECTED
          )}
          onNotificationClick={onNotificationClick}
        />
      </section>
    </div>
  );
};
