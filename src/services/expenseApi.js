const BASE_URL = "https://your-backend-api.com/api"; // Replace with your actual API endpoint

// Add Expense: Handles manual input and receipt upload
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
    const response = await fetch(`${BASE_URL}/expenses`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error adding expense:", error);
    throw error;
  }
};

// Get Expenses: Fetches all expense records
export const getExpenses = async () => {
  try {
    const response = await fetch(`${BASE_URL}/expenses`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    const data = await response.json();
    return data.expenses || [];
  } catch (error) {
    console.error("Error fetching expenses:", error);
    throw error;
  }
};
