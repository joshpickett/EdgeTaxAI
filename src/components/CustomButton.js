import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { setupSrcPath } from '../setup_path';
import { colors, typography, spacing } from '../styles/tokens';

const CustomButton = ({ title, onPress }) => {
  return (
    <TouchableOpacity style={styles.button} onPress={onPress}>
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: colors.primary.main,
    padding: spacing.md,
    borderRadius: spacing.xs,
    alignItems: 'center'
  },
  text: {
    color: colors.text.contrast,
    fontWeight: typography.fontWeight.bold,
    fontSize: typography.fontSize.md
  },
});

export default CustomButton;
