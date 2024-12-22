import { offlineManager } from './offlineManager';
import { apiClient } from './apiClient';
import NetInfo from '@react-native-community/netinfo';

class SyncService {
  constructor() {
    this.syncInProgress = false;
    this.lastSyncTime = null;
  }

  async syncData() {
    if (this.syncInProgress) {
      return;
    }

    try {
      this.syncInProgress = true;
      const isConnected = await NetInfo.fetch();

      if (!isConnected.isConnected) {
        throw new Error('No internet connection');
      }

      // Sync expenses
      await this.syncExpenses();

      // Sync mileage records
      await this.syncMileage();

      // Sync receipts
      await this.syncReceipts();

      this.lastSyncTime = new Date();
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
    
    // Merge and resolve conflicts
    const mergedExpenses = this.mergeExpenses(localExpenses, serverExpenses);
    
    // Update local storage
    await this.updateLocalExpenses(mergedExpenses);
    
    // Update server
    await apiClient.updateExpenses(mergedExpenses);
  }

  async syncMileage() {
    const localMileage = await this.getLocalMileage();
    const serverMileage = await apiClient.getMileage();
    
    // Merge and resolve conflicts
    const mergedMileage = this.mergeMileage(localMileage, serverMileage);
    
    // Update local storage
    await this.updateLocalMileage(mergedMileage);
    
    // Update server
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

  private mergeExpenses(local, server) {
    // Implement smart merging logic
    return server.map(serverExpense => {
      const localExpense = local.find(e => e.id === serverExpense.id);
      return localExpense?.lastModified > serverExpense.lastModified
        ? localExpense
        : serverExpense;
    });
  }

  private mergeMileage(local, server) {
    // Implement smart merging logic
    return server.map(serverRecord => {
      const localRecord = local.find(r => r.id === serverRecord.id);
      return localRecord?.lastModified > serverRecord.lastModified
        ? localRecord
        : serverRecord;
    });
  }
}

export const syncService = new SyncService();
