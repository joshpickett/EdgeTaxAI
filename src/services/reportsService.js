const BASE_URL = "https://your-backend-api.com/api"; // Replace with actual backend URL

// Fetch IRS-ready reports
export const fetchIRSReports = async () => {
  try {
    const response = await fetch(`${BASE_URL}/reports/irs`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching IRS reports:", error);
    throw error;
  }
};

// Fetch expense breakdown reports
export const fetchExpenseReports = async () => {
  try {
    const response = await fetch(`${BASE_URL}/reports/expenses`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching expense reports:", error);
    throw error;
  }
};
