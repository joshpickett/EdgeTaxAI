import React from 'react';
import { formFieldStyles } from '../styles/FormFieldStyles';

interface ValidationFeedbackProps {
  errors: Array<{
    field: string;
    message: string;
    code: string;
  }>;
  warnings: Array<{
    field: string;
    message: string;
    code: string;
  }>;
  suggestions: Array<{
    field: string;
    message: string;
    confidence_score?: number;
    verification_status?: string;
    potentialSavings?: number;
  }>;
}

export const ValidationFeedback: React.FC<ValidationFeedbackProps> = ({
  errors,
  warnings,
  suggestions
}) => {
  return (
    <div className="validation-feedback">
      {errors.length > 0 && (
        <div style={formFieldStyles.errorContainer}>
          <h4>Required Corrections</h4>
          {errors.map((error, index) => (
            <div key={index} style={formFieldStyles.error}>
              <span className="field">{error.field}:</span>
              <span className="message">{error.message}</span>
            </div>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div style={formFieldStyles.warningContainer}>
          <h4>Warnings</h4>
          {warnings.map((warning, index) => (
            <div key={index} style={formFieldStyles.warning}>
              <span className="field">{warning.field}:</span>
              <span className="message">{warning.message}</span>
            </div>
          ))}
        </div>
      )}

      {suggestions.length > 0 && (
        <div style={formFieldStyles.suggestionContainer}>
          <h4>Optimization Suggestions</h4>
          {suggestions.map((suggestion, index) => (
            <div key={index} style={formFieldStyles.suggestion}>
              <div className="suggestion-header">
                <span className="message">{suggestion.message}</span>
                {suggestion.confidence_score && (
                  <span className="confidence">
                    Confidence: {(suggestion.confidence_score * 100).toFixed(1)}%
                  </span>
                )}
              </div>
              {suggestion.verification_status && (
                <div className="verification-status">
                  Status: {suggestion.verification_status}
                </div>
              )}
              {suggestion.potentialSavings && (
                <span className="savings">
                  Potential Savings: ${suggestion.potentialSavings}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
