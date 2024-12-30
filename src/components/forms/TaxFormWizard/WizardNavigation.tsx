import React from 'react';
import { wizardStyles } from './styles/WizardStyles';

interface WizardNavigationProps {
  currentStep: number;
  totalSteps: number;
  canProceed: boolean;
  onNext: () => void;
  onPrevious: () => void;
  onSave: () => void;
}

export const WizardNavigation: React.FC<WizardNavigationProps> = ({
  currentStep,
  totalSteps,
  canProceed,
  onNext,
  onPrevious,
  onSave
}) => {
  return (
    <div style={wizardStyles.navigation}>
      <button
        style={{ ...wizardStyles.button.base, ...wizardStyles.button.secondary }}
        onClick={onPrevious}
        disabled={currentStep === 0}
      >
        Previous
      </button>

      <button
        style={{ ...wizardStyles.button.base, ...wizardStyles.button.secondary }}
        onClick={onSave}
      >
        Save Progress
      </button>

      <button
        style={{ ...wizardStyles.button.base, ...wizardStyles.button.primary }}
        onClick={onNext}
        disabled={!canProceed}
      >
        {currentStep === totalSteps - 1 ? 'Submit' : 'Next'}
      </button>
    </div>
  );
};
