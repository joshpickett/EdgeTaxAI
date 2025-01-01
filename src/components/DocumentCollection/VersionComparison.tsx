import React from 'react';
import { DocumentStatus } from '../../types/documents';

interface VersionComparisonProps {
  currentVersion: number;
  previousVersions: Array<{
    id: string;
    version: number;
    timestamp: string;
    status: DocumentStatus;
  }>;
  selectedVersion: number;
  onVersionSelect: (version: number) => void;
}

export const VersionComparison: React.FC<VersionComparisonProps> = ({
  currentVersion,
  previousVersions,
  selectedVersion,
  onVersionSelect
}) => {
  return (
    <div className="version-comparison">
      <h3>Version History</h3>
      
      <div className="version-timeline">
        {previousVersions.map((version) => (
          <div
            key={version.id}
            className={`version-item ${selectedVersion === version.version ? 'selected' : ''}`}
            onClick={() => onVersionSelect(version.version)}
          >
            <div className="version-header">
              <span className="version-number">Version {version.version}</span>
              <span className="version-date">
                {new Date(version.timestamp).toLocaleDateString()}
              </span>
            </div>
            <div className="version-status">
              <span className={`status-badge ${version.status.toLowerCase()}`}>
                {version.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="comparison-view">
        <div className="previous-version">
          <h4>Version {selectedVersion}</h4>
          <div className="document-preview">
            {/* Previous version preview */}
          </div>
        </div>
        <div className="current-version">
          <h4>Current Version {currentVersion}</h4>
          <div className="document-preview">
            {/* Current version preview */}
          </div>
        </div>
      </div>
    </div>
  );
};
