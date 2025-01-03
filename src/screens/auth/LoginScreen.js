import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { UnifiedAuthService } from 'shared/services/unifiedAuthService';
import { SharedValidator } from 'shared/utils/validators';
import CustomButton from '../components/CustomButton';

const authService = UnifiedAuthService.getInstance();

const LoginScreen = ({ navigation }) => {
  const [identifier, setIdentifier] = useState('');
  const [errors, setErrors] = useState({});

  const handleLogin = async () => {
    try {
      const validationErrors = SharedValidator.validateAuth({ identifier });
      if (validationErrors.length > 0) {
        setErrors(validationErrors);
        return;
      }
      await authService.login({ identifier });
      // Handle success
    } catch (error) {
      setErrors({ general: error.message });
      // Handle error
    }
  };

  const handleVerifyOTP = async () => {
    try {
      const result = await authService.verifyOTP({ 
        identifier, 
        otp,
        deviceInfo: navigator.userAgent 
      });
      // Handle success
    } catch (error) {
      // Handle error
    }
  };

  return (
    <View style={styles.container}>
      {/* Input fields and buttons go here */}
      <CustomButton title="Login" onPress={handleLogin} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
});

export default LoginScreen;
