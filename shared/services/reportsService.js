import { setupSharedPath } from './setup_path';
setupSharedPath();

import { apiClient } from './apiClient';
import { offlineManager } from 'utils/offlineManager';
import { validateReportData } from 'utils/validation';

class ReportsService {
  constructor() {
    this.reportTypes = {
      TAX_SUMMARY: 'tax_summary',
      QUARTERLY: 'quarterly',
      CUSTOM: 'custom'
    };
    this.cacheManager = cacheManager;
  }

  async generateReport(type, params = {}) {
    try {
      // Validate report parameters
      const validation = validateReportData(params);
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '));
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

...rest of the code...
