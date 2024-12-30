import React from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { PersonalInfoStep } from './steps/PersonalInfoStep';
import { IncomeStep } from './steps/IncomeStep';
import { AdjustmentsStep } from './steps/AdjustmentsStep';
import { CreditsStep } from './steps/CreditsStep';
import { ReviewStep } from './steps/ReviewStep';

interface WizardStepProps {
  stepData: {
    id: string;
    title: string;
    component: string;
  };
  formData: Partial<Form1040Data>;
  onUpdate: (data: Partial<Form1040Data>) => void;
}

const stepComponents = {
  PersonalInfoStep,
  IncomeStep,
  AdjustmentsStep,
  CreditsStep,
  ReviewStep
};

export const WizardStep: React.FC<WizardStepProps> = ({
  stepData,
  formData,
  onUpdate
}) => {
  const StepComponent = stepComponents[stepData.component];

  return (
    <div className="wizard-step">
      <h2>{stepData.title}</h2>
      <StepComponent
        formData={formData}
        onUpdate={onUpdate}
      />
    </div>
  );
};
