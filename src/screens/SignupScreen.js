import React, { useState } from "react";
import { View, Text, StyleSheet, Alert } from "react-native";
import InputField from "../components/InputField";
import CustomButton from "../components/CustomButton";
import { sendSignupOTP, verifySignupOTP } from "../services/api";
import { validateEmail, validatePhone } from "../utils/validation";

const SignupScreen = ({ navigation }) => {
  const [identifier, setIdentifier] = useState(""); // Email or phone number
  const [otp, setOtp] = useState("");
  const [isOtpSent, setIsOtpSent] = useState(false); // Tracks if OTP has been sent
  const [errors, setErrors] = useState({});

  // Step 1: Send OTP for Signup
  const handleSendOTP = async () => {
    // Clear previous errors
    setErrors({});
    
    // Validate input
    const emailError = validateEmail(identifier);
    const phoneError = validatePhone(identifier);
    
    if (emailError && phoneError) {
      setErrors({ identifier: "Please enter a valid email or phone number" });
      return;
    }

    try {
      const result = await sendSignupOTP(identifier); // Call API to send OTP
      if (result.success) {
        setIsOtpSent(true);
        Alert.alert("OTP Sent", "Please check your email or phone for the OTP.");
      } else {
        Alert.alert("Error", result.message || "Unable to send OTP.");
      }
    } catch (error) {
      console.error("Send OTP Error:", error);
      Alert.alert("Error", "Failed to send OTP. Please try again.");
    }
  };

  // Step 2: Verify OTP
  const handleVerifyOTP = async () => {
    if (!otp) {
      Alert.alert("Error", "Please enter the OTP.");
      return;
    }

    try {
      const result = await verifySignupOTP(identifier, otp); // Call API to verify OTP
      if (result.success) {
        Alert.alert("Signup Successful!", "Your account has been created.");
        navigation.navigate("Login"); // Redirect to Login
      } else {
        Alert.alert("Error", result.message || "Invalid or expired OTP.");
      }
    } catch (error) {
      console.error("Verify OTP Error:", error);
      Alert.alert("Error", "Failed to verify OTP. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sign Up</Text>

      {/* Input for Email or Phone */}
      <InputField
        label="Email or Phone Number"
        placeholder="Enter your email or phone number"
        value={identifier}
        onChangeText={setIdentifier}
        keyboardType="email-address"
        editable={!isOtpSent} // Prevent editing after OTP is sent
        error={errors.identifier}
      />

      {/* OTP Input */}
      {isOtpSent && (
        <InputField
          label="OTP Code"
          placeholder="Enter the OTP"
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

      {/* Navigation to Login */}
      <Text style={styles.loginText} onPress={() => navigation.navigate("Login")}>
        Already have an account? Login
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: "center" },
  title: { fontSize: 24, fontWeight: "bold", marginBottom: 20, textAlign: "center" },
  loginText: { marginTop: 15, textAlign: "center", color: "#007BFF" },
});

export default SignupScreen;
