import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';
import firebase from 'firebase/app';
import { registerForPushNotifications, handleForegroundNotifications } from '../notificationService';

// Mock dependencies
jest.mock('expo-notifications');
jest.mock('expo-constants', () => ({
  isDevice: true
}));
jest.mock('firebase/app', () => ({
  messaging: () => ({
    getToken: jest.fn()
  })
}));

describe('NotificationService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    console.error = jest.fn();
    console.log = jest.fn();
  });

  describe('registerForPushNotifications', () => {
    it('should successfully register for push notifications', async () => {
      const mockExpoPushToken = 'expo-push-token';
      const mockFCMToken = 'fcm-token';

      Notifications.getPermissionsAsync.mockResolvedValueOnce({ status: 'granted' });
      Notifications.getExpoPushTokenAsync.mockResolvedValueOnce({ data: mockExpoPushToken });
      firebase.messaging().getToken.mockResolvedValueOnce(mockFCMToken);

      const result = await registerForPushNotifications();

      expect(result).toEqual({
        expoPushToken: mockExpoPushToken,
        fcmToken: mockFCMToken
      });
      expect(Notifications.getPermissionsAsync).toHaveBeenCalled();
      expect(Notifications.getExpoPushTokenAsync).toHaveBeenCalled();
      expect(firebase.messaging().getToken).toHaveBeenCalled();
    });

    it('should request permissions if not already granted', async () => {
      Notifications.getPermissionsAsync.mockResolvedValueOnce({ status: 'undetermined' });
      Notifications.requestPermissionsAsync.mockResolvedValueOnce({ status: 'granted' });
      Notifications.getExpoPushTokenAsync.mockResolvedValueOnce({ data: 'token' });
      firebase.messaging().getToken.mockResolvedValueOnce('fcm-token');

      await registerForPushNotifications();

      expect(Notifications.requestPermissionsAsync).toHaveBeenCalled();
    });

    it('should handle permission denial', async () => {
      Notifications.getPermissionsAsync.mockResolvedValueOnce({ status: 'undetermined' });
      Notifications.requestPermissionsAsync.mockResolvedValueOnce({ status: 'denied' });

      const result = await registerForPushNotifications();

      expect(result).toBeUndefined();
      expect(global.alert).toHaveBeenCalledWith(
        'Failed to get push notification permissions!'
      );
    });

    it('should handle non-device environments', async () => {
      Constants.isDevice = false;

      const result = await registerForPushNotifications();

      expect(result).toBeUndefined();
      expect(global.alert).toHaveBeenCalledWith(
        'Push notifications are only supported on physical devices.'
      );
    });

    it('should handle token generation errors', async () => {
      Notifications.getPermissionsAsync.mockResolvedValueOnce({ status: 'granted' });
      Notifications.getExpoPushTokenAsync.mockRejectedValueOnce(
        new Error('Token generation failed')
      );

      await expect(registerForPushNotifications())
        .rejects.toThrow('Token generation failed');
      expect(console.error).toHaveBeenCalled();
    });
  });

  describe('handleForegroundNotifications', () => {
    it('should set up notification handler with correct configuration', () => {
      handleForegroundNotifications();

      expect(Notifications.setNotificationHandler).toHaveBeenCalledWith({
        handleNotification: expect.any(Function)
      });

      // Test the handler configuration
      const handler = Notifications.setNotificationHandler.mock.calls[0][0];
      return handler.handleNotification().then(result => {
        expect(result).toEqual({
          shouldShowAlert: true,
          shouldPlaySound: true,
          shouldSetBadge: false
        });
      });
    });

    it('should add notification received listener', () => {
      handleForegroundNotifications();

      expect(Notifications.addNotificationReceivedListener).toHaveBeenCalled();
    });

    it('should add notification response listener', () => {
      handleForegroundNotifications();

      expect(Notifications.addNotificationResponseReceivedListener).toHaveBeenCalled();
    });

    it('should handle received notifications correctly', () => {
      const mockNotification = { title: 'Test Notification' };
      let receivedListener;

      Notifications.addNotificationReceivedListener.mockImplementation(listener => {
        receivedListener = listener;
      });

      handleForegroundNotifications();
      receivedListener(mockNotification);

      expect(console.log).toHaveBeenCalledWith(
        'Foreground Notification Received:',
        mockNotification
      );
    });

    it('should handle notification responses correctly', () => {
      const mockResponse = { notification: { title: 'Test Response' } };
      let responseListener;

      Notifications.addNotificationResponseReceivedListener.mockImplementation(listener => {
        responseListener = listener;
      });

      handleForegroundNotifications();
      responseListener(mockResponse);

      expect(console.log).toHaveBeenCalledWith(
        'Notification Response:',
        mockResponse
      );
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty notification data', () => {
      let receivedListener;
      Notifications.addNotificationReceivedListener.mockImplementation(listener => {
        receivedListener = listener;
      });

      handleForegroundNotifications();
      receivedListener({});

      expect(console.log).toHaveBeenCalledWith(
        'Foreground Notification Received:',
        {}
      );
    });

    it('should handle null notification response', () => {
      let responseListener;
      Notifications.addNotificationResponseReceivedListener.mockImplementation(listener => {
        responseListener = listener;
      });

      handleForegroundNotifications();
      responseListener(null);

      expect(console.log).toHaveBeenCalledWith('Notification Response:', null);
    });

    it('should handle permission check errors', async () => {
      Notifications.getPermissionsAsync.mockRejectedValueOnce(
        new Error('Permission check failed')
      );

      await expect(registerForPushNotifications())
        .rejects.toThrow('Permission check failed');
      expect(console.error).toHaveBeenCalled();
    });
  });
});
