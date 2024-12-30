import React, { useState, useEffect } from 'react';
import { AuditEntry } from '../types/audit';
import { formatDate } from '../utils/formatting';

interface AuditTrailProps {
  documentId: string;
  entries: AuditEntry[];
  onLoadMore?: () => void;
  hasMore?: boolean;
}

export const AuditTrail: React.FC<AuditTrailProps> = ({
  documentId,
  entries,
  onLoadMore,
  hasMore = false
}) => {
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set());

  const toggleEntry = (entryId: string) => {
    const newExpanded = new Set(expandedEntries);
    if (newExpanded.has(entryId)) {
      newExpanded.delete(entryId);
    } else {
      newExpanded.add(entryId);
    }
    setExpandedEntries(newExpanded);
  };

  const renderAuditEntry = (entry: AuditEntry) => {
    const isExpanded = expandedEntries.has(entry.id);

    return (
      <div 
        key={entry.id}
        className="audit-entry"
        style={{
          padding: '12px',
          borderBottom: '1px solid #eee',
          cursor: 'pointer'
        }}
        onClick={() => toggleEntry(entry.id)}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontWeight: 'bold' }}>{entry.action}</span>
          <span style={{ color: '#666' }}>{formatDate(entry.timestamp)}</span>
        </div>
        
        <div style={{ color: '#666', fontSize: '0.9em' }}>
          {entry.user}
        </div>

        {isExpanded && (
          <div style={{ marginTop: '8px', fontSize: '0.9em' }}>
            <div>IP Address: {entry.ipAddress}</div>
            <div>User Agent: {entry.userAgent}</div>
            {entry.metadata && (
              <pre style={{ 
                marginTop: '8px',
                padding: '8px',
                backgroundColor: '#f5f5f5',
                borderRadius: '4px',
                overflow: 'auto'
              }}>
                {JSON.stringify(entry.metadata, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="audit-trail">
      <h3>Audit Trail</h3>
      <div className="audit-entries">
        {entries.map(renderAuditEntry)}
      </div>
      
      {hasMore && (
        <button
          onClick={onLoadMore}
          style={{
            margin: '16px 0',
            padding: '8px 16px',
            backgroundColor: '#f0f0f0',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Load More
        </button>
      )}
    </div>
  );
};
