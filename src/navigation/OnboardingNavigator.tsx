import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { WelcomeScreen } from '../screens/onboarding/WelcomeScreen';
import { DocumentCollectionScreen } from '../screens/onboarding/DocumentCollectionScreen';
import { PlatformConnectionScreen } from '../screens/onboarding/PlatformConnectionScreen';
import { TaxProfileScreen } from '../screens/onboarding/TaxProfileScreen';
import { OnboardingCompleteScreen } from '../screens/onboarding/OnboardingCompleteScreen';

const Stack = createNativeStackNavigator();

export const OnboardingNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        gestureEnabled: false
      }}
    >
      <Stack.Screen name="Welcome" component={WelcomeScreen} />
      <Stack.Screen name="DocumentCollection" component={DocumentCollectionScreen} />
      <Stack.Screen name="PlatformConnection" component={PlatformConnectionScreen} />
      <Stack.Screen name="TaxProfile" component={TaxProfileScreen} />
      <Stack.Screen name="OnboardingComplete" component={OnboardingCompleteScreen} />
    </Stack.Navigator>
  );
};
