const BASE_URL = "https://your-backend-api.com/api/reports"; // Replace with actual backend URL

// Centralized Fetch Function
const fetchWithErrorHandling = async (url, options = {}) => {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Something went wrong.");
    }

    return await response.json();
  } catch (error) {
    console.error(`Error in fetch request (${url}):`, error.message);
    throw error;
  }
};

// Fetch Dashboard Data
export const fetchDashboardData = async () => {
  try {
    const [taxData, incomeData, expenseData, planningData] = await Promise.all([
      fetchTaxSummary(),
      fetchIncomeData(),
      fetchExpenseData(),
      fetchPlanningData()
    ]);

    return {
      taxData,
      incomeData,
      expenseData,
      planningData
    };
  } catch (error) {
    console.error("Error fetching dashboard data:", error);
    throw error;
  }
};

// Fetch IRS-ready reports
export const fetchIRSReports = async (userId) => {
  try {
    const url = `${BASE_URL}/irs/${userId}`;
    return await fetchWithErrorHandling(url);
  } catch (error) {
    throw new Error("Failed to fetch IRS-ready reports. Please try again.");
  }
};

// Fetch expense breakdown reports
export const fetchExpenseData = async () => {
  try {
    const url = `${BASE_URL}/expenses/summary`;
    return await fetchWithErrorHandling(url);
  } catch (error) {
    throw new Error("Failed to fetch expense reports");
  }
};

// Fetch custom reports with filters (Start Date, End Date, Category)
export const fetchCustomReports = async (userId, filters) => {
  const { startDate, endDate, category } = filters;

  // Input Validation
  if (!startDate || !endDate) {
    throw new Error("Start date and end date are required.");
  }

  try {
    const url = `${BASE_URL}/custom/${userId}`;
    const options = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start_date: startDate,
        end_date: endDate,
        category: category || "", // Optional
      }),
    };

    return await fetchWithErrorHandling(url, options);
  } catch (error) {
    throw new Error("Failed to fetch custom reports. Please check your filters.");
  }
};
