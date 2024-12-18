import React, { useState } from "react";
import { View, Text, TextInput, Button, Alert, StyleSheet } from "react-native";
import { calculateMileage } from "../services/mileageService";

const MileageTrackingScreen = () => {
  const [startLocation, setStartLocation] = useState("");
  const [endLocation, setEndLocation] = useState("");
  const [distance, setDistance] = useState(null);

  const handleCalculate = async () => {
    try {
      if (!startLocation || !endLocation) {
        Alert.alert("Error", "Both start and end locations are required.");
        return;
      }

      const result = await calculateMileage(startLocation, endLocation);
      setDistance(result);
    } catch (error) {
      Alert.alert("Error", error.message);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Mileage Tracking</Text>
      <TextInput
        style={styles.input}
        placeholder="Start Location"
        value={startLocation}
        onChangeText={setStartLocation}
      />
      <TextInput
        style={styles.input}
        placeholder="End Location"
        value={endLocation}
        onChangeText={setEndLocation}
      />
      <Button title="Calculate Mileage" onPress={handleCalculate} />
      {distance && <Text style={styles.result}>Distance: {distance}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 20 },
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  input: { borderWidth: 1, borderColor: "#ccc", padding: 10, marginBottom: 10, borderRadius: 5 },
  result: { marginTop: 20, fontSize: 18, color: "green", textAlign: "center" },
});

export default MileageTrackingScreen;
