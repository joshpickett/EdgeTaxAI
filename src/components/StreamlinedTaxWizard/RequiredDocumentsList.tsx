import React from 'react';
import { DocumentStatus } from '../../types/documents';
import { StatusBadge } from '../StatusBadge';

interface RequiredDocumentsListProps {
  documents: Array<{
    id: string;
    name: string;
    description: string;
    required: boolean;
    status: DocumentStatus;
    category: string;
    priority: 'high' | 'medium' | 'low';
    conditions?: Array<string>;
    metadata?: {
      stateSpecific?: boolean;
      state?: string;
      thresholds?: {
        amount?: number;
        currency?: string;
      };
      requiresAppraisal?: boolean;
    };
    rejectionReason?: string;
    version?: number;
  }>;
  onResubmit?: (documentId: string) => void;
}

export const RequiredDocumentsList: React.FC<RequiredDocumentsListProps> = ({
  documents,
  onResubmit
}) => {
  return (
    <div className="required-documents-list">
      <h3>Required Documents</h3>
      <div className="documents-grid">
        {documents.map(doc => (
          <div 
            key={doc.id} 
            className={`document-item ${doc.required ? 'required' : 'optional'}`}
          >
            <div className="document-header">
              <StatusBadge status={doc.status} />
              <span className={`priority-badge ${doc.priority}`}>
                {doc.priority}
              </span>
              <span className="category-badge">
                {doc.category}
              </span>
              {doc.conditions && doc.conditions.length > 0 && (
                <div className="conditions-list">
                  {doc.conditions.map(condition => (
                    <span key={condition} className="condition-tag">
                      {condition}
                      {doc.metadata?.thresholds?.amount && 
                        ` (>${doc.metadata.thresholds.amount} 
                          ${doc.metadata.thresholds.currency || 'USD'})`
                      }
                    </span>
                  ))}
                </div>
              )}
              {doc.version > 1 && (
                <span className="version-badge">
                  Version {doc.version}
                </span>
              )}
              {doc.required && <span className="required-badge">Required</span>}
            </div>
            <div className="document-info">
              <h4>{doc.name}</h4>
              <p>{doc.description}</p>
              {doc.status === DocumentStatus.REJECTED && (
                <div className="rejection-info">
                  <p className="rejection-reason">{doc.rejectionReason}</p>
                  <button 
                    onClick={() => onResubmit?.(doc.id)}
                    className="resubmit-button"
                  >
                    Resubmit Document</button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
