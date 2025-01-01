import React from 'react';
import { DocumentStatus } from '../../types/documents';

interface ReviewQueueProps {
  documents: Array<{
    id: string;
    fileName: string;
    status: DocumentStatus;
    type: string;
    submittedAt: string;
  }>;
  selectedDocument: string | null;
  onDocumentSelect: (documentId: string) => void;
}

export const ReviewQueue: React.FC<ReviewQueueProps> = ({
  documents,
  selectedDocument,
  onDocumentSelect
}) => {
  const pendingDocuments = documents.filter(
    document => document.status === DocumentStatus.NEEDS_REVIEW
  );

  return (
    <div className="review-queue">
      <h3>Review Queue</h3>
      <div className="queue-list">
        {pendingDocuments.map(document => (
          <div
            key={document.id}
            className={`queue-item ${selectedDocument === document.id ? 'selected' : ''}`}
            onClick={() => onDocumentSelect(document.id)}
          >
            <div className="document-info">
              <span className="filename">{document.fileName}</span>
              <span className="document-type">{document.type}</span>
            </div>
            <div className="submission-info">
              <span className="timestamp">
                Submitted: {new Date(document.submittedAt).toLocaleDateString()}
              </span>
            </div>
          </div>
        ))}
        {pendingDocuments.length === 0 && (
          <div className="empty-queue">
            No documents waiting for review
          </div>
        )}
      </div>
    </div>
  );
};
