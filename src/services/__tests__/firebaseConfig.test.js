import firebase from 'firebase/app';
import { auth, db } from '../firebaseConfig';

jest.mock('firebase/app', () => ({
  apps: [],
  initializeApp: jest.fn(),
  app: jest.fn(),
  auth: jest.fn(() => ({
    setPersistence: jest.fn()
  })),
  firestore: jest.fn(() => ({
    enablePersistence: jest.fn().mockResolvedValue()
  }))
}));

describe('Firebase Configuration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes Firebase when no apps exist', () => {
    require('../firebaseConfig');
    expect(firebase.initializeApp).toHaveBeenCalledWith({
      apiKey: expect.any(String),
      authDomain: expect.any(String),
      projectId: expect.any(String),
      storageBucket: expect.any(String),
      messagingSenderId: expect.any(String),
      appId: expect.any(String),
      measurementId: expect.any(String)
    });
  });

  it('uses existing app when already initialized', () => {
    firebase.apps = [{}];
    require('../firebaseConfig');
    expect(firebase.app).toHaveBeenCalled();
    expect(firebase.initializeApp).not.toHaveBeenCalled();
  });

  it('enables persistence for Firestore', () => {
    const mockEnablePersistence = jest.fn().mockResolvedValue();
    firebase.firestore.mockReturnValue({
      enablePersistence: mockEnablePersistence
    });

    require('../firebaseConfig');
    expect(mockEnablePersistence).toHaveBeenCalled();
  });

  it('sets persistence for Authentication', () => {
    const mockSetPersistence = jest.fn();
    firebase.auth.mockReturnValue({
      setPersistence: mockSetPersistence
    });

    require('../firebaseConfig');
    expect(mockSetPersistence).toHaveBeenCalled();
  });
});
