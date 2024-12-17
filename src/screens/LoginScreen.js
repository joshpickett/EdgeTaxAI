import React, { useState } from "react";
import { View, Text, StyleSheet, Alert } from "react-native";
import InputField from "../components/InputField";
import CustomButton from "../components/CustomButton";
import { loginUser } from "../services/api";

const LoginScreen = ({ navigation }) => {
  const [identifier, setIdentifier] = useState(""); // Accepts email or phone
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const result = await loginUser(identifier, password);
      if (result.success) {
        Alert.alert("Login Successful!", "Welcome back!");
        navigation.navigate("Dashboard");
      } else {
        Alert.alert("Error", result.message || "Invalid credentials.");
      }
    } catch (error) {
      Alert.alert("Login Error", "Unable to login. Please try again.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login</Text>
      <InputField
        label="Email or Phone"
        placeholder="Enter email or phone number"
        value={identifier}
        onChangeText={setIdentifier}
        keyboardType="default"
      />
      <InputField
        label="Password"
        placeholder="Enter your password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <CustomButton title="Login" onPress={handleLogin} />
      <Text style={styles.signupText} onPress={() => navigation.navigate("Signup")}>
        Don’t have an account? Sign Up
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: "center" },
  title: { fontSize: 24, fontWeight: "bold", marginBottom: 20, textAlign: "center" },
  signupText: { marginTop: 15, textAlign: "center", color: "#007BFF" },
});

export default LoginScreen;
