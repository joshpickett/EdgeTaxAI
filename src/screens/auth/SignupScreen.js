import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { UnifiedAuthService } from 'shared/services/unifiedAuthService';
import { SharedValidator } from 'shared/utils/validators';
import CustomButton from '../../components/CustomButton';
import InputField from '../../components/InputField';
import { colors, spacing, typography } from '../../styles/tokens';

const authService = UnifiedAuthService.getInstance();

const SignupScreen = ({ navigation }) => {
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    otp: ''
  });
  const [errors, setErrors] = useState({});
  const [otpSent, setOtpSent] = useState(false);

  const handleSignup = async () => {
    try {
      const validationErrors = SharedValidator.validateAuth(formData);
      if (validationErrors.length > 0) {
        setErrors(validationErrors);
        return;
      }

      const result = await authService.signup({
        ...formData,
        deviceInfo: navigator.userAgent
      });

      if (result.success) {
        setOtpSent(true);
        Alert.alert('Success', 'Please check your email/phone for OTP');
      }
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  const handleVerifyOTP = async () => {
    try {
      const result = await authService.verifyOTP({
        identifier: formData.email || formData.phone,
        otp: formData.otp
      });

      if (result.success) {
        navigation.replace('Dashboard');
      }
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };

  return (
    <View style={styles.container}>
      <InputField
        label="Email"
        value={formData.email}
        onChangeText={(text) => setFormData({ ...formData, email: text })}
        error={errors.email}
        disabled={otpSent}
      />

      <InputField
        label="Phone"
        value={formData.phone}
        onChangeText={(text) => setFormData({ ...formData, phone: text })}
        error={errors.phone}
        disabled={otpSent}
      />

      {otpSent && (
        <InputField
          label="OTP"
          value={formData.otp}
          onChangeText={(text) => setFormData({ ...formData, otp: text })}
          error={errors.otp}
          keyboardType="numeric"
        />
      )}

      <CustomButton
        title={otpSent ? "Verify OTP" : "Sign Up"}
        onPress={otpSent ? handleVerifyOTP : handleSignup}
        style={styles.button}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.lg,
    backgroundColor: colors.background
  },
  button: {
    marginTop: spacing.md
  }
});

export default SignupScreen;
