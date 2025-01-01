import React from 'react';
import { DocumentStatus } from '../../types/documents';
import { CircularProgress } from '../CircularProgress';

interface StatusTrackerProps {
  documents: Array<{
    id: string;
    type: DocumentType;
    status: DocumentStatus;
    fileName: string;
    lastUpdated?: string;
    priority: 'high' | 'medium' | 'low';
    processingTime?: number;
  }>;
  onStatusChange: (documentId: string, status: DocumentStatus) => void;
}

export const StatusTracker: React.FC<StatusTrackerProps> = ({
  documents,
  onStatusChange
}) => {
  const calculateProgress = () => {
    const total = documents.length;
    const completed = documents.filter(
      d => d.status === DocumentStatus.VERIFIED
    ).length;
    return (completed / total) * 100;
  };

  const getStatusCounts = () => ({
    verified: documents.filter(d => d.status === DocumentStatus.VERIFIED).length,
    pending: documents.filter(d => d.status === DocumentStatus.NEEDS_REVIEW).length,
    rejected: documents.filter(d => d.status === DocumentStatus.REJECTED).length
  });

  const calculateAverageProcessingTime = () => {
    const totalProcessingTime = documents.reduce((sum, doc) => sum + (doc.processingTime || 0), 0);
    return totalProcessingTime / documents.length || 0;
  };

  const countPriorityItems = () => {
    return documents.filter(doc => doc.priority === 'high').length;
  };

  const counts = getStatusCounts();

  return (
    <div className="status-tracker">
      <div className="status-overview">
        <CircularProgress 
          percentage={calculateProgress()} 
          size={80} 
          strokeWidth={8}
          color={getProgressColor(calculateProgress())}
        />
        <div className="status-metrics">
          <div className="metric">
            <span className="label">Avg. Processing Time</span>
            <span className="value">{calculateAverageProcessingTime()}s</span>
          </div>
          <div className="metric">
            <span className="label">Priority Items</span>
            <span className="value">{countPriorityItems()}</span>
          </div>
        </div>
        <div className="status-text">
          <h3>Overall Progress</h3>
          <p>{calculateProgress()}% Complete</p>
        </div>
      </div>

      <div className="status-counts">
        <div className="status-item">
          <span className="count verified">{counts.verified}</span>
          <span className="label">Verified</span>
        </div>
        <div className="status-item">
          <span className="count pending">{counts.pending}</span>
          <span className="label">Pending Review</span>
        </div>
        <div className="status-item">
          <span className="count rejected">{counts.rejected}</span>
          <span className="label">Rejected</span>
        </div>
      </div>

      <div className="status-timeline">
        {documents.map(doc => (
          <div key={doc.id} className="timeline-item">
            <span className="filename">{doc.fileName}</span>
            <span className={`status ${doc.status.toLowerCase()}`}>
              {doc.status}
            </span>
            {doc.lastUpdated && (
              <span className="timestamp">{doc.lastUpdated}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
