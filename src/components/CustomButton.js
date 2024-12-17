import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

const CustomButton = ({ title, onPress }) => {
  return (
    <TouchableOpacity style={styles.button} onPress={onPress}>
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: { backgroundColor: '#007BFF', padding: 12, borderRadius: 5, alignItems: 'center' },
  text: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
});

export default CustomButton;
