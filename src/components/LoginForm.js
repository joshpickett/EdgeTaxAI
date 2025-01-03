import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { SharedValidator } from 'shared/utils/validators';
import InputField from './InputField';
import CustomButton from './CustomButton';

const LoginForm = ({ onSubmit }) => {
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState({});

  const handleSubmit = () => {
    const validationErrors = SharedValidator.validateAuth({ email });
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }
    onSubmit({ email });
  };

  return (
    <View style={styles.container}>
      <InputField
        label="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        error={errors.email}
        keyboardType="email-address"
      />
      <CustomButton title="Login" onPress={handleSubmit} style={styles.button} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: spacing.lg,
    width: '100%',
  },
  button: {
    marginTop: spacing.lg,
    backgroundColor: colors.primary.main,
  }
});

export default LoginForm;
