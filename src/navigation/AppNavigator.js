import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

// Screens
import LoginScreen from "../screens/LoginScreen";
import SignupScreen from "../screens/SignupScreen";
import DashboardScreen from "../screens/DashboardScreen";
import PasswordResetScreen from "../screens/PasswordResetScreen";

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
      </Stack.Navigator>
    </NavigationContainer>
  );
};

import MileageTrackingScreen from "../screens/MileageTrackingScreen";

// Add the new screen to your navigator
<Stack.Screen
  name="MileageTracking"
  component={MileageTrackingScreen}
  options={{ title: "Mileage Tracking" }}
/>;


export default AppNavigator;
