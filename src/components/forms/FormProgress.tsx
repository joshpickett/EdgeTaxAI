import React from 'react';

interface FormProgressProps {
  currentStep: number;
  totalSteps: number;
}

export const FormProgress: React.FC<FormProgressProps> = ({
  currentStep,
  totalSteps
}) => {
  const progressPercentage = (currentStep / totalSteps) * 100;

  return (
    <div style={{ width: '100%', backgroundColor: '#e0e0e0', borderRadius: '5px' }}>
      <div
        style={{
          width: `${progressPercentage}%`,
          backgroundColor: '#3b5998',
          height: '10px',
          borderRadius: '5px'
        }}
      />
      <div style={{ textAlign: 'center', marginTop: '5px' }}>
        Step {currentStep} of {totalSteps}
      </div>
    </div>
  );
};
