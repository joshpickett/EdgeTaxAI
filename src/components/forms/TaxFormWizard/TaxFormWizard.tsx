import React, { useState, useEffect } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { TAX_WIZARD_CONFIG } from '../../../config/taxWizardConfig';
import { WizardStep } from './WizardStep';
import { WizardNavigation } from './WizardNavigation';
import { WizardProgress } from './WizardProgress';
import { useFormWizard } from '../../../hooks/useFormWizard';
import { wizardStyles } from './styles/WizardStyles';

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

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const steps = Object.entries(TAX_WIZARD_CONFIG.steps).map(([id, config]) => ({
    id,
    title: config.title,
    component: `${id.charAt(0).toUpperCase()}${id.slice(1)}Step`,
    required: config.required,
    validation: config.validation
  }));

  const handleNext = async () => {
    const currentStepConfig = steps[currentStep];
    const isValid = await validateStep(currentStepConfig);

    if (!isValid) {
      return;
    }

    if (currentStep < steps.length - 1 && isValid) {
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
