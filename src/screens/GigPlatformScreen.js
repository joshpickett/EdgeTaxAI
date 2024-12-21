import React, { useState } from "react";
import {
  View,
  Text,
  Button,
  StyleSheet,
  FlatList,
  ActivityIndicator,
  Alert,
  Linking,
  TextInput,
} from "react-native";
import {
  fetchPlatformData,
  fetchConnectedPlatforms,
  connectApiKeyPlatform,
} from "../services/gigPlatformService";

// List of gig platforms
const platforms = [
  { name: "Uber", key: "uber", color: "#007BFF", method: "oauth" },
  { name: "Lyft", key: "lyft", color: "#FF69B4", method: "oauth" },
  { name: "DoorDash", key: "doordash", color: "#FF4500", method: "api_key" },
  { name: "Instacart", key: "instacart", color: "#32CD32", method: "api_key" },
  { name: "Upwork", key: "upwork", color: "#008080", method: "oauth" },
  { name: "Fiverr", key: "fiverr", color: "#FFBF00", method: "oauth" },
];

const GigPlatformScreen = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState("");
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [apiKey, setApiKey] = useState("");

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
      Alert.alert("Error", error.message || "Failed to connect with API key.");
    }
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
          {connectedPlatforms.map((platform, index) => (
            <Text key={index} style={styles.connectedText}>
              ✅ {platform.platform.toUpperCase()}
            </Text>
          ))}
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
          <FlatList
            data={data}
            keyExtractor={(item, index) => index.toString()}
            renderItem={({ item }) => (
              <View style={styles.item}>
                <Text>{JSON.stringify(item)}</Text>
              </View>
            )}
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
  container: { flex: 1, padding: 20, backgroundColor: "#F9F9F9" },
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 10 },
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
});

export default GigPlatformScreen;
