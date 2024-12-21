import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, Alert, ScrollView } from "react-native";
import { useDispatch, useSelector } from 'react-redux';
import CustomButton from "../components/CustomButton";
import LoadingState from "../components/LoadingState";
import ErrorMessage from "../components/ErrorMessage";
import InputField from "../components/InputField";
import { signupUser, verifyOTP } from '../store/slices/authSlice';
import { validateEmail, validatePhone } from "../utils/validation";

const SignupScreen = () => {
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [formErrors, setFormErrors] = useState({});
   
  const dispatch = useDispatch();
  const { loading, error, otpSent } = useSelector((state) => state.auth);

  const handleSignup = async () => {
    try {
      // Validate inputs
      const emailError = validateEmail(email);
      const phoneError = validatePhone(phone);
      
      if (emailError && phoneError) {
        setFormErrors({
          email: emailError,
          phone: phoneError
        });
        return;
      }
      
      setFormErrors({});
 
      const identifier = email || phone;
      
      const result = await dispatch(signupUser({ identifier })).unwrap();
      if (result) {
        Alert.alert("Success", "OTP sent for verification");
      }
    } catch (error) {
      Alert.alert("Error", error.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Create Account</Text>

      {loading && <LoadingState />}
      {error && <ErrorMessage message={error} type="error" />}
      
      <InputField
        label="Email"
        placeholder="Enter your email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        error={formErrors.email}
      />

      <InputField
        label="Phone"
        placeholder="Enter your phone number"
        value={phone}
        onChangeText={setPhone}
        keyboardType="phone-pad"
        error={formErrors.phone}
      />

      {/* ...rest of the code... */}

      <Text style={styles.footer}>
        Don't have an account? Login
      </Text>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  footer: {
    marginTop: 20,
    textAlign: 'center',
  },
});

export default SignupScreen;
