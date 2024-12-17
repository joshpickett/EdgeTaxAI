import * as Notifications from "expo-notifications";
import Constants from "expo-constants";
import firebase from "./firebaseConfig";

// Request permission for notifications and get FCM token
export const registerForPushNotifications = async () => {
  let token;

  if (Constants.isDevice) {
    // Ask for permission to send notifications
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

    // Retrieve the Expo Push Token
    token = (await Notifications.getExpoPushTokenAsync()).data;
    console.log("Expo Push Token:", token);

    // Optional: Send the token to Firebase Cloud Messaging (FCM)
    const messaging = firebase.messaging();
    messaging
      .getToken()
      .then((fcmToken) => {
        console.log("FCM Token:", fcmToken);
      })
      .catch((error) => {
        console.error("Error getting FCM Token:", error);
      });
  } else {
    alert("Push notifications are not supported on simulators.");
  }

  return token;
};

// Schedule a notification (example: 10 seconds from now)
export const scheduleLocalNotification = async (title, body) => {
  await Notifications.scheduleNotificationAsync({
    content: {
      title,
      body,
    },
    trigger: { seconds: 10 }, // Trigger after 10 seconds
  });
};
