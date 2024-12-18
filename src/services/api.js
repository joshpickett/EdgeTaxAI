const BASE_URL = "https://your-backend-api.com/api";

/**
 * Utility function to handle API requests.
 * @param {string} endpoint - API endpoint (relative to BASE_URL).
 * @param {string} method - HTTP method ("GET", "POST", etc.).
 * @param {object} payload - Request body for POST/PUT methods.
 * @param {object} headers - Optional custom headers.
 * @returns {Promise<object>} - Response JSON or error.
 */
export const sendRequest = async (endpoint, method = "GET", payload = null, headers = {}) => {
  const defaultHeaders = { "Content-Type": "application/json" };
  const options = {
    method,
    headers: { ...defaultHeaders, ...headers },
  };

  if (payload) {
    options.body = JSON.stringify(payload);
  }

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
      console.error(`API Error: ${data.error || "Unknown error occurred"}`);
      throw new Error(data.error || "An error occurred. Please try again.");
    }
    return data;
  } catch (error) {
    console.error(`Request Failed (${method} ${endpoint}):`, error.message);
    throw error;
  }
};

/**
 * Validate input fields to ensure no field is empty.
 * @param {object} fields - Object with field names and values.
 * @returns {boolean} - True if all fields are valid, otherwise false.
 */
export const validateFields = (fields) => {
  for (const [key, value] of Object.entries(fields)) {
    if (!value) {
      console.warn(`Validation failed: ${key} is required.`);
      return false;
    }
  }
  return true;
};

/**
 * Login Function: Allows users to log in with email or phone.
 * @param {string} identifier - Email or phone number.
 * @param {string} password - User password.
 */
export const loginUser = async (identifier, password) => {
  if (!validateFields({ identifier, password })) {
    throw new Error("All fields are required.");
  }
  return await sendRequest("/auth/login", "POST", { identifier, password });
};

/**
 * Signup Function: Allows users to sign up with email, phone, and password.
 * @param {string} fullName - Full name of the user.
 * @param {string} email - User email.
 * @param {string} phoneNumber - User phone number.
 * @param {string} password - Password.
 */
export const signupUser = async (fullName, email, phoneNumber, password) => {
  if (!validateFields({ fullName, email, phoneNumber, password })) {
    throw new Error("All fields are required.");
  }
  return await sendRequest("/auth/signup", "POST", {
    full_name: fullName,
    email,
    phone_number: phoneNumber,
    password,
  });
};

/**
 * Reset Password: Sends a reset link to email or phone.
 * @param {string} identifier - Email or phone number.
 */
export const resetPassword = async (identifier) => {
  if (!validateFields({ identifier })) {
    throw new Error("Email or phone number is required.");
  }
  return await sendRequest("/auth/password-reset", "POST", { identifier });
};

/**
 * Add Expense: Upload expense details with optional receipt.
 * @param {object} expenseData - Expense details.
 * @param {object} receiptFile - Optional receipt file (FormData).
 */
export const addExpense = async (expenseData, receiptFile = null) => {
  const formData = new FormData();
  for (const key in expenseData) {
    formData.append(key, expenseData[key]);
  }
  if (receiptFile) {
    formData.append("receipt", receiptFile);
  }

  const options = {
    method: "POST",
    body: formData,
  };

  try {
    const response = await fetch(`${BASE_URL}/expenses`, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Failed to add expense.");
    }
    return data;
  } catch (error) {
    console.error("Add Expense Error:", error.message);
    throw error;
  }
};

/**
 * Fetch Expenses: Retrieves all user expenses.
 */
export const getExpenses = async () => {
  return await sendRequest("/expenses", "GET");
};
 