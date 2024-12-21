const BASE_URL = "https://your-backend-api.com/api/auth";

// Send One-Time Password for Signup/Login
export const sendOTP = async (identifier, type = 'signup') => {
  try {
    const response = await fetch(`${BASE_URL}/send-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        identifier,
        type,
        device_info: getDeviceInfo() 
      }),
    });
    return await response.json();
  } catch (error) {
    console.error("Send One-Time Password Error:", error.message);
    throw new Error("Failed to send One-Time Password. Please try again.");
  }
};

// Verify One-Time Password for Signup/Login
export const verifyOTP = async (identifier, otpCode) => {
  try {
    const response = await fetch(`${BASE_URL}/verify-otp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, otp_code: otpCode }),
    });
    return await response.json();
  } catch (error) {
    console.error("Verify One-Time Password Error:", error.message);
    throw new Error("Failed to verify One-Time Password. Please try again.");
  }
};

// Fetch Profile: Retrieves the user's profile details
export const getProfile = async () => {
  try {
    const response = await fetch(`${BASE_URL}/profile`, {
      method: "GET",
      credentials: "include", // Include session cookies
    });
    return await response.json();
  } catch (error) {
    console.error("Fetch Profile Error:", error.message);
    throw new Error("Failed to fetch profile details.");
  }
};

// Update Profile: Updates full name, email, and phone number
export const updateProfile = async (fullName, email, phoneNumber) => {
  try {
    const response = await fetch(`${BASE_URL}/profile`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ full_name: fullName, email, phone_number: phoneNumber }),
    });
    return await response.json();
  } catch (error) {
    console.error("Update Profile Error:", error.message);
    throw new Error("Failed to update profile.");
  }
};
