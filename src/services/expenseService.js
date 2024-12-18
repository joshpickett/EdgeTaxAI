const BASE_URL = "https://your-backend-api.com/api/expenses"; // Replace with your backend URL

// Add Expense: Supports manual input and receipt upload
export const addExpense = async (description, amount, category, date, receiptFile) => {
  const formData = new FormData();
  formData.append("description", description);
  formData.append("amount", amount);
  formData.append("category", category);
  formData.append("date", date);
  if (receiptFile) {
    formData.append("receipt", {
      uri: receiptFile.uri,
      name: receiptFile.fileName || "receipt.jpg",
      type: receiptFile.mimeType || "image/jpeg",
    });
  }

  try {
    const response = await fetch(`${BASE_URL}/add`, {
      method: "POST",
      body: formData,
    });
    return await response.json();
  } catch (error) {
    console.error("Error adding expense:", error.message);
    throw error;
  }
};

// List Expenses for a User
export const listExpenses = async (userId) => {
  try {
    const response = await fetch(`${BASE_URL}/list/${userId}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    return await response.json();
  } catch (error) {
    console.error("Error listing expenses:", error.message);
    throw error;
  }
};

// Edit Expense
export const editExpense = async (expenseId, updatedExpense) => {
  try {
    const response = await fetch(`${BASE_URL}/edit/${expenseId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedExpense),
    });
    return await response.json();
  } catch (error) {
    console.error("Error editing expense:", error.message);
    throw error;
  }
};

// Delete Expense
export const deleteExpense = async (expenseId) => {
  try {
    const response = await fetch(`${BASE_URL}/delete/${expenseId}`, {
      method: "DELETE",
    });
    return await response.json();
  } catch (error) {
    console.error("Error deleting expense:", error.message);
    throw error;
  }
};

// Fetch All Expenses (General)
export const getExpenses = async () => {
  try {
    const response = await fetch(`${BASE_URL}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    return await response.json();
  } catch (error) {
    console.error("Error fetching all expenses:", error.message);
    throw error;
  }
};
