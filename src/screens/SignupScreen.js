import React, { useState } from "react";
import { View, Text, StyleSheet, Alert } from "react-native";
import InputField from "../components/InputField";
import CustomButton from "../components/CustomButton";
import { signupUser } from "../services/api";

const SignupScreen = ({ navigation }) => {
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");

  const handleSignup = async () => {
    try {
      const result = await signupUser(email, phone, password);
      if (result.success) {
        Alert.alert("Signup Successful!", "You can now log in.");
        navigation.navigate("Login");
      } else {
        Alert.alert("Error", result.message || "Could not sign up.");
      }
    } catch (error) {
      Alert.alert("Signup Error", "Unable to sign up. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Sign Up</Text>
      <InputField
        label="Email"
        placeholder="Enter your email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
      />
      <InputField
        label="Phone Number"
        placeholder="Enter your phone number"
        value={phone}
        onChangeText={setPhone}
        keyboardType="phone-pad"
      />
      <InputField
        label="Password"
        placeholder="Enter your password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <CustomButton title="Sign Up" onPress={handleSignup} />
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
