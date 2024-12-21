import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, Alert } from "react-native";
import CustomButton from "../components/CustomButton";
import { sendLoginOTP, verifyLoginOTP } from "../services/api"; // Updated API functions

const LoginScreen = ({ navigation }) => {
  const [identifier, setIdentifier] = useState(""); // Email or Phone
  const [otp, setOtp] = useState("");
  const [isOtpSent, setIsOtpSent] = useState(false);

  // Step 1: Send OTP for Login
  const handleSendOTP = async () => {
    if (!identifier) {
      Alert.alert("Error", "Please enter your email or phone number.");
      return;
    }

    try {
      const result = await sendLoginOTP(identifier); // Call the API to send OTP
      if (result && result.message) {
        setIsOtpSent(true);
        Alert.alert("OTP Sent", "Please check your phone or email for the verification code.");
      } else {
        Alert.alert("Error", result?.error || "Unable to send OTP. Please try again.");
      }
    } catch (error) {
      console.error("Send OTP Error:", error);
      Alert.alert("Error", "Unable to send OTP. Please try again.");
    }
  };

  // Step 2: Verify OTP
  const handleVerifyOTP = async () => {
    if (!otp) {
      Alert.alert("Error", "Please enter the OTP sent to your email or phone.");
      return;
    }

    try {
      const result = await verifyLoginOTP(identifier, otp); // Call the API to verify OTP
      if (result && result.message) {
        Alert.alert("Login Successful", "Welcome back!");
        navigation.navigate("Dashboard"); // Navigate to Dashboard
      } else {
        Alert.alert("Error", result?.error || "Invalid or expired OTP.");
      }
    } catch (error) {
      console.error("Verify OTP Error:", error);
      Alert.alert("Error", "Unable to verify OTP. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login with OTP</Text>

      {/* Input for Email or Phone */}
      <TextInput
        style={styles.input}
        placeholder="Email or Phone"
        value={identifier}
        onChangeText={setIdentifier}
        keyboardType="email-address"
        editable={!isOtpSent} // Prevent editing after OTP is sent
      />

      {/* Input for OTP */}
      {isOtpSent && (
        <TextInput
          style={styles.input}
          placeholder="Enter OTP"
          value={otp}
          onChangeText={setOtp}
          keyboardType="numeric"
          maxLength={6}
        />
      )}

      {/* Buttons */}
      {!isOtpSent ? (
        <CustomButton title="Send OTP" onPress={handleSendOTP} />
      ) : (
        <CustomButton title="Verify OTP" onPress={handleVerifyOTP} />
      )}

      {/* Navigation to Signup */}
      <Text
        style={styles.signupText}
        onPress={() => navigation.navigate("Signup")}
      >
        Don't have an account? Sign Up
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: "center" },
  title: { fontSize: 24, fontWeight: "bold", textAlign: "center", marginBottom: 20 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    padding: 10,
    borderRadius: 5,
    marginBottom: 15,
    backgroundColor: "#fff",
  },
  signupText: { textAlign: "center", color: "#007BFF", marginTop: 20 },
});

export default LoginScreen;
