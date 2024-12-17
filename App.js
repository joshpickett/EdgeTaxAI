import React, { useEffect } from "react";
import { View, Text, StyleSheet } from "react-native";
import firebase from "firebase/app";
import "firebase/messaging"; // Import messaging for notifications if needed
import AppNavigator from "./src/navigation/AppNavigator";

// Firebase Configuration
const firebaseConfig = {
  apiKey: "AIzaSyAj9wZxikUsYyFROyjeUkQTDLf6Gq02dnQ",
  authDomain: "edgetaxai.firebaseapp.com",
  projectId: "edgetaxai",
  storageBucket: "edgetaxai.firebasestorage.app",
  messagingSenderId: "1099137610113",
  appId: "1:1099137610113:ios:eb59ea951c327b751ff880",
};

if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}

const App = () => {
  useEffect(() => {
    console.log("Firebase initialized successfully!");
    // Add notification setup or other Firebase setup logic here if needed
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
