import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiClient } from './apiClient';
import { offlineManager } from './offlineManager';

class DataSyncService {
  constructor() {
    this.syncInProgress = false;
    this.lastSyncTime = null;
    this.syncInterval = 1800000; // 30 minutes
  }

  async startSync() {
    if (this.syncInProgress) return;
    
    try {
      this.syncInProgress = true;
      
      // Sync all data types
      await Promise.all([
        this.syncExpenses(),
        this.syncIncome(),
        this.syncMileage(),
        this.syncReceipts()
      ]);

      this.lastSyncTime = new Date();
      await this.updateSyncStatus();
    } catch (error) {
      console.error('Sync error:', error);
      throw error;
    } finally {
      this.syncInProgress = false;
    }
  }

  async syncExpenses() {
    const localExpenses = await this.getLocalExpenses();
    const serverExpenses = await apiClient.getExpenses();
    
    const mergedExpenses = this.mergeData(localExpenses, serverExpenses);
    await this.updateLocalExpenses(mergedExpenses);
    await apiClient.updateExpenses(mergedExpenses);
  }

  async syncIncome() {
    const localIncome = await this.getLocalIncome();
    const serverIncome = await apiClient.getIncome();
    
    const mergedIncome = this.mergeData(localIncome, serverIncome);
    await this.updateLocalIncome(mergedIncome);
    await apiClient.updateIncome(mergedIncome);
  }

  async syncMileage() {
    const localMileage = await this.getLocalMileage();
    const serverMileage = await apiClient.getMileage();
    
    const mergedMileage = this.mergeData(localMileage, serverMileage);
    await this.updateLocalMileage(mergedMileage);
    await apiClient.updateMileage(mergedMileage);
  }

  async syncReceipts() {
    const localReceipts = await this.getLocalReceipts();
    
    for (const receipt of localReceipts) {
      if (!receipt.synced) {
        await this.uploadReceipt(receipt);
      }
    }
  }

  private mergeData(local, server) {
    return server.map(serverItem => {
      const localItem = local.find(item => item.id === serverItem.id);
      return localItem?.lastModified > serverItem.lastModified
        ? localItem
        : serverItem;
    });
  }

  private async updateSyncStatus() {
    const status = {
      lastSync: this.lastSyncTime,
      platform: Platform.OS,
      version: '1.0'
    };
    
    await AsyncStorage.setItem('syncStatus', JSON.stringify(status));
  }

  async getSyncStatus() {
    const status = await AsyncStorage.getItem('syncStatus');
    return status ? JSON.parse(status) : null;
  }
}

export const dataSyncService = new DataSyncService();
