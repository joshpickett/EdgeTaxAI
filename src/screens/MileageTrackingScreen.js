import React, { useState } from "react";
import { View, Text, Button, StyleSheet, Alert } from "react-native";
import { getCurrentLocation, calculateDistance } from "../services/mileageService";

const MileageTrackingScreen = () => {
  const [distance, setDistance] = useState(null);

  const handleCalculateDistance = async () => {
    try {
      // Fetch current location
      const origin = await getCurrentLocation();
      const destination = { latitude: 37.7749, longitude: -122.4194 }; // Example: San Francisco

      // Calculate the distance
      const result = await calculateDistance(origin, destination);
      setDistance(result);
    } catch (error) {
      Alert.alert("Error", error.message);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Mileage Tracking</Text>
      <Button title="Calculate Distance" onPress={handleCalculateDistance} />
      {distance && <Text style={styles.result}>Distance: {distance}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", padding: 20 },
  title: { fontSize: 24, fontWeight: "bold", marginBottom: 20 },
  result: { marginTop: 20, fontSize: 18, color: "green" },
});

export default MileageTrackingScreen;
