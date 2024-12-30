import React, { useState, useEffect } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { WizardStep } from './WizardStep';
import { WizardNavigation } from './WizardNavigation';
import { WizardProgress } from './WizardProgress';
import { useFormWizard } from '../../../hooks/useFormWizard';
import { wizardStyles } from './styles/WizardStyles';
import { InitialScreeningStep } from './steps/InitialScreeningStep';

interface TaxFormWizardProps {
  initialData?: Partial<Form1040Data>;
  onComplete: (data: Form1040Data) => void;
  onSave: (data: Partial<Form1040Data>) => void;
}

export const TaxFormWizard: React.FC<TaxFormWizardProps> = ({
  initialData,
  onComplete,
  onSave
}) => {
  const {
    currentStep,
    setCurrentStep,
    formData,
    updateFormData,
    isStepValid,
    canProceed
  } = useFormWizard(initialData);

  const steps = [
    {
      id: 'initial-screening',
      title: 'Basic Information',
      component: 'InitialScreeningStep'
    },
    {
      id: 'personal-info',
      title: 'Personal Information',
      component: 'PersonalInfoStep'
    },
    {
      id: 'income',
      title: 'Income',
      component: 'IncomeStep'
    },
    {
      id: 'adjustments',
      title: 'Adjustments',
      component: 'AdjustmentsStep'
    },
    {
      id: 'credits',
      title: 'Credits',
      component: 'CreditsStep'
    },
    {
      id: 'review',
      title: 'Review & Submit',
      component: 'ReviewStep'
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(formData as Form1040Data);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSave = () => {
    onSave(formData);
  };

  return (
    <div style={wizardStyles.container}>
      <WizardProgress 
        steps={steps} 
        currentStep={currentStep} 
        completedSteps={formData.completedSteps} 
      />
      
      <div style={wizardStyles.content}>
        <WizardStep
          stepData={steps[currentStep]}
          formData={formData}
          onUpdate={updateFormData}
        />
      </div>

      <WizardNavigation
        currentStep={currentStep}
        totalSteps={steps.length}
        canProceed={canProceed}
        onNext={handleNext}
        onPrevious={handlePrevious}
        onSave={handleSave}
      />
    </div>
  );
};
