import React, { useState, useEffect } from "react";
import { View, Text, TextInput, Button, Alert, StyleSheet, Switch } from "react-native";
import DateTimePicker from '@react-native-community/datetimepicker';
import * as Location from 'expo-location';
import mileageService from "../../shared/services/mileageService";

// Add location tracking functionality
const useLocationTracking = () => {
  const [tracking, setTracking] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [distance, setDistance] = useState(0);
  return { tracking, setTracking, currentLocation, setCurrentLocation, distance, setDistance };
};

const MileageTrackingScreen = () => {
  const [startLocation, setStartLocation] = useState("");
  const [endLocation, setEndLocation] = useState("");
  const [purpose, setPurpose] = useState("");
  const [recurring, setRecurring] = useState(false);
  const [frequency, setFrequency] = useState("weekly");
  const [date, setDate] = useState(new Date());
  const [distance, setDistance] = useState(null);
  const [taxDeduction, setTaxDeduction] = useState(null);
  const [isTracking, setIsTracking] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [watchId, setWatchId] = useState(null);

  const handleCalculate = async () => {
    try {
      if (!startLocation || !endLocation || !purpose) {
        Alert.alert("Error", "All fields are required.");
        return;
      }

      const result = await mileageService.calculateMileage({
        start: startLocation,
        end: endLocation,
        purpose: purpose,
        recurring: recurring,
        frequency: frequency,
        date: date.toISOString()
      });
      setDistance(result.distance);
      setTaxDeduction(result.tax_deduction);
    } catch (error) {
      Alert.alert("Error", error.message);
    }
  };

  // Add automatic mileage calculation
  const calculateDistance = (startLoc, endLoc) => {
    if (!startLoc || !endLoc) return 0;
    
    const R = 6371; // Earth's radius in km
    const dLat = (endLoc.latitude - startLoc.latitude) * Math.PI / 180;
    const dLon = (endLoc.longitude - startLoc.longitude) * Math.PI / 180;
    
    return R * Math.sqrt(dLat * dLat + dLon * dLon);
  };

  const startGPSTracking = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      
      if (status === 'granted') {
        setIsTracking(true);
        const id = Location.watchPositionAsync(
          { accuracy: Location.Accuracy.High, distanceInterval: 10 },
          position => {
            setCurrentLocation(position.coords);
          }
        );
        setWatchId(id);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };
  
  const stopGPSTracking = () => {
    if (watchId !== null) {
      watchId.remove();
      setWatchId(null);
      setIsTracking(false);
    }
  };

  useEffect(() => {
    if (isTracking) {
      startGPSTracking();
    } else {
      stopGPSTracking();
    }
    
    return () => {
      stopGPSTracking();
    };
  }, [isTracking]);

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
      <TextInput
        style={styles.input}
        placeholder="Business Purpose"
        value={purpose}
        onChangeText={setPurpose}
      />
      <View style={styles.switchContainer}>
        <Text>Recurring Trip</Text>
        <Switch
          value={recurring}
          onValueChange={setRecurring}
        />
      </View>
      {recurring && (
        <TextInput
          style={styles.input}
          placeholder="Frequency (e.g., weekly, monthly)"
          value={frequency}
          onChangeText={setFrequency}
        />
      )}
      <DateTimePicker
        value={date}
        mode="date"
        display="default"
        onChange={(event, selectedDate) => {
          const currentDate = selectedDate || date;
          setDate(currentDate);
        }}
      />
      <Button title="Track Mileage" onPress={handleCalculate} />
      {distance && <Text style={styles.result}>Distance: {distance}</Text>}
      {taxDeduction && <Text style={styles.result}>Estimated Tax Deduction: ${taxDeduction.toFixed(2)}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 20 },
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  input: { borderWidth: 1, borderColor: "#ccc", padding: 10, marginBottom: 10, borderRadius: 5 },
  switchContainer: { flexDirection: "row", alignItems: "center", marginBottom: 10 },
  result: { marginTop: 20, fontSize: 18, color: "green", textAlign: "center" },
});

export default MileageTrackingScreen;
