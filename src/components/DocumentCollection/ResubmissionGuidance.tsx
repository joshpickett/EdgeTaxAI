import React from 'react';

interface ResubmissionGuidanceProps {
  documentType: string;
  rejectionReason?: string;
}

export const ResubmissionGuidance: React.FC<ResubmissionGuidanceProps> = ({
  documentType,
  rejectionReason
}) => {
  const getGuidanceSteps = () => {
    const commonSteps = [
      'Ensure the document is clearly legible',
      'Check that all required information is visible',
      'Make sure the file is in an accepted format (PDF, JPG, PNG)',
      'Verify the document is not password protected'
    ];

    const specificSteps = getDocumentTypeSpecificSteps(documentType);
    return [...commonSteps, ...specificSteps];
  };

  const getDocumentTypeSpecificSteps = (type: string): string[] => {
    switch (type) {
      case 'W2':
        return [
          'Include all copies of the W-2 form',
          'Ensure employer EIN is visible',
          'Verify all income boxes are clearly visible'
        ];
      case 'BANK_STATEMENT':
        return [
          'Include all pages of the statement',
          'Ensure account numbers are visible',
          'Include the full statement period'
        ];
      default:
        return [];
    }
  };

  return (
    <div className="resubmission-guidance">
      <h3>Submission Guidelines</h3>
      
      <div className="guidance-content">
        <div className="steps-list">
          <h4>Before You Resubmit</h4>
          <ol>
            {getGuidanceSteps().map((step, index) => (
              <li key={index} className="step-item">
                {step}
              </li>
            ))}
          </ol>
        </div>

        {rejectionReason && (
          <div className="specific-guidance">
            <h4>Addressing Previous Issues</h4>
            <p>Based on the rejection reason, please ensure:</p>
            <ul>
              {rejectionReason.split(';').map((reason, index) => (
                <li key={index} className="guidance-item">
                  How to fix: {reason.trim()}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
