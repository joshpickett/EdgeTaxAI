import React, { useState, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { MobileFormScreen } from '../components/mobile/MobileFormScreen';
import { MobileFormProgress } from '../components/mobile/MobileFormProgress';
import { MobileFormNavigation } from '../components/mobile/MobileFormNavigation';
import { taxFormService } from '../../shared/services/taxFormService';
import { TaxFormTemplate } from '../../shared/types/tax-forms';
import { LoadingOverlay } from '../components/LoadingOverlay';
import { MobileFormField } from '../components/mobile/MobileFormField';

export const FormWizardScreen: React.FC = ({ route, navigation }) => {
  const { formType } = route.params;
  const [currentStep, setCurrentStep] = useState(0);
  const [template, setTemplate] = useState<TaxFormTemplate | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTemplate();
  }, [formType]);

  const loadTemplate = async () => {
    try {
      const formTemplate = await taxFormService.loadTemplate(formType);
      setTemplate(formTemplate);
    } catch (error) {
      console.error('Error loading template:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (currentStep < (template?.sections.length || 0) - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      navigation.navigate('Review');
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      navigation.goBack();
    }
  };

  if (loading || !template) {
    return <LoadingOverlay />;
  }

  return (
    <MobileFormScreen>
      <MobileFormProgress
        steps={template.sections.map(s => s.title)}
        currentStep={currentStep}
      />
      
      <View style={styles.formContent}>
        {/* Current section form fields */}
        {template.sections[currentStep].fields.map(field => (
          <MobileFormField
            key={field.id}
            field={field}
            onChange={() => {}}
          />
        ))}
      </View>

      <MobileFormNavigation
        onNext={handleNext}
        onBack={handleBack}
        canGoNext={currentStep < template.sections.length - 1}
        canGoBack={currentStep > 0}
      />
    </MobileFormScreen>
  );
};

const styles = StyleSheet.create({
  formContent: {
    flex: 1,
    padding: 16
  }
});
