import React from 'react';
import { View, TextInput, Text, StyleSheet } from 'react-native';
import { IRSFormField } from '../../../shared/types/irs-forms';

interface Props {
  field: IRSFormField;
  value: any;
  onChange: (value: any) => void;
  error?: string;
}

export const MobileFormField: React.FC<Props> = ({
  field,
  value,
  onChange,
  error
}) => {
  const renderField = () => {
    switch (field.type) {
      case 'text':
      case 'number':
        return (
          <TextInput
            style={[styles.input, error && styles.inputError]}
            value={String(value || '')}
            onChangeText={onChange}
            keyboardType={field.type === 'number' ? 'numeric' : 'default'}
            placeholder={field.placeholder}
          />
        );

      // Add other field types here

      default:
        return null;
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{field.label}</Text>
      {renderField()}
      {error && <Text style={styles.errorText}>{error}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    padding: 12,
    fontSize: 16,
  },
  inputError: {
    borderColor: 'red',
  },
  errorText: {
    color: 'red',
    fontSize: 12,
    marginTop: 4,
  },
});
