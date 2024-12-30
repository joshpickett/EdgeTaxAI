import React from 'react';
import { VerificationResult } from '../types/ocr';

interface VerificationResultsProps {
  results: VerificationResult[];
  onManualVerification?: (field: string, value: string) => void;
}

export const VerificationResults: React.FC<VerificationResultsProps> = ({
  results,
  onManualVerification
}) => {
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'green';
    if (confidence >= 0.6) return 'orange';
    return 'red';
  };

  return (
    <div className="verification-results">
      <h3>Verification Results</h3>
      {results.map((result, index) => (
        <div 
          key={index} 
          className="verification-item"
          style={{ 
            padding: '10px',
            margin: '5px 0',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        >
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>Field: {result.field}</span>
            <span style={{ 
              color: getConfidenceColor(result.confidence)
            }}>
              Confidence: {(result.confidence * 100).toFixed(1)}%
            </span>
          </div>
          
          {result.needsManualReview && (
            <div style={{ marginTop: '10px' }}>
              <span style={{ color: 'orange' }}>Needs Manual Review</span>
              {onManualVerification && (
                <button
                  onClick={() => onManualVerification(result.field, result.value)}
                  style={{
                    marginLeft: '10px',
                    padding: '5px 10px',
                    borderRadius: '4px',
                    border: '1px solid #ccc'
                  }}
                >
                  Verify Manually
                </button>
              )}
            </div>
          )}

          {result.suggestions?.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <strong>Suggestions:</strong>
              <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                {result.suggestions.map((suggestion, idx) => (
                  <li key={idx}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}

          {result.message && (
            <div style={{ 
              marginTop: '5px',
              color: '#666'
            }}>
              {result.message}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
