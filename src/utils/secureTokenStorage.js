import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

class SecureTokenStorage {
  constructor() {
    this.isSecureStorageAvailable = Platform.OS !== 'web';
  }

  async storeToken(key, value) {
    try {
      if (this.isSecureStorageAvailable) {
        await SecureStore.setItemAsync(key, value);
      } else {
        await AsyncStorage.setItem(key, value);
      }
      return true;
    } catch (error) {
      console.error('Error storing token:', error);
      return false;
    }
  }

  async getToken(key) {
    try {
      if (this.isSecureStorageAvailable) {
        return await SecureStore.getItemAsync(key);
      }
      return await AsyncStorage.getItem(key);
    } catch (error) {
      console.error('Error retrieving token:', error);
      return null;
    }
  }

  async removeToken(key) {
    try {
      if (this.isSecureStorageAvailable) {
        await SecureStore.deleteItemAsync(key);
      } else {
        await AsyncStorage.removeItem(key);
      }
      return true;
    } catch (error) {
      console.error('Error removing token:', error);
      return false;
    }
  }

  async clearAllTokens() {
    try {
      const keys = await this.getAllTokenKeys();
      for (const key of keys) {
        await this.removeToken(key);
      }
      return true;
    } catch (error) {
      console.error('Error clearing tokens:', error);
      return false;
    }
  }

  async getAllTokenKeys() {
    try {
      if (this.isSecureStorageAvailable) {
        // SecureStore doesn't provide a way to list keys
        // You'll need to maintain a separate list of keys
        const keysString = await SecureStore.getItemAsync('token_keys');
        return keysString ? JSON.parse(keysString) : [];
      }
      const keys = await AsyncStorage.getAllKeys();
      return keys.filter(key => key.startsWith('token_'));
    } catch (error) {
      console.error('Error getting token keys:', error);
      return [];
    }
  }
}

export const secureTokenStorage = new SecureTokenStorage();
