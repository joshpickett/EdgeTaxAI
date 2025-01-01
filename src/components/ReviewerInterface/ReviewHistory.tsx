import React from 'react';
import { DocumentStatus } from '../../types/documents';

interface ReviewHistoryItem {
  id: string;
  timestamp: string;
  reviewer: string;
  status: DocumentStatus;
  feedback?: string;
  version: number;
}

interface ReviewHistoryProps {
  history: ReviewHistoryItem[];
  documentId: string;
}

export const ReviewHistory: React.FC<ReviewHistoryProps> = ({
  history,
  documentId
}) => {
  return (
    <div className="review-history">
      <h3>Review History</h3>
      <div className="history-timeline">
        {history.map((item, index) => (
          <div key={item.id} className="history-item">
            <div className="history-marker">
              <div className="marker-line" />
              <div className={`marker-dot ${item.status.toLowerCase()}`} />
            </div>
            <div className="history-content">
              <div className="history-header">
                <span className="timestamp">
                  {new Date(item.timestamp).toLocaleString()}
                </span>
                <span className="version">Version {item.version}</span>
              </div>
              <div className="history-details">
                <span className="reviewer">{item.reviewer}</span>
                <span className={`status ${item.status.toLowerCase()}`}>
                  {item.status}
                </span>
              </div>
              {item.feedback && (
                <div className="feedback">{item.feedback}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
