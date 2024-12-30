import React, { useState } from 'react';
import { View, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { Text } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import { TYPOGRAPHY } from '../../../assets/config/typography';

interface MobileFormSectionProps {
  title: string;
  children: React.ReactNode;
  initiallyExpanded?: boolean;
}

export const MobileFormSection: React.FC<MobileFormSectionProps> = ({
  title,
  children,
  initiallyExpanded = true
}) => {
  const [expanded, setExpanded] = useState(initiallyExpanded);
  const [animation] = useState(new Animated.Value(initiallyExpanded ? 1 : 0));

  const toggleExpanded = () => {
    const toValue = expanded ? 0 : 1;
    Animated.timing(animation, {
      toValue,
      duration: 300,
      useNativeDriver: false
    }).start();
    setExpanded(!expanded);
  };

  const heightInterpolate = animation.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 500] // Adjust based on content
  });

  return (
    <View style={styles.container}>
      <TouchableOpacity 
        style={styles.header} 
        onPress={toggleExpanded}
        activeOpacity={0.7}
      >
        <Text style={styles.title}>{title}</Text>
        <Icon 
          name={expanded ? 'expand-less' : 'expand-more'} 
          size={24} 
          color={COLORS.text.secondary}
        />
      </TouchableOpacity>
      <Animated.View style={[styles.content, { height: heightInterpolate }]}>
        {children}
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.background,
    borderRadius: 8,
    marginBottom: SPACING.md,
    elevation: 2,
    shadowColor: COLORS.text.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.divider
  },
  title: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontFamily: TYPOGRAPHY.fontFamily.medium
  },
  content: {
    overflow: 'hidden'
  }
});
