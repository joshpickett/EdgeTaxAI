import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Button } from 'react-native-paper';
import { MobileFormScreen } from '../../components/mobile/MobileFormScreen';
import { MobileFormField } from '../../components/mobile/MobileFormField';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { FilingStatus, BusinessType } from '../../../shared/types/tax';

export const TaxProfileScreen = ({ navigation }) => {
  const [profile, setProfile] = useState({
    filingStatus: '',
    businessType: '',
    estimatedIncome: '',
    hasEmployment: false
  });

  const handleSubmit = () => {
    // Save profile data
    navigation.navigate('OnboardingComplete');
  };

  return (
    <MobileFormScreen>
      <View style={styles.container}>
        <Text style={styles.title}>Tax Profile Setup</Text>
        <Text style={styles.subtitle}>
          Help us customize your tax experience
        </Text>

        <View style={styles.form}>
          <MobileFormField
            name="filingStatus"
            label="Filing Status"
            type="select"
            options={Object.values(FilingStatus).map(status => ({
              label: status.replace(/_/g, ' '),
              value: status
            }))}
            value={profile.filingStatus}
            onChange={(value) => setProfile(prev => ({ ...prev, filingStatus: value }))}
          />

          <MobileFormField
            name="businessType"
            label="Business Type"
            type="select"
            options={Object.values(BusinessType).map(type => ({
              label: type.replace(/_/g, ' '),
              value: type
            }))}
            value={profile.businessType}
            onChange={(value) => setProfile(prev => ({ ...prev, businessType: value }))}
          />

          <MobileFormField
            name="estimatedIncome"
            label="Estimated Annual Income"
            type="number"
            value={profile.estimatedIncome}
            onChange={(value) => setProfile(prev => ({ ...prev, estimatedIncome: value }))}
          />

          <MobileFormField
            name="hasEmployment"
            label="Do you also have W-2 employment?"
            type="checkbox"
            value={profile.hasEmployment}
            onChange={(value) => setProfile(prev => ({ ...prev, hasEmployment: value }))}
          />
        </View>

        <View style={styles.footer}>
          <Button
            mode="contained"
            onPress={handleSubmit}
            style={styles.button}
          >
            Complete Setup
          </Button>
        </View>
      </View>
    </MobileFormScreen>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: SPACING.lg
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: SPACING.sm
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.text.secondary,
    marginBottom: SPACING.xl
  },
  form: {
    flex: 1
  },
  footer: {
    marginTop: SPACING.xl
  },
  button: {
    paddingVertical: SPACING.sm
  }
});
