import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Button, List, Switch } from 'react-native-paper';
import { MobileFormScreen } from '../../components/mobile/MobileFormScreen';
import { platformConnectionService } from '../../../shared/services/platformConnectionService';
import { COLORS } from '../../../assets/config/colors';
import { SPACING } from '../../../assets/config/spacing';

const PLATFORMS = [
  {
    id: 'uber',
    name: 'Uber',
    icon: 'car',
    forms: ['1099-K', '1099-NEC']
  },
  {
    id: 'lyft',
    name: 'Lyft',
    icon: 'car',
    forms: ['1099-K']
  },
  {
    id: 'doordash',
    name: 'DoorDash',
    icon: 'food',
    forms: ['1099-NEC']
  },
  {
    id: 'instacart',
    name: 'Instacart',
    icon: 'cart',
    forms: ['1099-NEC']
  }
];

export const PlatformConnectionScreen = ({ navigation }) => {
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([]);
  const [loading, setLoading] = useState<{[key: string]: boolean}>({});

  const handleConnect = async (platformId: string) => {
    setLoading(prev => ({ ...prev, [platformId]: true }));
    try {
      await platformConnectionService.connectPlatform(platformId, 'current-user-id');
      setConnectedPlatforms(prev => [...prev, platformId]);
      
      // Fetch and validate Internal Revenue Service fields for the platform
      const irsFields = await platformConnectionService.getIRSFields(platformId);
      await platformConnectionService.validateIRSFields(platformId, irsFields);
      
    } catch (error) {
      console.error('Platform connection error:', error);
    } finally {
      setLoading(prev => ({ ...prev, [platformId]: false }));
    }
  };

  const handleDisconnect = async (platformId: string) => {
    try {
      await platformConnectionService.disconnectPlatform(platformId, 'current-user-id');
      setConnectedPlatforms(prev => prev.filter(id => id !== platformId));
    } catch (error) {
      console.error('Platform disconnection error:', error);
    }
  };

  return (
    <MobileFormScreen>
      <View style={styles.header}>
        <Text style={styles.title}>Connect Your Platforms</Text>
        <Text style={styles.subtitle}>
          Link your gig economy platforms to automatically import tax documents
        </Text>
      </View>

      <ScrollView style={styles.content}>
        {PLATFORMS.map((platform) => (
          <Card key={platform.id} style={styles.platformCard}>
            <Card.Content>
              <View style={styles.platformHeader}>
                <List.Item
                  title={platform.name}
                  description={`Supports: ${platform.forms.join(', ')}`}
                  left={props => <List.Icon {...props} icon={platform.icon} />}
                />
                <Switch
                  value={connectedPlatforms.includes(platform.id)}
                  onValueChange={() => {
                    if (connectedPlatforms.includes(platform.id)) {
                      handleDisconnect(platform.id);
                    } else {
                      handleConnect(platform.id);
                    }
                  }}
                  disabled={loading[platform.id]}
                />
              </View>
            </Card.Content>
          </Card>
        ))}
      </ScrollView>

      <View style={styles.footer}>
        <Button
          mode="contained"
          onPress={() => navigation.navigate('TaxProfile')}
          disabled={connectedPlatforms.length === 0}
        >
          Continue to Tax Profile
        </Button>
      </View>
    </MobileFormScreen>
  );
};

const styles = StyleSheet.create({
  header: {
    padding: SPACING.md
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: SPACING.sm
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.text.secondary
  },
  content: {
    flex: 1,
    padding: SPACING.md
  },
  platformCard: {
    marginBottom: SPACING.md
  },
  platformHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  footer: {
    padding: SPACING.md,
    borderTopWidth: 1,
    borderTopColor: COLORS.divider
  }
});
