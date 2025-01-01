interface NotificationCenterProps {
  documentUpdates: Array<{
    id: string;
    fileName: string;
    status: DocumentStatus;
    rejectionReason?: string;
    timestamp: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  onNotificationClick?: (id: string) => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  documentUpdates,
  onNotificationClick
}) => {
  return (
    <div className="notification-center">
      {documentUpdates.map(doc => (
        <div 
          key={doc.id} 
          className={`notification-item ${doc.priority}`}
          onClick={() => onNotificationClick?.(doc.id)}
        >
          <div className="notification-icon">
            {doc.status === DocumentStatus.NEEDS_REVIEW ? '⏳' : '❌'}
          </div>
          <div className="notification-content">
            <div className="notification-header">
              <h4>{doc.fileName}</h4>
              <span className="timestamp">{doc.timestamp}</span>
            </div>
            <p className="status-message">
              {doc.status === DocumentStatus.NEEDS_REVIEW ? 
                'Document is under review' : 
                `Document was rejected: ${doc.rejectionReason}`
              }
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};
