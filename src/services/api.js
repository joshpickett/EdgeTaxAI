const BASE_URL = "https://your-backend-api.com/api";

export const loginUser = async (identifier, password) => {
  try {
    const response = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password }), // identifier can be email or phone
    });
    return await response.json();
  } catch (error) {
    console.error("Login Error:", error);
    throw error;
  }
};

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
