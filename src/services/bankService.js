const BASE_URL = "https://your-backend-api.com/api/banks";

// Connect Bank Account
export const connectBankAccount = async (userId, bankName) => {
  try {
    const response = await fetch(`${BASE_URL}/connect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, bank_name: bankName }),
    });

    if (!response.ok) throw new Error("Failed to connect bank account.");
    return await response.json();
  } catch (error) {
    console.error("Error connecting bank account:", error.message);
    throw error;
  }
};

// Fetch Bank Transactions
export const getBankTransactions = async (userId) => {
  try {
    const response = await fetch(`${BASE_URL}/transactions/${userId}`);
    if (!response.ok) throw new Error("Failed to fetch transactions.");
    return await response.json();
  } catch (error) {
    console.error("Error fetching bank transactions:", error.message);
    throw error;
  }
};
