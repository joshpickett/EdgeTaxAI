import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { setupSrcPath } from '../setup_path';
setupSrcPath();
import InputField from './InputField';
import Button from './CustomButton';
import { colors, spacing, typography } from '../styles/tokens';

const LoginForm = ({ onSubmit }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = () => {
    onSubmit({ email, password });
  };

  return (
    <View style={styles.container}>
      <InputField
        label="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />
      <InputField
        label="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title="Login" onPress={handleSubmit} style={styles.button} />
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
