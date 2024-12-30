import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Button } from 'react-native-paper';
import { MobileFormScreen } from '../components/mobile/MobileFormScreen';
import { COLORS } from '../../assets/config/colors';
import { SPACING } from '../../assets/config/spacing';
import { IRS_CONSTANTS } from '../../shared/constants/irs';

interface FormOption {
  id: string;
  title: string;
  description: string;
  formType: string;
}

const formOptions: FormOption[] = [
  {
    id: '1040',
    title: 'Form 1040',
    description: 'Standard U.S. Individual Income Tax Return',
    formType: IRS_CONSTANTS.FORM_TYPES.FORM_1040
  },
  {
    id: '1099-nec',
    title: 'Form 1099-NEC',
    description: 'Nonemployee Compensation',
    formType: IRS_CONSTANTS.FORM_TYPES.FORM_1099_NEC
  },
  {
    id: '1099-k',
    title: 'Form 1099-K',
    description: 'Payment Card and Third Party Network Transactions',
    formType: IRS_CONSTANTS.FORM_TYPES.FORM_1099_K
  }
];

export const FormSelectionScreen: React.FC = ({ navigation }) => {
  const handleFormSelect = (formType: string) => {
    navigation.navigate('FormWizard', { formType });
  };

  return (
    <MobileFormScreen>
      <Text style={styles.title}>Select Tax Form</Text>
      <Text style={styles.subtitle}>
        Choose the appropriate form based on your income type
      </Text>
      
      <ScrollView style={styles.formList}>
        {formOptions.map((form) => (
          <Card 
            key={form.id} 
            style={styles.formCard}
            onPress={() => handleFormSelect(form.formType)}
          >
            <Card.Content>
              <Text style={styles.formTitle}>{form.title}</Text>
              <Text style={styles.formDescription}>{form.description}</Text>
            </Card.Content>
            <Card.Actions>
              <Button 
                mode="contained" 
                onPress={() => handleFormSelect(form.formType)}
              >
                Select
              </Button>
            </Card.Actions>
          </Card>
        ))}
      </ScrollView>
    </MobileFormScreen>
  );
};

const styles = StyleSheet.create({
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: SPACING.sm,
    color: COLORS.text.primary
  },
  subtitle: {
    fontSize: 16,
    marginBottom: SPACING.lg,
    color: COLORS.text.secondary
  },
  formList: {
    flex: 1
  },
  formCard: {
    marginBottom: SPACING.md,
    elevation: 2
  },
  formTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: SPACING.xs
  },
  formDescription: {
    fontSize: 14,
    color: COLORS.text.secondary
  }
});
