import React from 'react';
import { DocumentStatus } from '../types/documents';

interface StatusBadgeProps {
  status: DocumentStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getStatusColor = () => {
    switch (status) {
      case DocumentStatus.VERIFIED:
        return '#4CAF50';
      case DocumentStatus.NEEDS_REVIEW:
        return '#FFC107';
      case DocumentStatus.REJECTED:
        return '#F44336';
      default:
        return '#9E9E9E';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case DocumentStatus.VERIFIED:
        return 'Verified';
      case DocumentStatus.NEEDS_REVIEW:
        return 'Under Review';
      case DocumentStatus.REJECTED:
        return 'Rejected';
      default:
        return 'Pending';
    }
  };

  return (
    <div className="status-badge" style={{
      backgroundColor: getStatusColor(),
      color: '#fff',
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      fontWeight: 500
    }}>
      {getStatusText()}
    </div>
  );
};
