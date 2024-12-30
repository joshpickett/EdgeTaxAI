import React from 'react';
import { View, StyleSheet, TextInput, TouchableOpacity } from 'react-native';
import { Text } from 'react-native-paper';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../assets/config/typography';
import DateTimePicker from '@react-native-community/datetimepicker';
import { useFormContext } from 'react-hook-form';

interface MobileFormFieldProps {
  name: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'select';
  required?: boolean;
  placeholder?: string;
  options?: Array<{ label: string; value: string }>;
}

export const MobileFormField: React.FC<MobileFormFieldProps> = ({
  name,
  label,
  type = 'text',
  required = false,
  placeholder,
  options
}) => {
  const { register, setValue, watch } = useFormContext();
  const value = watch(name);
  const [showDatePicker, setShowDatePicker] = React.useState(false);

  const renderField = () => {
    switch (type) {
      case 'date':
        return (
          <TouchableOpacity 
            style={styles.dateInput}
            onPress={() => setShowDatePicker(true)}
          >
            <Text>{value ? new Date(value).toLocaleDateString() : placeholder}</Text>
            {showDatePicker && (
              <DateTimePicker
                value={value ? new Date(value) : new Date()}
                mode="date"
                onChange={(event, selectedDate) => {
                  setShowDatePicker(false);
                  if (selectedDate) {
                    setValue(name, selectedDate.toISOString());
                  }
                }}
              />
            )}
          </TouchableOpacity>
        );

      case 'number':
        return (
          <TextInput
            style={styles.input}
            keyboardType="numeric"
            placeholder={placeholder}
            value={value}
            onChangeText={(text) => setValue(name, text)}
          />
        );

      default:
        return (
          <TextInput
            style={styles.input}
            placeholder={placeholder}
            value={value}
            onChangeText={(text) => setValue(name, text)}
          />
        );
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>
        {label} {required && <Text style={styles.required}>*</Text>}
      </Text>
      {renderField()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: SPACING.md
  },
  label: {
    marginBottom: SPACING.sm,
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontFamily: TYPOGRAPHY.fontFamily.medium
  },
  required: {
    color: COLORS.error
  },
  input: {
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 8,
    padding: SPACING.sm,
    fontSize: TYPOGRAPHY.fontSize.md
  },
  dateInput: {
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: 8,
    padding: SPACING.sm,
    fontSize: TYPOGRAPHY.fontSize.md
  }
});
