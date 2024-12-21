import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, Alert } from "react-native";
import { useDispatch, useSelector } from 'react-redux';
import CustomButton from "../components/CustomButton";
import { loginUser, verifyOTP } from '../store/slices/authSlice';
import { RootState } from '../store';
import { validateEmail, validatePhone } from "../utils/validation";

const LoginScreen = ({ navigation }) => {
  const [identifier, setIdentifier] = useState(""); // Email or Phone
  const [otp, setOtp] = useState("");
  const [errors, setErrors] = useState({});
  
  const dispatch = useDispatch();
  const { loading, error, otpSent } = useSelector(
    (state: RootState) => state.auth
  );

  // Validate before sending OTP
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
      const result = await dispatch(loginUser({ identifier })).unwrap();
      if (result) {
        Alert.alert("OTP Sent", "Please check your phone or email for the verification code.");
      } else {
        Alert.alert("Error", "Unable to send OTP. Please try again.");
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
      const result = await dispatch(verifyOTP({ identifier, otp })).unwrap();
      if (result) {
        Alert.alert("Login Successful", "Welcome back!");
        navigation.navigate("Dashboard"); // Navigate to Dashboard
      } else {
        Alert.alert("Error", "Invalid or expired OTP.");
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
        editable={!otpSent} // Prevent editing after OTP is sent
      />
      {errors.identifier && <Text style={styles.errorText}>{errors.identifier}</Text>}

      {/* Input for OTP */}
      {otpSent && (
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
      {!otpSent ? (
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
  errorText: {
    color: '#ff0000',
    fontSize: 12,
    marginTop: -10,
    marginBottom: 10,
  },
  signupText: { textAlign: "center", color: "#007BFF", marginTop: 20 },
});

export default LoginScreen;
