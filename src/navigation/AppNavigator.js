import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

// Screens
import LoginScreen from "../screens/LoginScreen";
import SignupScreen from "../screens/SignupScreen";
import PasswordResetScreen from "../screens/PasswordResetScreen";
import DashboardScreen from "../screens/DashboardScreen";
import MileageTrackingScreen from "../screens/MileageTrackingScreen";
import ReportsScreen from "../screens/ReportsScreen";
import ExpensesScreen from "../screens/ExpensesScreen";
import BankIntegrationScreen from "../screens/BankIntegrationScreen"; // New Bank Integration Screen

const Stack = createNativeStackNavigator();

const AppNavigator = () => {
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
        <Stack.Screen
          name="PasswordReset"
          component={PasswordResetScreen}
          options={{ title: "Reset Password" }}
        />

        {/* Main App Screens */}
        <Stack.Screen
          name="Dashboard"
          component={DashboardScreen}
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
          component={BankIntegrationScreen} // New Screen
          options={{ title: "Bank Integration" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
