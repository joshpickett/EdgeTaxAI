import { apiClient } from './apiClient';
import { offlineManager } from './offlineManager';
import { cacheManager } from './cacheManager';
import { validateReportData } from '../utils/validation';
import { ReportGenerationError, ReportValidationError } from '../types/errors';

class SharedReportingService {
  constructor() {
    this.reportTypes = {
      TAX_SUMMARY: 'tax_summary',
      QUARTERLY: 'quarterly',
      EXPENSE: 'expense',
      INCOME: 'income',
      CUSTOM: 'custom'
    };
    this.cacheManager = cacheManager;
  }

  async generateReport(type, params = {}) {
    try {
      // Validate report parameters
      const validation = validateReportData(params);
      if (!validation.isValid) {
        throw new ReportValidationError(validation.errors.join(', '), 'VALIDATION_ERROR');
      }

      // Check cache first
      const cacheKey = `${type}_${JSON.stringify(params)}`;
      const cachedData = await this.cacheManager.get(cacheKey);
      if (cachedData) {
        return cachedData;
      }

      const endpoint = `/reports/${type}`;
      const response = await apiClient.post(endpoint, params);
      
      // Cache the response
      await this.cacheManager.set(cacheKey, response.data);
      return response.data;
    } catch (error) {
      if (!navigator.onLine) {
        await offlineManager.queueOperation({
          type: 'GENERATE_REPORT',
          data: { reportType: type, params }
        });
        return null;
      }
      throw new ReportGenerationError(error.message, 'REPORT_GENERATION_ERROR');
    }
  }

  async fetchDashboardData() {
    try {
      const [taxData, incomeData, expenseData, planningData] = await Promise.all([
        this.getTaxSummary(),
        this.getIncomeData(),
        this.getExpenseData(),
        this.getPlanningData()
      ]);

      return {
        taxData,
        incomeData,
        expenseData,
        planningData
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }

  async getTaxSummary() {
    return this.generateReport(this.reportTypes.TAX_SUMMARY);
  }

  async getIncomeData() {
    return this.generateReport(this.reportTypes.INCOME);
  }

  async getExpenseData() {
    return this.generateReport(this.reportTypes.EXPENSE);
  }

  async getPlanningData() {
    return this.generateReport('planning');
  }

  async exportReport(type, format, params = {}) {
    try {
      const response = await apiClient.post(`/reports/export/${type}`, {
        format,
        ...params
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting report:', error);
      throw error;
    }
  }
}

export const sharedReportingService = new SharedReportingService();
