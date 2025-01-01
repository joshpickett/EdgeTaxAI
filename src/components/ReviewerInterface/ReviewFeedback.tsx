import React from 'react';
import { DocumentStatus } from '../../types/documents';

interface ReviewFeedbackProps {
  documentId: string;
  feedback: string;
  onFeedbackChange: (feedback: string) => void;
  onSubmit: (status: DocumentStatus, feedback: string) => void;
}

export const ReviewFeedback: React.FC<ReviewFeedbackProps> = ({
  documentId,
  feedback,
  onFeedbackChange,
  onSubmit
}) => {
  const handleSubmit = (status: DocumentStatus) => {
    if (status === DocumentStatus.REJECTED && !feedback) {
      alert('Please provide feedback for rejected documents');
      return;
    }
    onSubmit(status, feedback);
  };

  return (
    <div className="review-feedback">
      <h3>Review Feedback</h3>
      <div className="feedback-form">
        <textarea
          value={feedback}
          onChange={(e) => onFeedbackChange(e.target.value)}
          placeholder="Enter feedback or notes about the document..."
          rows={4}
        />
        <div className="action-buttons">
          <button
            className="reject-button"
            onClick={() => handleSubmit(DocumentStatus.REJECTED)}
          >
            Reject
          </button>
          <button
            className="approve-button"
            onClick={() => handleSubmit(DocumentStatus.VERIFIED)}
          >
            Approve
          </button>
        </div>
      </div>
    </div>
  );
};
