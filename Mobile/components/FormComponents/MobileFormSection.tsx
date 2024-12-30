import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Animated } from 'react-native';
import { IRSFormSection } from '../../../shared/types/irs-forms';
import { MobileFormField } from './MobileFormField';

interface Props {
  section: IRSFormSection;
  values: Record<string, any>;
  onChange: (fieldName: string, value: any) => void;
  errors?: Record<string, string>;
}

export const MobileFormSection: React.FC<Props> = ({
  section,
  values,
  onChange,
  errors = {}
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [animation] = useState(new Animated.Value(0));

  const toggleExpand = () => {
    const toValue = isExpanded ? 0 : 1;
    Animated.timing(animation, {
      toValue,
      duration: 300,
      useNativeDriver: false,
    }).start();
    setIsExpanded(!isExpanded);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={toggleExpand} style={styles.header}>
        <Text style={styles.title}>{section.title}</Text>
      </TouchableOpacity>
      
      <Animated.View style={[
        styles.content,
        {
          maxHeight: animation.interpolate({
            inputRange: [0, 1],
            outputRange: [0, 1000]
          })
        }
      ]}>
        {section.fields.map((field) => (
          <MobileFormField
            key={field.id}
            field={field}
            value={values[field.name]}
            onChange={(value) => onChange(field.name, value)}
            error={errors[field.name]}
          />
        ))}
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
    borderRadius: 8,
    backgroundColor: 'white',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  header: {
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
  },
  content: {
    padding: 16,
    overflow: 'hidden',
  },
});
