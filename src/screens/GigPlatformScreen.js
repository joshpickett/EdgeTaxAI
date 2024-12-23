import React, { useState } from "react";
import {
  View,
  Text,
  Button,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  Alert,
  Linking,
  TextInput,
  Image,
} from "react-native";
import {
  fetchPlatformData,
  fetchConnectedPlatforms,
  syncPlatformData,
  getSyncStatus,
  connectApiKeyPlatform,
} from "../services/gigPlatformService";
import PlatformDataDisplay from "../components/PlatformDataDisplay";
import { colors, typography, spacing } from '../styles/tokens';

// Asset paths
const ASSETS_DIR = '../assets';
const PLATFORM_ICON = `${ASSETS_DIR}/logo/icon/edgetaxai-icon-color.svg`;

// List of gig platforms
const platforms = [
  { name: "Uber", key: "uber", color: "#007BFF", method: "oauth" },
  { name: "Lyft", key: "lyft", color: "#FF69B4", method: "oauth" },
  { name: "DoorDash", key: "doordash", color: "#FF4500", method: "api_key" },
  { name: "Instacart", key: "instacart", color: "#32CD32", method: "api_key" },
  { name: "Upwork", key: "upwork", color: "#008080", method: "oauth" },
  { name: "Fiverr", key: "fiverr", color: "#FFBF00", method: "oauth" },
];

// Custom hook for platform management
const usePlatformManagement = () => {
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(false);
  return { platforms, setPlatforms, loading, setLoading };
};

