const BASE_URL = "https://your-backend-api.com/api";

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
// Add expense (manual input or OCR)
export const addExpense = async (description, amount, category, date, receiptFile) => {
    const formData = new FormData();
    formData.append("description", description);
    formData.append("amount", amount);
    formData.append("category", category);
    formData.append("date", date);
    if (receiptFile) {
      formData.append("receipt", {
        uri: receiptFile.uri,
        name: receiptFile.name,
        type: receiptFile.type,
      });
    }
  
    try {
      const response = await fetch(`${BASE_URL}/expenses`, {
        method: "POST",
        body: formData,
      });
      return await response.json();
    } catch (error) {
      console.error("Add Expense Error:", error);
      throw error;
    }
  };
  
  // Fetch all expenses
  export const getExpenses = async () => {
    try {
      const response = await fetch(`${BASE_URL}/expenses`);
      return await response.json();
    } catch (error) {
      console.error("Fetch Expenses Error:", error);
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
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error resetting password:", error);
    throw error;
  }
};

  