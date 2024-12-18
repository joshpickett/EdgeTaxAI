const BASE_URL = "https://your-backend-api.com/api/expenses"; // Update with actual URL

// Add Expense
export const addExpense = async (expenseData) => {
  const response = await fetch(`${BASE_URL}/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(expenseData),
  });
  return await response.json();
};

// List Expenses
export const listExpenses = async (userId) => {
  const response = await fetch(`${BASE_URL}/list/${userId}`);
  return await response.json();
};

// Edit Expense
export const editExpense = async (expenseId, updatedExpense) => {
  const response = await fetch(`${BASE_URL}/edit/${expenseId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updatedExpense),
  });
  return await response.json();
};

// Delete Expense
export const deleteExpense = async (expenseId) => {
  const response = await fetch(`${BASE_URL}/delete/${expenseId}`, {
    method: "DELETE",
  });
  return await response.json();
};
