// Import Firebase SDK
import firebase from "firebase/app";
import "firebase/messaging"; // For push notifications (optional for Expo)

// Your Firebase project configuration
const firebaseConfig = {
  apiKey: "AIzaSyDv4ZWR97IVnIbE8TyYBZXGzzlJ-cGwG58",
  authDomain: "edgetaxai.firebaseapp.com",
  projectId: "edgetaxai",
  storageBucket: "edgetaxai.firebasestorage.app",
  messagingSenderId: "1099137610113",
  appId: "1:1099137610113:android:cd3acf8792aa782f1ff880",
};

// Initialize Firebase (prevent re-initialization)
if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
} else {
  firebase.app(); // Use existing app instance if already initialized
}

export default firebase;
