import { 
  registerForPushNotifications, 
  handleForegroundNotifications 
} from '../notificationService';
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';
import firebase from 'firebase/app';

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
  });

  describe('registerForPushNotifications', () => {
    it('successfully registers for push notifications', async () => {
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
    });

    it('requests permissions if not granted', async () => {
      Notifications.getPermissionsAsync.mockResolvedValueOnce({ status: 'undetermined' });
      Notifications.requestPermissionsAsync.mockResolvedValueOnce({ status: 'granted' });

      await registerForPushNotifications();

      expect(Notifications.requestPermissionsAsync).toHaveBeenCalled();
    });

    it('handles permission denial', async () => {
      Notifications.getPermissionsAsync.mockResolvedValueOnce({ status: 'denied' });
      Notifications.requestPermissionsAsync.mockResolvedValueOnce({ status: 'denied' });

      const consoleSpy = jest.spyOn(console, 'error');
      await registerForPushNotifications();

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Failed to get push notification permissions')
      );
    });

    it('handles non-device environments', async () => {
      Constants.isDevice = false;
      const result = await registerForPushNotifications();
      expect(result).toBeUndefined();
    });
  });

  describe('handleForegroundNotifications', () => {
    it('sets up notification handler correctly', () => {
      handleForegroundNotifications();

      expect(Notifications.setNotificationHandler).toHaveBeenCalledWith({
        handleNotification: expect.any(Function)
      });
    });

    it('adds notification listeners', () => {
      handleForegroundNotifications();

      expect(Notifications.addNotificationReceivedListener).toHaveBeenCalled();
      expect(Notifications.addNotificationResponseReceivedListener).toHaveBeenCalled();
    });
  });
});