const GigPlatformScreen = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState("");
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [apiKey, setApiKey] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const MAX_RETRIES = 3;

  // Function to handle OAuth connection
  const handleConnectOAuth = async (platformKey) => {
    try {
      const authUrl = `https://your-backend-api.com/api/gig/connect/${platformKey}`;
      Linking.openURL(authUrl).catch(() => {
        Alert.alert("Error", `Failed to open connection URL for ${platformKey.toUpperCase()}.`);
      });
    } catch (error) {
      Alert.alert("Error", "Failed to initiate platform connection.");
    }
  };

  // Function to handle API key connection
  const handleConnectApiKey = async (platform) => {
    try {
      if (!apiKey) {
        Alert.alert("Error", "Please enter an API key to connect.");
        return;
      }
      const message = await connectApiKeyPlatform(platform, apiKey);
      Alert.alert("Success", message);
    } catch (error) {
      handleApiError(error, platform);
    }
  };

  // Enhanced error handling for API connections
  const handleApiError = (error, platform) => {
    console.error(`Platform connection error (${platform}):`, error);
    Alert.alert(
      "Connection Error",
      `Failed to connect to ${platform}. Please try again later.`
    );
  };

  // Load connected platforms
  const loadConnectedPlatforms = async () => {
    setLoading(true);
    try {
      const userId = "123"; // Replace with actual user ID
      const platforms = await fetchConnectedPlatforms(userId);
      setConnectedPlatforms(platforms);
    } catch (error) {
      Alert.alert("Error", "Failed to fetch connected platforms.");
    } finally {
      setLoading(false);
    }
  };

  // Function to handle platform sync with retry
  const handleSync = async (platform) => {
    setLoading(true);
    try {
      const userId = "123"; // Replace with actual user ID
      await syncPlatformData(platform, userId);
      setRetryCount(0);
      Alert.alert("Success", `${platform} data synced successfully`);
      loadConnectedPlatforms(); // Refresh the list after sync
    } catch (error) {
      if (retryCount < MAX_RETRIES) {
        setRetryCount(prev => prev + 1);
        setTimeout(() => handleSync(platform), 1000 * Math.pow(2, retryCount));
      } else {
        Alert.alert("Error", `Failed to sync ${platform} data after ${MAX_RETRIES} attempts`);
        setRetryCount(0);
      }
    } finally {
      setLoading(false);
    }
  };

  // Function to handle pull-to-refresh
  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    try {
      await loadConnectedPlatforms();
    } catch (error) {
      Alert.alert("Error", "Failed to refresh platforms");
    } finally {
      setRefreshing(false);
    }
  }, []);

  // Fetch platform data
  const handleFetchData = async (platform) => {
    setLoading(true);
    setSelectedPlatform(platform);
    try {
      const userId = "123"; // Replace with actual user ID
      const fetchedData = await fetchPlatformData(platform, userId);
      setData(fetchedData);
    } catch (error) {
      Alert.alert("Error", error.message || `Failed to fetch data for ${platform}.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Manage Gig Platforms</Text>
      <Image source={PLATFORM_ICON} style={styles.icon} />

      {/* Platform Connection Section */}
      {platforms.map((platform) => (
        <View key={platform.key} style={styles.buttonContainer}>
          <Text style={styles.subTitle}>{platform.name}</Text>
          {platform.method === "oauth" ? (
            <Button
              title={`Connect ${platform.name}`}
              color={platform.color}
              onPress={() => handleConnectOAuth(platform.key)}
            />
          ) : (
            <>
              <TextInput
                style={styles.input}
                placeholder={`Enter ${platform.name} API Key`}
                value={apiKey}
                onChangeText={setApiKey}
              />
              <Button
                title={`Connect ${platform.name}`}
                color={platform.color}
                onPress={() => handleConnectApiKey(platform.key)}
              />
            </>
          )}
        </View>
      ))}

      <Button
        title="Load Connected Platforms"
        color="#17A2B8"
        onPress={loadConnectedPlatforms}
      />

      {/* Display Connected Platforms */}
      {connectedPlatforms.length > 0 && (
        <View>
          <Text style={styles.subTitle}>Connected Platforms</Text>
          <ScrollView
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={onRefresh}
                colors={["#007BFF"]}
              />
            }
          >
            {connectedPlatforms.map((platform, index) => (
              <Text key={index} style={styles.connectedText}>
                ÃÂ¢ {platform.platform.toUpperCase()}
                <Button
                  title="Sync"
                  onPress={() => handleSync(platform.platform)}
                />
              </Text>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Fetch and Display Platform Data */}
      <Text style={styles.subTitle}>Fetch Platform Data</Text>
      {platforms.map((platform) => (
        <View key={platform.key} style={styles.buttonContainer}>
          <Button
            title={`Fetch ${platform.name} Data`}
            color={platform.color}
            onPress={() => handleFetchData(platform.key)}
          />
        </View>
      ))}

      {loading && <ActivityIndicator size="large" color="#007BFF" />}
      {!loading && data.length > 0 && (
        <View>
          <Text style={styles.subTitle}>Data for {selectedPlatform.toUpperCase()}</Text>
          <PlatformDataDisplay
            data={data}
            platform={selectedPlatform}
          />
        </View>
      )}

      <Text style={styles.footer}>
        By connecting your account, you allow us to fetch your trip and earnings data securely.
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: spacing.lg, backgroundColor: colors.background.default },
  title: { fontSize: typography.fontSize.lg, fontWeight: typography.fontWeight.bold, color: colors.text.primary, textAlign: "center", marginBottom: 10 },
  subTitle: { fontSize: 18, fontWeight: "bold", marginTop: 10, marginBottom: 5 },
  buttonContainer: { marginBottom: 15 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 8,
    marginBottom: 10,
    borderRadius: 5,
    backgroundColor: "#FFF",
  },
  connectedText: { fontSize: 16, color: "#28A745", marginBottom: 5 },
  item: {
    padding: 10,
    marginVertical: 5,
    backgroundColor: "#E7F3FF",
    borderRadius: 5,
  },
  footer: { fontSize: 12, color: "#888", textAlign: "center", marginTop: 20 },
  icon: {
    width: 50,
    height: 50,
    marginBottom: spacing.md,
  },
});

export default GigPlatformScreen;
