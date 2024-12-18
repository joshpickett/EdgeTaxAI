const BASE_URL = "https://your-backend-api.com/api/auth";

// Login function: accepts email or phone as "identifier"
export const loginUser = async (identifier, password) => {
  try {
    const response = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password }),
    });
    return await response.json();
  } catch (error) {
    console.error("Login Error:", error);
    throw error;
  }
};

// Signup function: accepts email, phone, and password
export const signupUser = async (email, phone, password) => {
  try {
    const response = await fetch(`${BASE_URL}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, phone, password }),
    });
    return await response.json();
  } catch (error) {
    console.error("Signup Error:", error);
    throw error;
  }
};

// Password Reset: Sends a reset link to email or phone
export const resetPassword = async (emailOrPhone) => {
  try {
    const response = await fetch(`${BASE_URL}/password-reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier: emailOrPhone }),
    });
    return await response.json();
  } catch (error) {
    console.error("Reset Password Error:", error);
    throw error;
  }
};
