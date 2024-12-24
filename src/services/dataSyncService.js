import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiClient } from './apiClient';
import { offlineManager } from './offlineManager';
import { EventEmitter } from '../utils/eventEmitter';

class DataSyncService {
  constructor() {
    this.syncInProgress = false;
    this.lastSyncTime = null;
    this.syncInterval = 1800000; // 30 minutes
    this.eventEmitter = new EventEmitter();
  }

  async startSync() {
    if (this.syncInProgress) return;
    
    // Check network connectivity
    if (!navigator.onLine) {
      console.log('Offline - sync postponed');
      return;
    }
    
    try {
      this.syncInProgress = true;
      
      await this.checkPendingOperations();
      // Sync all data types
      await Promise.all([
        this.syncExpenses(),
        this.syncIncome(),
        this.syncMileage(),
        this.syncReceipts(),
        this.syncPlatformData()
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
    
    // Update last sync timestamp for expenses
    await AsyncStorage.setItem('lastExpenseSync', new Date().toISOString());
  }

  async getLocalExpenses() {
    return await offlineManager.getExpenses();
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

  async checkPendingOperations() {
    const pendingOperations = await offlineManager.getPendingOperations();
    if (pendingOperations.length > 0) {
      for (const operation of pendingOperations) {
        try {
          await operation.execute();
          await offlineManager.removeOperation(operation.id);
        } catch (error) {
          console.error('Error executing pending operation:', error);
        }
      }
    }
  }

  private mergeData(local, server) {
    return server.map(serverItem => {
      const localItem = local.find(item => item.id === serverItem.id);
      
      // If item exists in both, compare timestamps
      return localItem?.lastModified > serverItem.lastModified
        ? localItem
        : serverItem;
      
      // Add new items that only exist locally
      const newLocalItems = local.filter(item => 
        !server.some(serverItem => serverItem.id === item.id)
      );
      
      return [...mergedItems, ...newLocalItems];
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

  async syncPlatformData() {
    const platforms = ['uber', 'lyft', 'doordash', 'instacart'];
    for (const platform of platforms) {
      try {
        await apiClient.syncPlatformData(platform);
      } catch (error) {
        console.error(`Error syncing ${platform} data:`, error);
      }
    }
  }

  subscribeSyncStatus(callback) {
    return this.eventEmitter.subscribe('syncStatus', callback);
  }

  unsubscribeSyncStatus(subscriptionId) {
    this.eventEmitter.unsubscribe('syncStatus', subscriptionId);
  }
}

export const dataSyncService = new DataSyncService();
