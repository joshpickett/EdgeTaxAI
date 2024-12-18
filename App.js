import React, { useEffect } from "react";
import { View, Text, StyleSheet, Alert } from "react-native";
import firebase from "firebase/app";
import "firebase/messaging";
import * as Notifications from "expo-notifications";
import Constants from "expo-constants";
import AppNavigator from "./src/navigation/AppNavigator";
import { registerForPushNotifications } from "./src/services/notificationService"; // Push Notification Logic

// Load environment variables
import {
  FIREBASE_API_KEY,
  FIREBASE_AUTH_DOMAIN,
  FIREBASE_PROJECT_ID,
  FIREBASE_STORAGE_BUCKET,
  FIREBASE_MESSAGING_SENDER_ID,
  FIREBASE_APP_ID,
} from "react-native-dotenv";

// Firebase Configuration
const firebaseConfig = {
  apiKey: FIREBASE_API_KEY,
  authDomain: FIREBASE_AUTH_DOMAIN,
  projectId: FIREBASE_PROJECT_ID,
  storageBucket: FIREBASE_STORAGE_BUCKET,
  messagingSenderId: FIREBASE_MESSAGING_SENDER_ID,
  appId: FIREBASE_APP_ID,
};

try {
  if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
    console.log("Firebase initialized successfully!");
  }
} catch (error) {
  console.error("Firebase initialization error:", error.message);
}

const App = () => {
  useEffect(() => {
    const setupNotifications = async () => {
      try {
        const { expoPushToken, fcmToken } = await registerForPushNotifications();
        console.log("Expo Push Token:", expoPushToken);
        console.log("FCM Token:", fcmToken);
      } catch (error) {
        console.error("Notification Setup Error:", error.message);
      }
    };

    setupNotifications();
  }, []);

  return (
    <View style={styles.container}>
      <AppNavigator />
      <Text style={styles.text}>Welcome to EdgeTaxAI!</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center" },
  text: { fontSize: 18, fontWeight: "bold", color: "#333" },
});

export default App;
