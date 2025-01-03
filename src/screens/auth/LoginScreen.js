/ src/screens/LoginScreen.tsx

import { UnifiedAuthService } from 'shared/services/unifiedAuthService';

const authService = UnifiedAuthService.getInstance();

const LoginScreen = () => {
  const handleLogin = async (credentials) => {
    try {
      await authService.login(credentials);
      // Handle success
    } catch (error) {
      // Handle error
    }
  };

  // Rest of the component
};