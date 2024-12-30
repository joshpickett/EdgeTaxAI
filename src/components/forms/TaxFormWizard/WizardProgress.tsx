import React from 'react';
import { wizardStyles } from './styles/WizardStyles';

interface WizardProgressProps {
  steps: Array<{
    id: string;
    title: string;
  }>;
  currentStep: number;
  completedSteps: string[];
}

export const WizardProgress: React.FC<WizardProgressProps> = ({
  steps,
  currentStep,
  completedSteps
}) => {
  return (
    <div style={wizardStyles.progressBar}>
      {steps.map((step, index) => (
        <div
          key={step.id}
          style={wizardStyles.step}
        >
          <div style={wizardStyles.stepNumber}>{index + 1}</div>
          <div style={wizardStyles.stepTitle}>{step.title}</div>
          {index < steps.length - 1 && 
            <div style={wizardStyles.stepConnector} />
          }
        </div>
      ))}
    </div>
  );
};
