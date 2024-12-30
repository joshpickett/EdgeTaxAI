import React, { useState, useEffect } from 'react';
import { Form1040Data } from 'shared/types/form1040';
import { FormIntegrationService } from 'api/services/integration/form_integration_service';
import { FormValidationService } from 'api/services/form/form_validation_service';
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
  onRestore: (data: Partial<Form1040Data>) => void;
}

const formIntegrationService = new FormIntegrationService();
const formValidationService = new FormValidationService();

export const TaxFormWizard: React.FC<TaxFormWizardProps> = ({
  initialData,
  onComplete,
  onSave,
  onRestore
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [lastSaved, setLastSaved] = useState<Date>(new Date());
  const [autoSaveInterval, setAutoSaveInterval] = useState<NodeJS.Timeout | null>(null);

  const {
    formData,
    updateFormData,
    isStepValid,
    canProceed
  } = useFormWizard(initialData);

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isInitializing, setIsInitializing] = useState(true);
  const [wizardData, setWizardData] = useState(null);

  const steps = Object.entries(TAX_WIZARD_CONFIG.steps).map(([id, config]) => ({
    id,
    title: config.title,
    component: `${id.charAt(0).toUpperCase()}${id.slice(1)}Step`,
    required: config.required,
    validation: config.validation
  }));

  useEffect(() => {
    const initializeWizard = async () => {
      try {
        // Restore previous progress if available
        const savedProgress = await formIntegrationService.restore_progress(
          initialData?.userId,
          'Form1040'
        );
        
        if (savedProgress) {
          updateFormData(savedProgress);
          setCurrentStep(savedProgress.lastCompletedStep || 0);
        }

        const initData = await formIntegrationService.initialize_form_wizard(
          initialData?.userId,
          'Form1040',
          new Date().getFullYear(),
          initialData
        );
        
        // Setup autosave
        const interval = setInterval(() => {
          if (formProgressService.should_autosave(lastSaved)) {
            handleAutoSave();
          }
        }, 60000); // Check every minute
        
        setAutoSaveInterval(interval);
        
        setWizardData(initData);
      } catch (error) {
        console.error('Error initializing wizard:', error);
      }
    };
    initializeWizard();
    
    return () => {
      if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
      }
    };
  }, []);

  const handleNext = async () => {
    try {
      const currentStepConfig = steps[currentStep];
      
      // Save progress before proceeding
      await handleAutoSave();
      
      const validation = await formValidationService.validate_section(
        'Form1040',
        currentStepConfig.id,
        formData
      );

      // Update completion tracking
      const updatedFormData = {
        ...formData,
        completedSteps: [
          ...(formData.completedSteps || []),
          currentStepConfig.id
        ]
      };
      updateFormData(updatedFormData);

      if (!validation.isValid) {
        setValidationErrors(validation.errors);
        return;
      }

      if (currentStep < steps.length - 1) {
        setCurrentStep(currentStep + 1);
      } else {
        await handleFormSubmission();
      }
    } catch (error) {
      console.error('Error proceeding to next step:', error);
    }
  };

  const handleAutoSave = async () => {
    try {
      await formIntegrationService.save_progress(
        formData.userId,
        'Form1040',
        {
          ...formData,
          lastCompletedStep: currentStep
        }
      );
      setLastSaved(new Date());
    } catch (error) {
      console.error('Error auto-saving progress:', error);
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
