import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// Screens
import LoginScreen from '../screens/LoginScreen';
import SignupScreen from '../screens/SignupScreen';
import DashboardScreen from '../screens/DashboardScreen';

// Expense Screens
import AddExpenseScreen from '../screens/expenses/AddExpenseScreen';
import ExpenseDashboardScreen from '../screens/expenses/ExpenseDashboardScreen';

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

        {/* Main Dashboard */}
        <Stack.Screen 
          name="Dashboard" 
          component={DashboardScreen} 
          options={{ title: "Dashboard" }} 
        />

        {/* Expense Tracking Screens */}
        <Stack.Screen 
          name="AddExpense" 
          component={AddExpenseScreen} 
          options={{ title: "Add Expense" }} 
        />
        <Stack.Screen 
          name="ExpenseDashboard" 
          component={ExpenseDashboardScreen} 
          options={{ title: "Expense Dashboard" }} 
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
