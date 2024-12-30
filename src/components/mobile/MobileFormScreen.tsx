import React from 'react';
import { View, ScrollView, StyleSheet, SafeAreaView, KeyboardAvoidingView, Platform } from 'react-native';
import { useHeaderHeight } from '@react-navigation/elements';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';

interface MobileFormScreenProps {
  children: React.ReactNode;
  scrollable?: boolean;
  keyboardAware?: boolean;
}

export const MobileFormScreen: React.FC<MobileFormScreenProps> = ({
  children,
  scrollable = true,
  keyboardAware = true
}) => {
  const headerHeight = useHeaderHeight();

  const content = (
    <View style={styles.container}>
      {children}
    </View>
  );

  const wrappedContent = scrollable ? (
    <ScrollView 
      style={styles.scrollView}
      keyboardShouldPersistTaps="handled"
      showsVerticalScrollIndicator={false}
    >
      {content}
    </ScrollView>
  ) : content;

  return (
    <SafeAreaView style={styles.safeArea}>
      {keyboardAware ? (
        <KeyboardAvoidingView
          style={styles.keyboardAvoid}
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
          keyboardVerticalOffset={headerHeight}
        >
          {wrappedContent}
        </KeyboardAvoidingView>
      ) : wrappedContent}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.background
  },
  keyboardAvoid: {
    flex: 1
  },
  scrollView: {
    flex: 1
  },
  container: {
    flex: 1,
    padding: SPACING.md
  }
});
