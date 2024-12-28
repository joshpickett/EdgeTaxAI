import React from 'react';
import { View, TextInput, StyleSheet, Text } from 'react-native';
import { setupSrcPath } from '../setup_path';
setupSrcPath();
import { colors, typography, spacing } from '../styles/tokens';

const InputField = ({ label, placeholder, value, onChangeText, secureTextEntry, keyboardType, error }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        style={[styles.input, error && styles.inputError]}
        placeholder={placeholder}
        value={value}
        onChangeText={onChangeText}
        secureTextEntry={secureTextEntry}
        keyboardType={keyboardType}
      />
      {error && <Text style={styles.errorText}>{error}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginBottom: spacing.md },
  label: { marginBottom: spacing.xs, fontSize: typography.fontSize.sm, fontWeight: typography.fontWeight.bold },
  input: { borderWidth: 1, borderColor: colors.grey[300], padding: spacing.sm, borderRadius: 5 },
  inputError: {
    borderColor: colors.error.main,
  },
  errorText: {
    color: colors.error.main,
    fontSize: typography.fontSize.xs,
    marginTop: spacing.xs,
  }
});

export default InputField;
