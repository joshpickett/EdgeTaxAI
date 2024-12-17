import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, Alert } from "react-native";
import CustomButton from "../components/CustomButton";
import { resetPassword } from "../services/api";

const PasswordResetScreen = ({ navigation }) => {
  const [identifier, setIdentifier] = useState("");

  const handleReset = async () => {
    try {
      const response = await resetPassword(identifier);
      if (response.success) {
        Alert.alert("Success", "Password reset link sent successfully!");
        navigation.navigate("Login");
      } else {
        Alert.alert("Error", response.message || "Failed to send reset link.");
      }
    } catch (error) {
      Alert.alert("Error", "An error occurred. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Reset Password</Text>
      <Text style={styles.subtitle}>Enter your email or phone number to receive a reset link.</Text>
      <TextInput
        style={styles.input}
        placeholder="Email or Phone"
        value={identifier}
        onChangeText={setIdentifier}
        keyboardType="default"
      />
      <CustomButton title="Send Reset Link" onPress={handleReset} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 20 },
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 10 },
  subtitle: { textAlign: "center", marginBottom: 20 },
  input: { borderWidth: 1, borderColor: "#ccc", padding: 10, borderRadius: 5, marginBottom: 20 },
});

export default PasswordResetScreen;
