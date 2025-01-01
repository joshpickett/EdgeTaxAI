import React, { useState } from 'react';
import { DocumentStatus } from '../../types/documents';

interface DocumentViewerProps {
  document: {
    id: string;
    fileName: string;
    status: DocumentStatus;
    type: string;
    metadata?: Record<string, any>;
  };
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  document
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'metadata'>('preview');

  return (
    <div className="document-viewer">
      <div className="viewer-header">
        <h3>{document.fileName}</h3>
        <div className="viewer-tabs">
          <button
            className={`tab ${activeTab === 'preview' ? 'active' : ''}`}
            onClick={() => setActiveTab('preview')}
          >
            Preview
          </button>
          <button
            className={`tab ${activeTab === 'metadata' ? 'active' : ''}`}
            onClick={() => setActiveTab('metadata')}
          >
            Metadata
          </button>
        </div>
      </div>

      <div className="viewer-content">
        {activeTab === 'preview' ? (
          <div className="document-preview">
            {/* Document preview implementation */}
            <img 
              src={`/api/documents/${document.id}/preview`} 
              alt={document.fileName}
            />
          </div>
        ) : (
          <div className="document-metadata">
            {document.metadata ? (
              <div className="metadata-list">
                {Object.entries(document.metadata).map(([key, value]) => (
                  <div key={key} className="metadata-item">
                    <span className="metadata-key">{key}:</span>
                    <span className="metadata-value">
                      {JSON.stringify(value)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-metadata">
                No metadata available for this document
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
