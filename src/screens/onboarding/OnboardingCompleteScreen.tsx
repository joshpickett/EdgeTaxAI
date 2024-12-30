import React from 'react';
import { View, StyleSheet, Image } from 'react-native';
import { Text, Button } from 'react-native-paper';
import { MobileFormScreen } from '../../components/mobile/MobileFormScreen';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons'; // Added import for Icon

export const OnboardingCompleteScreen = ({ navigation }) => {
  return (
    <MobileFormScreen scrollable={false}>
      <View style={styles.container}>
        <Image
          source={require('../../../assets/logo/primary/edgetaxai-vertical-color.svg')}
          style={styles.logo}
        />
        
        <View style={styles.content}>
          <Text style={styles.title}>You're All Set!</Text>
          <Text style={styles.subtitle}>
            Your tax profile is ready and your platforms are connected.
            Let's start organizing your taxes.
          </Text>
          
          <View style={styles.summaryContainer}>
            <SummaryItem
              icon="check-circle"
              title="Documents Collected"
              description="Your tax documents are ready for processing"
            />
            <SummaryItem
              icon="link"
              title="Platforms Connected"
              description="Your gig platforms are synced"
            />
            <SummaryItem
              icon="account"
              title="Profile Complete"
              description="Your tax profile is set up"
            />
          </View>
        </View>

        <View style={styles.footer}>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Dashboard')}
            style={styles.button}
          >
            Go to Dashboard
          </Button>
        </View>
      </View>
    </MobileFormScreen>
  );
};

const SummaryItem = ({ icon, title, description }) => (
  <View style={styles.summaryItem}>
    <Icon name={icon} size={24} color={COLORS.success} />
    <View style={styles.summaryText}>
      <Text style={styles.summaryTitle}>{title}</Text>
      <Text style={styles.summaryDescription}>{description}</Text>
    </View>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'space-between',
    padding: SPACING.lg
  },
  logo: {
    width: 200,
    height: 80,
    alignSelf: 'center',
    marginTop: SPACING.xl
  },
  content: {
    flex: 1,
    justifyContent: 'center'
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: SPACING.sm
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    color: COLORS.text.secondary,
    marginBottom: SPACING.xl
  },
  summaryContainer: {
    marginTop: SPACING.xl
  },
  summaryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.lg
  },
  summaryText: {
    marginLeft: SPACING.md,
    flex: 1
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: SPACING.xs
  },
  summaryDescription: {
    fontSize: 14,
    color: COLORS.text.secondary
  },
  footer: {
    marginTop: SPACING.xl
  },
  button: {
    paddingVertical: SPACING.sm
  }
});
