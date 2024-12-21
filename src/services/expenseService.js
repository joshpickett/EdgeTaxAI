const BASE_URL = "http://localhost:5000/api/expenses"; // Replace with your backend URL

// Fetch Expenses
export const fetchExpenses = async () => {
  try {
    const response = await fetch(`${BASE_URL}/list`);
    if (!response.ok) {
      throw new Error("Failed to fetch expenses.");
    }
    const data = await response.json();
    return data.expenses;
  } catch (error) {
    console.error("Error fetching expenses:", error.message);
    throw error;
  }
};

// Add New Expense
export const addExpense = async (description, amount, category, date) => {
  try {
    const response = await fetch(`${BASE_URL}/add`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        description,
        amount: parseFloat(amount),
        category,
        date,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to add expense.");
    }

    return await response.json();
  } catch (error) {
    console.error("Error adding expense:", error.message);
    throw error;
  }
};

// Edit Existing Expense
export const editExpense = async (id, updatedValues) => {
  try {
    const response = await fetch(`${BASE_URL}/edit/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedValues),
    });

    if (!response.ok) {
      throw new Error("Failed to edit expense.");
    }

    return await response.json();
  } catch (error) {
    console.error("Error editing expense:", error.message);
    throw error;
  }
};

// Delete Expense
export const deleteExpense = async (id) => {
  try {
    const response = await fetch(`${BASE_URL}/delete/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("Failed to delete expense.");
    }

    return await response.json();
  } catch (error) {
    console.error("Error deleting expense:", error.message);
    throw error;
  }
};

// Categorize Expense (AI Integration)
export const categorizeExpense = async (description) => {
  try {
    const response = await fetch(`${BASE_URL}/categorize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description }),
    });

    if (!response.ok) {
      throw new Error("Failed to categorize expense.");
    }

    const data = await response.json();
    return data.category || "Uncategorized";
  } catch (error) {
    console.error("Error categorizing expense:", error.message);
    return "Uncategorized";
  }
};

