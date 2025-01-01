import React from 'react';

interface RejectionHandlerProps {
  rejectionReason?: string;
  rejectionFeedback?: string;
}

export const RejectionHandler: React.FC<RejectionHandlerProps> = ({
  rejectionReason,
  rejectionFeedback
}) => {
  return (
    <div className="rejection-handler">
      <h3>Rejection Details</h3>
      
      <div className="rejection-details">
        {rejectionReason && (
          <div className="rejection-reason">
            <h4>Reason for Rejection</h4>
            <p>{rejectionReason}</p>
          </div>
        )}
        
        {rejectionFeedback && (
          <div className="rejection-feedback">
            <h4>Reviewer Feedback</h4>
            <p>{rejectionFeedback}</p>
          </div>
        )}
      </div>

      <div className="correction-checklist">
        <h4>Required Corrections</h4>
        <ul>
          {rejectionReason?.split(';').map((reason, index) => (
            <li key={index} className="correction-item">
              <input type="checkbox" id={`correction-${index}`} />
              <label htmlFor={`correction-${index}`}>{reason.trim()}</label>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
