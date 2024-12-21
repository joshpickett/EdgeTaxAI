import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Alert } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";

// Screens
import LoginScreen from "../screens/LoginScreen";
import SignupScreen from "../screens/SignupScreen";
import DashboardScreen from "../screens/DashboardScreen";
import MileageTrackingScreen from "../screens/MileageTrackingScreen";
import ReportsScreen from "../screens/ReportsScreen";
import ExpensesScreen from "../screens/ExpensesScreen";
import BankIntegrationScreen from "../screens/BankIntegrationScreen";
import TaxReminderScreen from "../screens/TaxReminderScreen";
import ProfileScreen from "../screens/ProfileScreen";
import GigPlatformScreen from "../screens/GigPlatformScreen";

// Services
import { logoutUser } from "../services/api";

const Stack = createNativeStackNavigator();

const AppNavigator = () => {
  // Logout Logic
  const handleLogout = async (navigation) => {
    try {
      await logoutUser(); // Clears user session and tokens
      await AsyncStorage.removeItem("userToken"); // Remove token locally
      Alert.alert("Success", "You have been logged out.");
      navigation.reset({
        index: 0,
        routes: [{ name: "Login" }],
      });
    } catch (error) {
      Alert.alert("Error", "Failed to log out. Please try again.");
    }
  };

  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        {/* Authentication Screens */}
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="Signup"
          component={SignupScreen}
          options={{ title: "Sign Up" }}
        />

        {/* Main App Screens */}
        <Stack.Screen
          name="Dashboard"
          component={({ navigation }) => (
            <DashboardScreen
              onLogout={() => handleLogout(navigation)} // Pass Logout Function
            />
          )}
          options={{ title: "Dashboard" }}
        />
        <Stack.Screen
          name="MileageTracking"
          component={MileageTrackingScreen}
          options={{ title: "Mileage Tracking" }}
        />
        <Stack.Screen
          name="Expenses"
          component={ExpensesScreen}
          options={{ title: "Manage Expenses" }}
        />
        <Stack.Screen
          name="Reports"
          component={ReportsScreen}
          options={{ title: "Reports" }}
        />
        <Stack.Screen
          name="BankIntegration"
          component={BankIntegrationScreen}
          options={{ title: "Bank Integration" }}
        />
        <Stack.Screen
          name="TaxReminder"
          component={TaxReminderScreen}
          options={{ title: "Tax Reminders" }}
        />
        <Stack.Screen
          name="Profile"
          component={ProfileScreen}
          options={{ title: "User Profile" }}
        />
        <Stack.Screen
          name="GigPlatforms"
          component={GigPlatformScreen}
          options={{ title: "Manage Gig Platforms" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
