import React, { useState } from 'react';
import { VerificationResult } from '../../../../types/ocr';
import { formFieldStyles } from '../styles/FormFieldStyles';
import { formSectionStyles } from '../styles/FormSectionStyles';

interface FieldVerificationProps {
  field: string;
  originalValue: string;
  verificationResult: VerificationResult;
  onVerify: (field: string, value: string) => void;
  onSkip: (field: string) => void;
}

export const FieldVerification: React.FC<FieldVerificationProps> = ({
  field,
  originalValue,
  verificationResult,
  onVerify,
  onSkip
}) => {
  const [value, setValue] = useState(originalValue);
  const [isEditing, setIsEditing] = useState(false);

  const handleVerify = () => {
    onVerify(field, value);
    setIsEditing(false);
  };

  return (
    <div style={formSectionStyles.container}>
      <div style={formFieldStyles.group}>
        <h4>{field}</h4>
        
        <div style={formFieldStyles.row}>
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Original Value</label>
            <input
              type="text"
              value={originalValue}
              disabled
              style={{
                ...formFieldStyles.input,
                backgroundColor: '#f5f5f5'
              }}
            />
          </div>
          
          <div style={formFieldStyles.column}>
            <label style={formFieldStyles.label}>Confidence</label>
            <div style={{
              ...formFieldStyles.input,
              backgroundColor: '#f5f5f5',
              color: verificationResult.confidence >= 0.8 ? 'green' : 'orange'
            }}>
              {(verificationResult.confidence * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {isEditing ? (
          <div style={formFieldStyles.row}>
            <div style={formFieldStyles.column}>
              <label style={formFieldStyles.label}>Corrected Value</label>
              <input
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                style={formFieldStyles.input}
              />
            </div>
            <div style={formFieldStyles.buttonGroup}>
              <button
                onClick={handleVerify}
                style={formFieldStyles.button.primary}
              >
                Verify
              </button>
              <button
                onClick={() => setIsEditing(false)}
                style={formFieldStyles.button.secondary}
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div style={formFieldStyles.buttonGroup}>
            <button
              onClick={() => setIsEditing(true)}
              style={formFieldStyles.button.primary}
            >
              Edit
            </button>
            <button
              onClick={() => onSkip(field)}
              style={formFieldStyles.button.secondary}
            >
              Skip
            </button>
          </div>
        )}

        {verificationResult.suggestions?.length > 0 && (
          <div style={formFieldStyles.suggestions}>
            <label style={formFieldStyles.label}>Suggestions:</label>
            {verificationResult.suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => setValue(suggestion)}
                style={formFieldStyles.button.suggestion}
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
