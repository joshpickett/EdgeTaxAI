import React from 'react';
import { View, TextInput, StyleSheet, Text } from 'react-native';

const InputField = ({ label, placeholder, value, onChangeText, secureTextEntry, keyboardType }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        style={styles.input}
        placeholder={placeholder}
        value={value}
        onChangeText={onChangeText}
        secureTextEntry={secureTextEntry}
        keyboardType={keyboardType}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { marginBottom: 15 },
  label: { marginBottom: 5, fontSize: 14, fontWeight: 'bold' },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, borderRadius: 5 },
});

export default InputField;
