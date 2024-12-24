import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useSelector } from 'react-redux';
import { Alert } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";

// Auth Screens
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

const AppNavigator = ({ onReady }) => {
  const { isAuthenticated } = useSelector(state => state.auth);

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
    <Stack.Navigator>
      {!isAuthenticated ? (
        <Stack.Group screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="Signup" component={SignupScreen} />
        </Stack.Group>
      ) : (
        <Stack.Group>
          <Stack.Screen
            name="Dashboard"
            component={DashboardScreen}
            options={{
              title: "Dashboard",
              headerRight: ({ navigation }) => (
                <LogoutButton onPress={() => handleLogout(navigation)} />
              ),
            }}
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
        </Stack.Group>
      )}
    </Stack.Navigator>
  );
};

export default AppNavigator;
