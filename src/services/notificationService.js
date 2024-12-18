import * as Notifications from "expo-notifications";
import Constants from "expo-constants";
import firebase from "firebase/app";
import "firebase/messaging";

// Request permission and set up push notifications
export const registerForPushNotifications = async () => {
  try {
    if (!Constants.isDevice) {
      alert("Push notifications are only supported on physical devices.");
      return;
    }

    // Request notification permissions
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== "granted") {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== "granted") {
      alert("Failed to get push notification permissions!");
      return;
    }

    // Get Expo Push Token
    const expoPushToken = (await Notifications.getExpoPushTokenAsync()).data;
    console.log("Expo Push Token:", expoPushToken);

    // Get Firebase Cloud Messaging (FCM) Token
    const fcmToken = await firebase.messaging().getToken();
    console.log("FCM Token:", fcmToken);

    return { expoPushToken, fcmToken };
  } catch (error) {
    console.error("Error setting up push notifications:", error.message);
    throw error;
  }
};

// Handle foreground notifications
export const handleForegroundNotifications = () => {
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: false,
    }),
  });

  // Listen for notifications in the foreground
  Notifications.addNotificationReceivedListener((notification) => {
    console.log("Foreground Notification Received:", notification);
  });

  Notifications.addNotificationResponseReceivedListener((response) => {
    console.log("Notification Response:", response);
  });
};
