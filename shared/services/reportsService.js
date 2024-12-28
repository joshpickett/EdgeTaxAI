import { setupSharedPath } from './setup_path';
setupSharedPath();

import { REPORT_TYPES, REPORT_CONFIGS, CACHE_KEYS } from '../config/reportConfig';
import { apiClient } from './apiClient';
import { validateReportData } from '../utils/validation';
import { logger } from '../utils/logger';

export class ReportsService {
  constructor() {
    this.reportTypes = REPORT_TYPES;
    this.configs = REPORT_CONFIGS;
    this.cacheManager = cacheManager;
    this.logger = logger;
  }

  async validateData(params, rules) {
    const errors = [];
    for (const [field, rule] of Object.entries(rules)) {
      if (rule.required && !params[field]) {
        errors.push(`${field} is required`);
      } else if (params[field] && !rule.validate(params[field])) {
        errors.push(`${field} is invalid`);
      }
    }
    return { isValid: errors.length === 0, errors };
  }

  validateReportConfig(type, params) {
    const config = this.configs[type];
    if (!config) {
      throw new Error(`Invalid report type: ${type}`);
    }
    return validateReportData(params, config.validationRules);
  }
  
  async generateTaxSummary(params) {
    return this.generateReport(REPORT_TYPES.TAX_SUMMARY, params);
  }

  async generateQuarterlyReport(params) {
    return this.generateReport(REPORT_TYPES.QUARTERLY, params);
  }

  async getCachedReport(type, params) {
    const cacheKey = CACHE_KEYS.getReportCacheKey(type, params);
    try {
      const cachedData = await this.cacheManager.get(cacheKey);
      if (cachedData) {
        this.logger.debug(`Cache hit for ${type} report`);
        return cachedData;
      }
    } catch (error) {
      this.logger.error(`Cache error for ${type} report: ${error.message}`);
    }
    return null;
  }

  async generateReport(type, params = {}) {
    try {
      const validation = this.validateReportConfig(type, params);
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '));
      }

      const cacheKey = CACHE_KEYS.getReportCacheKey(type, params);
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
