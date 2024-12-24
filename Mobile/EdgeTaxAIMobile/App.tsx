import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { Provider, useSelector } from 'react-redux';
import { store } from './src/store';
import AppNavigator from './src/navigation/AppNavigator';
import { colors } from './src/styles/tokens';
import { sharedStyles } from './src/styles/shared';
import {
  SafeAreaView,
  StatusBar,
  useColorScheme,
  View,
} from 'react-native';
import ErrorBoundary from './src/components/ErrorBoundary';
import LoadingOverlay from './src/components/LoadingOverlay';
import { useAuth } from './src/hooks/useAuth';

function App(): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';
  const [isLoading, setIsLoading] = React.useState(true);
  const { initializeAuth } = useAuth();

  React.useEffect(() => {
    const initialize = async () => {
      await initializeAuth();
      setIsLoading(false);
    };
    initialize();
  }, []);

  const backgroundStyle = {
    backgroundColor: isDarkMode ? colors.darkMode.background.default : colors.grey[50],
    flex: 1,
  };

  const barStyle = isDarkMode ? 'light-content' : 'dark-content';

  return (
    <Provider store={store}>
      <NavigationContainer>
        <ErrorBoundary>
          <SafeAreaView style={[backgroundStyle, sharedStyles.safeArea]}>
            <StatusBar
              barStyle={barStyle}
              backgroundColor={backgroundStyle.backgroundColor}
            />
            {isLoading && <LoadingOverlay />}
            <View style={[backgroundStyle, { flex: 1 }]} testID="app-root">
              <AppNavigator />
            </View>
          </SafeAreaView>
        </ErrorBoundary>
      </NavigationContainer>
    </Provider>
  );
}

export default App;
