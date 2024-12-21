import AsyncStorage from "@react-native-async-storage/async-storage";

const BASE_URL = "https://your-backend-api.com/api/auth"; // Replace with your backend URL

// User Signup
export const signupUser = async (fullName, email, phoneNumber, password) => {
  try {
    const response = await fetch(`${BASE_URL}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: fullName,
        email: email,
        phone_number: phoneNumber,
        password: password,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Failed to sign up.");
    }
    return data; // Returns success message
  } catch (error) {
    console.error("Signup Error:", error.message);
    throw error;
  }
};

// User Login
export const loginUser = async (emailOrPhone, password) => {
  try {
    const response = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: emailOrPhone,
        phone_number: emailOrPhone, // Accept either email or phone
        password: password,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Failed to log in.");
    }

    // Save the user token/session to AsyncStorage
    await AsyncStorage.setItem("userToken", data.user_id.toString());
    return data;
  } catch (error) {
    console.error("Login Error:", error.message);
    throw error;
  }
};

// User Logout
export const logoutUser = async () => {
  try {
    // Call backend logout endpoint
    const response = await fetch(`${BASE_URL}/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Failed to log out.");
    }

    // Clear user session/token from AsyncStorage
    await AsyncStorage.removeItem("userToken");
    return data; // Return success message
  } catch (error) {
    console.error("Logout Error:", error.message);
    throw error;
  }
};

// Get User Token (Session Check)
export const getUserToken = async () => {
  try {
    const token = await AsyncStorage.getItem("userToken");
    return token;
  } catch (error) {
    console.error("Error fetching user token:", error.message);
    throw error;
  }
};
