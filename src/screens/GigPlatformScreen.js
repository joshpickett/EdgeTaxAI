import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Card, Button, Divider, Portal, Modal } from 'react-native-paper';
import { MobileFormScreen } from '../components/mobile/MobileFormScreen';
import { PlatformDataDisplay } from '../components/PlatformDataDisplay';
import { platformService } from '../../shared/services/platformService';
import { COLORS } from '../../assets/config/colors';
import { SPACING } from '../../assets/config/spacing';

const PLATFORMS = {
  UBER: 'uber',
  LYFT: 'lyft',
  DOORDASH: 'doordash',
  INSTACART: 'instacart'
};

export const GigPlatformScreen = ({ navigation }) => {
  const [connectedPlatforms, setConnectedPlatforms] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadPlatformData();
  }, []);

  const loadPlatformData = async () => {
    try {
      setLoading(true);
      const platforms = await platformService.getConnectedPlatforms();
      setConnectedPlatforms(platforms);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (platform) => {
    try {
      setSelectedPlatform(platform);
      const result = await platformService.connectPlatform(platform);
      setConnectedPlatforms(prev => ({
        ...prev,
        [platform]: result
      }));
      setShowModal(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDisconnect = async (platform) => {
    try {
      await platformService.disconnectPlatform(platform);
      setConnectedPlatforms(prev => {
        const updated = { ...prev };
        delete updated[platform];
        return updated;
      });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <MobileFormScreen>
      <ScrollView style={styles.container}>
        <Text style={styles.title}>Connected Platforms</Text>
        
        {Object.entries(PLATFORMS).map(([key, platform]) => (
          <Card key={platform} style={styles.platformCard}>
            <Card.Content>
              <View style={styles.platformHeader}>
                <Text style={styles.platformName}>{key}</Text>
                <Button
                  mode={connectedPlatforms[platform] ? "outlined" : "contained"}
                  onPress={() => connectedPlatforms[platform] 
                    ? handleDisconnect(platform)
                    : handleConnect(platform)
                  }
                >
                  {connectedPlatforms[platform] ? "Disconnect" : "Connect"}
                </Button>
              </View>
              
              {connectedPlatforms[platform] && (
                <PlatformDataDisplay 
                  platformData={connectedPlatforms[platform]}
                  isLoading={loading}
                  error={error}
                />
              )}
            </Card.Content>
          </Card>
        ))}
      </ScrollView>

      <Portal>
        <Modal
          visible={showModal}
          onDismiss={() => setShowModal(false)}
          contentContainerStyle={styles.modal}
        >
          <Text style={styles.modalTitle}>
            Connect to {selectedPlatform}
          </Text>
          <Text style={styles.modalText}>
            You will be redirected to {selectedPlatform} to authorize access.
          </Text>
          <Button
            mode="contained"
            onPress={() => handleConnect(selectedPlatform)}
            style={styles.modalButton}
          >
            Continue
          </Button>
          <Button
            onPress={() => setShowModal(false)}
          >
            Cancel
          </Button>
        </Modal>
      </Portal>
    </MobileFormScreen>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: SPACING.md,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
  platformCard: {
    marginBottom: SPACING.md,
  },
  platformHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  platformName: {
    fontSize: 18,
    fontWeight: '600',
  },
  modal: {
    backgroundColor: COLORS.background,
    padding: SPACING.lg,
    margin: SPACING.lg,
    borderRadius: 8,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: SPACING.md,
  },
  modalText: {
    marginBottom: SPACING.lg,
    color: COLORS.text.secondary,
  },
  modalButton: {
    marginBottom: SPACING.md,
  },
});
