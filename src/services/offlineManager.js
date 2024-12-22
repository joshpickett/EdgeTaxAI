import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

class OfflineManager {
  constructor() {
    this.syncQueue = [];
    this.isOnline = true;
    this.setupNetworkListener();
  }

  setupNetworkListener() {
    NetInfo.addEventListener(state => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected;
      
      if (wasOffline && this.isOnline) {
        this.processSyncQueue();
      }
    });
  }

  async queueOperation(operation) {
    try {
      this.syncQueue.push(operation);
      await AsyncStorage.setItem('syncQueue', JSON.stringify(this.syncQueue));
      
      if (this.isOnline) {
        await this.processSyncQueue();
      }
    } catch (error) {
      console.error('Error queuing operation:', error);
    }
  }

  async processSyncQueue() {
    while (this.syncQueue.length > 0 && this.isOnline) {
      const operation = this.syncQueue[0];
      try {
        await operation.execute();
        this.syncQueue.shift();
        await AsyncStorage.setItem('syncQueue', JSON.stringify(this.syncQueue));
      } catch (error) {
        console.error('Error processing sync queue:', error);
        break;
      }
    }
  }

  async loadSyncQueue() {
    try {
      const queue = await AsyncStorage.getItem('syncQueue');
      if (queue) {
        this.syncQueue = JSON.parse(queue);
      }
    } catch (error) {
      console.error('Error loading sync queue:', error);
    }
  }
}

export const offlineManager = new OfflineManager();
