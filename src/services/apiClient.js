import axios from 'axios';

class APIClient {
  constructor(baseURL = process.env.API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Add request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => this.handleAPIError(error)
    );
  }

  handleAPIError(error) {
    const customError = {
      message: error.response?.data?.message || 'An unexpected error occurred',
      status: error.response?.status,
      data: error.response?.data,
    };
    return Promise.reject(customError);
  }

  // Authentication endpoints
  async login(credentials) {
    return this.client.post('/auth/login', credentials);
  }

  async signup(userData) {
    return this.client.post('/auth/signup', userData);
  }

  async verifyOneTimePassword(data) {
    return this.client.post('/auth/verify-otp', data);
  }

  // Expense endpoints
  async getExpenses(params) {
    return this.client.get('/expenses', { params });
  }

  async addExpense(expenseData) {
    return this.client.post('/expenses', expenseData);
  }

  async updateExpense(id, expenseData) {
    return this.client.put(`/expenses/${id}`, expenseData);
  }

  // Reports endpoints
  async generateReport(params) {
    return this.client.post('/reports/generate', params);
  }

  // Tax optimization endpoints
  async getTaxSavings(data) {
    return this.client.post('/tax-optimization/analyze', data);
  }
}

export const apiClient = new APIClient();
