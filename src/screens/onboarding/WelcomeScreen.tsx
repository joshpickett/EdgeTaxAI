import React from 'react';
import { View, StyleSheet, Image } from 'react-native';
import { Text, Button } from 'react-native-paper';
import { MobileFormScreen } from '../../components/mobile/MobileFormScreen';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';
import Icon from 'react-native-vector-icons/Ionicons'; // Added import for Icon

export const WelcomeScreen = ({ navigation }) => {
  return (
    <MobileFormScreen scrollable={false}>
      <View style={styles.container}>
        <Image
          source={require('../../../assets/logo/primary/edgetaxai-vertical-color.svg')}
          style={styles.logo}
        />
        
        <View style={styles.content}>
          <Text style={styles.title}>Welcome to EdgeTaxAI</Text>
          <Text style={styles.subtitle}>
            Let's get started with organizing your tax documents and maximizing your deductions
          </Text>
          
          <View style={styles.features}>
            <FeatureItem
              icon="document-text"
              title="Smart Document Processing"
              description="Automatically scan and categorize your tax documents"
            />
            <FeatureItem
              icon="calculator"
              title="Tax Optimization"
              description="Get AI-powered suggestions for maximizing deductions"
            />
            <FeatureItem
              icon="sync"
              title="Platform Integration"
              description="Connect your gig economy platforms for automated tracking"
            />
          </View>
        </View>

        <View style={styles.footer}>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('DocumentCollection')}
            style={styles.button}
          >
            Get Started
          </Button>
        </View>
      </View>
    </MobileFormScreen>
  );
};

const FeatureItem = ({ icon, title, description }) => (
  <View style={styles.featureItem}>
    <Icon name={icon} size={24} color={COLORS.primary} />
    <View style={styles.featureText}>
      <Text style={styles.featureTitle}>{title}</Text>
      <Text style={styles.featureDescription}>{description}</Text>
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
  features: {
    marginTop: SPACING.xl
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.lg
  },
  featureText: {
    marginLeft: SPACING.md,
    flex: 1
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: SPACING.xs
  },
  featureDescription: {
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
