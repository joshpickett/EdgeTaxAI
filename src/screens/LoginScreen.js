import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet, Alert } from "react-native";
import CustomButton from "../components/CustomButton";
import { loginUser } from "../services/api";

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert("Error", "Please enter both email/phone and password.");
      return;
    }

    try {
      const result = await loginUser(email, password); // Call the API
      if (result && result.user_id) {
        Alert.alert("Login Successful!", "Welcome back.");
        navigation.navigate("Dashboard");
      } else {
        Alert.alert("Error", result?.message || "Invalid credentials.");
      }
    } catch (error) {
      console.error("Login Error:", error);
      Alert.alert("Error", "Unable to log in. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login</Text>

      <TextInput
        style={styles.input}
        placeholder="Email or Phone"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
      />

      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      {/* Forgot Password Link */}
      <Text
        style={styles.forgotPassword}
        onPress={() => navigation.navigate("PasswordReset")}
      >
        Forgot Password?
      </Text>

      <CustomButton title="Login" onPress={handleLogin} />

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
  },
  forgotPassword: { color: "#007BFF", textAlign: "right", marginBottom: 20 },
  signupText: { textAlign: "center", color: "#007BFF", marginTop: 20 },
});

export default LoginScreen;
