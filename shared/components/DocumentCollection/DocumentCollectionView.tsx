import React, { useState } from 'react';
import { DocumentType, DocumentStatus } from '../../types/documents';
import { DocumentUploader } from './DocumentUploader';
import { DocumentList } from './DocumentList';
import { ImportOptions } from './ImportOptions';

interface DocumentCollectionViewProps {
  onDocumentUpload: (file: File, type: DocumentType) => Promise<void>;
  onImportSelect: (source: string) => Promise<void>;
  documents: Array<{
    id: string;
    type: DocumentType;
    status: DocumentStatus;
    fileName: string;
  }>;
  isProcessing: boolean;
}

export const DocumentCollectionView: React.FC<DocumentCollectionViewProps> = ({
  onDocumentUpload,
  onImportSelect,
  documents,
  isProcessing
}) => {
  const [selectedImportSource, setSelectedImportSource] = useState<string | null>(null);

  const handleImportSelect = async (source: string) => {
    setSelectedImportSource(source);
    await onImportSelect(source);
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
      </section>
    </div>
  );
};
