import { secureTokenStorage } from '../secureTokenStorage';
import * as SecureStore from 'expo-secure-store';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// Mock dependencies
jest.mock('expo-secure-store');
jest.mock('@react-native-async-storage/async-storage');
jest.mock('react-native/Libraries/Utilities/Platform', () => ({
  OS: 'ios',
  select: jest.fn()
}));

describe('SecureTokenStorage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    console.error = jest.fn();
  });

  describe('Platform-specific Storage', () => {
    it('should use SecureStore on mobile platforms', async () => {
      Platform.OS = 'ios';
      await secureTokenStorage.storeToken('test_key', 'test_value');
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('test_key', 'test_value');
      expect(AsyncStorage.setItem).not.toHaveBeenCalled();
    });

    it('should use AsyncStorage on web platform', async () => {
      Platform.OS = 'web';
      const storage = new secureTokenStorage();
      await storage.storeToken('test_key', 'test_value');
      expect(AsyncStorage.setItem).toHaveBeenCalledWith('test_key', 'test_value');
      expect(SecureStore.setItemAsync).not.toHaveBeenCalled();
    });
  });

  describe('Token Operations', () => {
    describe('storeToken', () => {
      it('should store token successfully', async () => {
        SecureStore.setItemAsync.mockResolvedValueOnce(undefined);
        const result = await secureTokenStorage.storeToken('test_key', 'test_value');
        expect(result).toBe(true);
      });

      it('should handle storage errors', async () => {
        SecureStore.setItemAsync.mockRejectedValueOnce(new Error('Storage error'));
        const result = await secureTokenStorage.storeToken('test_key', 'test_value');
        expect(result).toBe(false);
        expect(console.error).toHaveBeenCalled();
      });

      it('should handle empty or invalid values', async () => {
        const result1 = await secureTokenStorage.storeToken('test_key', '');
        const result2 = await secureTokenStorage.storeToken('test_key', null);
        expect(result1).toBe(true);
        expect(result2).toBe(false);
      });
    });

    describe('getToken', () => {
      it('should retrieve token successfully', async () => {
        SecureStore.getItemAsync.mockResolvedValueOnce('test_value');
        const result = await secureTokenStorage.getToken('test_key');
        expect(result).toBe('test_value');
      });

      it('should handle retrieval errors', async () => {
        SecureStore.getItemAsync.mockRejectedValueOnce(new Error('Retrieval error'));
        const result = await secureTokenStorage.getToken('test_key');
        expect(result).toBeNull();
        expect(console.error).toHaveBeenCalled();
      });

      it('should handle non-existent tokens', async () => {
        SecureStore.getItemAsync.mockResolvedValueOnce(null);
        const result = await secureTokenStorage.getToken('non_existent_key');
        expect(result).toBeNull();
      });
    });

    describe('removeToken', () => {
      it('should remove token successfully', async () => {
        SecureStore.deleteItemAsync.mockResolvedValueOnce(undefined);
        const result = await secureTokenStorage.removeToken('test_key');
        expect(result).toBe(true);
      });

      it('should handle removal errors', async () => {
        SecureStore.deleteItemAsync.mockRejectedValueOnce(new Error('Removal error'));
        const result = await secureTokenStorage.removeToken('test_key');
        expect(result).toBe(false);
        expect(console.error).toHaveBeenCalled();
      });
    });

    describe('clearAllTokens', () => {
      it('should clear all tokens successfully', async () => {
        const mockKeys = ['token_1', 'token_2'];
        SecureStore.getItemAsync.mockResolvedValueOnce(JSON.stringify(mockKeys));
        SecureStore.deleteItemAsync.mockResolvedValue(undefined);

        const result = await secureTokenStorage.clearAllTokens();
        expect(result).toBe(true);
        expect(SecureStore.deleteItemAsync).toHaveBeenCalledTimes(mockKeys.length);
      });

      it('should handle clear errors', async () => {
        SecureStore.getItemAsync.mockRejectedValueOnce(new Error('Clear error'));
        const result = await secureTokenStorage.clearAllTokens();
        expect(result).toBe(false);
        expect(console.error).toHaveBeenCalled();
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle platform changes', async () => {
      Platform.OS = 'android';
      await secureTokenStorage.storeToken('test_key', 'test_value');
      expect(SecureStore.setItemAsync).toHaveBeenCalled();

      Platform.OS = 'web';
      const storage = new secureTokenStorage();
      await storage.storeToken('test_key', 'test_value');
      expect(AsyncStorage.setItem).toHaveBeenCalled();
    });

    it('should handle concurrent operations', async () => {
      const promises = [
        secureTokenStorage.storeToken('key1', 'value1'),
        secureTokenStorage.storeToken('key2', 'value2'),
        secureTokenStorage.getToken('key1'),
        secureTokenStorage.removeToken('key2')
      ];
      await expect(Promise.all(promises)).resolves.toBeDefined();
    });

    it('should handle special characters in keys and values', async () => {
      const specialKey = '!@#$%^&*()_+';
      const specialValue = '{}[]"\'';
      await secureTokenStorage.storeToken(specialKey, specialValue);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith(specialKey, specialValue);
    });

    it('should handle very large tokens', async () => {
      const largeValue = 'a'.repeat(1000000);
      await secureTokenStorage.storeToken('large_key', largeValue);
      expect(SecureStore.setItemAsync).toHaveBeenCalledWith('large_key', largeValue);
    });
  });
});
