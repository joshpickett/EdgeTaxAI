import React, { useState } from 'react';
import { DocumentStatus } from '../../types/documents';
import { VersionComparison } from './VersionComparison';
import { RejectionHandler } from './RejectionHandler';
import { ResubmissionGuidance } from './ResubmissionGuidance';

interface ResubmissionPortalProps {
  document: {
    id: string;
    fileName: string;
    status: DocumentStatus;
    version: number;
    rejectionReason?: string;
    rejectionFeedback?: string;
    previousVersions?: Array<{
      id: string;
      version: number;
      timestamp: string;
      status: DocumentStatus;
    }>;
  };
  onResubmit: (documentId: string, file: File) => Promise<void>;
}

export const ResubmissionPortal: React.FC<ResubmissionPortalProps> = ({
  document,
  onResubmit
}) => {
  const [selectedVersion, setSelectedVersion] = useState<number>(document.version);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleResubmit = async (file: File) => {
    try {
      setIsSubmitting(true);
      await onResubmit(document.id, file);
    } catch (error) {
      console.error('Error resubmitting document:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="resubmission-portal">
      <header className="portal-header">
        <h2>Document Resubmission</h2>
        <div className="document-info">
          <span className="filename">{document.fileName}</span>
          <span className="version">Version {document.version}</span>
        </div>
      </header>

      <div className="portal-content">
        <RejectionHandler
          rejectionReason={document.rejectionReason}
          rejectionFeedback={document.rejectionFeedback}
        />

        {document.previousVersions && document.previousVersions.length > 0 && (
          <VersionComparison
            currentVersion={document.version}
            previousVersions={document.previousVersions}
            selectedVersion={selectedVersion}
            onVersionSelect={setSelectedVersion}
          />
        )}

        <ResubmissionGuidance
          documentType={document.type}
          rejectionReason={document.rejectionReason}
        />

        <div className="resubmission-actions">
          <input
            type="file"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleResubmit(file);
            }}
            disabled={isSubmitting}
          />
          {isSubmitting && <span>Submitting...</span>}
        </div>
      </div>
    </div>
  );
};
