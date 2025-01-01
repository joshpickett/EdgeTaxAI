import React, { useState } from 'react';
import { DocumentStatus } from '../../types/documents';
import { ReviewQueue } from './ReviewQueue';
import { DocumentViewer } from './DocumentViewer';
import { ReviewFeedback } from './ReviewFeedback';

interface ReviewerWorkspaceProps {
  documents: Array<{
    id: string;
    fileName: string;
    status: DocumentStatus;
    type: string;
    submittedAt: string;
    priority: 'high' | 'medium' | 'low';
    version: number;
    reviewHistory?: Array<ReviewHistoryItem>;
  }>;
  onStatusChange: (documentId: string, status: DocumentStatus, feedback?: string) => void;
}

export const ReviewerWorkspace: React.FC<ReviewerWorkspaceProps> = ({
  documents,
  onStatusChange
}) => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string>('');

  const handleDocumentSelect = (documentId: string) => {
    setSelectedDocument(documentId);
    setFeedback('');
  };

  const handleFeedbackSubmit = (status: DocumentStatus, feedbackText: string) => {
    if (selectedDocument) {
      onStatusChange(selectedDocument, status, feedbackText);
      setFeedback('');
      setSelectedDocument(null);
    }
  };

  const selectedDocumentData = documents.find(d => d.id === selectedDocument);

  return (
    <div className="reviewer-workspace">
      <div className="workspace-layout">
        <div className="queue-section">
          <ReviewQueue
            documents={documents}
            selectedDocument={selectedDocument}
            onDocumentSelect={handleDocumentSelect}
            sortOptions={{
              priority: true,
              submissionDate: true,
              documentType: true
            }}
            filterOptions={{
              status: true,
              priority: true,
              documentType: true
            }}
            batchReviewEnabled={true}
          />
        </div>
        
        <div className="review-section">
          {selectedDocumentData ? (
            <>
              <DocumentViewer
                document={selectedDocumentData}
              />
              <ReviewFeedback
                documentId={selectedDocumentData.id}
                onSubmit={handleFeedbackSubmit}
                feedback={feedback}
                onFeedbackChange={setFeedback}
              />
            </>
          ) : (
            <div className="no-selection">
              Select a document from the queue to begin review
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
