import * as Location from "expo-location";
import { Platform } from "react-native";

// Platform-specific API keys
const GOOGLE_API_KEY = Platform.select({
  android: "AIzaSyBdIKjNKN37U6eDqDw6u1PEiQ8VHhjefx0", // Android API Key
  ios: "AIzaSyD-lLZVArNjgAN7mTZlehn5H7wbPZtncS4", // iOS API Key
});

// Function to get the user's current location
export const getCurrentLocation = async () => {
  const { status } = await Location.requestForegroundPermissionsAsync();

  if (status !== "granted") {
    throw new Error("Location permission not granted.");
  }

  const location = await Location.getCurrentPositionAsync({});
  return location.coords; // { latitude, longitude }
};

// Function to calculate distance using Google Maps Directions API
export const calculateDistance = async (origin, destination) => {
  const originStr = `${origin.latitude},${origin.longitude}`;
  const destinationStr = `${destination.latitude},${destination.longitude}`;

  const url = `https://maps.googleapis.com/maps/api/directions/json?origin=${originStr}&destination=${destinationStr}&key=${GOOGLE_API_KEY}`;

  const response = await fetch(url);
  const data = await response.json();

  if (data.status === "OK") {
    const distance = data.routes[0].legs[0].distance.text; // Example: "12.3 km"
    return distance;
  } else {
    throw new Error("Error fetching distance from Google API.");
  }
};
