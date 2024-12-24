import firebase from 'firebase/app';
import { auth, db } from '../firebaseConfig';

// Mock Firebase
jest.mock('firebase/app', () => ({
  apps: [],
  initializeApp: jest.fn(),
  app: jest.fn(),
  auth: jest.fn(() => ({
    setPersistence: jest.fn(),
    Auth: { Persistence: { LOCAL: 'LOCAL' } }
  })),
  firestore: jest.fn(() => ({
    enablePersistence: jest.fn().mockResolvedValue()
  }))
}));

describe('Firebase Configuration', () => {
  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    // Reset firebase.apps length
    Object.defineProperty(firebase, 'apps', { value: [] });
  });

  describe('Firebase Initialization', () => {
    it('should initialize firebase with correct config', () => {
      // Re-import to trigger initialization
      jest.isolateModules(() => {
        require('../firebaseConfig');
      });

      expect(firebase.initializeApp).toHaveBeenCalledWith(expect.objectContaining({
        apiKey: expect.any(String),
        authDomain: expect.any(String),
        projectId: expect.any(String),
        storageBucket: expect.any(String),
        messagingSenderId: expect.any(String),
        appId: expect.any(String),
        measurementId: expect.any(String)
      }));
    });

    it('should not reinitialize if firebase is already initialized', () => {
      // Mock firebase.apps to simulate already initialized
      Object.defineProperty(firebase, 'apps', { value: [{}] });

      jest.isolateModules(() => {
        require('../firebaseConfig');
      });

      expect(firebase.initializeApp).not.toHaveBeenCalled();
      expect(firebase.app).toHaveBeenCalled();
    });
  });

  describe('Authentication Setup', () => {
    it('should set up authentication persistence', () => {
      jest.isolateModules(() => {
        require('../firebaseConfig');
      });

      expect(auth.setPersistence).toHaveBeenCalledWith(
        firebase.auth.Auth.Persistence.LOCAL
      );
    });
  });

  describe('Firestore Setup', () => {
    it('should enable firestore persistence', () => {
      jest.isolateModules(() => {
        require('../firebaseConfig');
      });

      expect(db.enablePersistence).toHaveBeenCalled();
    });

    it('should handle persistence errors gracefully', async () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation();
      const mockError = new Error('Persistence error');
      
      db.enablePersistence.mockRejectedValueOnce(mockError);

      jest.isolateModules(() => {
        require('../firebaseConfig');
      });

      await new Promise(process.nextTick); // Wait for promise to resolve

      expect(consoleError).toHaveBeenCalledWith(
        'Firestore persistence error:',
        mockError
      );

      consoleError.mockRestore();
    });
  });

  describe('Error Handling', () => {
    it('should handle initialization errors', () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation();
      firebase.initializeApp.mockImplementationOnce(() => {
        throw new Error('Init error');
      });

      expect(() => {
        jest.isolateModules(() => {
          require('../firebaseConfig');
        });
      }).toThrow('Init error');

      consoleError.mockRestore();
    });
  });

  describe('Firebase Export', () => {
    it('should export firebase instance', () => {
      const { default: firebaseInstance } = require('../firebaseConfig');
      expect(firebaseInstance).toBeDefined();
    });

    it('should export auth instance', () => {
      expect(auth).toBeDefined();
    });

    it('should export firestore instance', () => {
      expect(db).toBeDefined();
    });
  });
});
