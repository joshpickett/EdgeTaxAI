import AsyncStorage from '@react-native-async-storage/async-storage';
import { dataSyncService } from './dataSyncService';

class OfflineManager {
  constructor() {
    this.operationQueue = [];
    this.syncInProgress = false;
    this.maxRetries = 3;
    this.retryDelay = 1000; // 1 second
  }

  // ...rest of the code...

  createOperation(operationData) {
    const operation = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      retryCount: 0,
      ...operationData
    };
    
    // ...rest of the code...

    return operation;
  }

  async retryOperation(operation) {
    if (operation.retryCount >= this.maxRetries) {
      console.error(`Operation ${operation.id} failed after ${this.maxRetries} attempts`);
      return false;
    }

    operation.retryCount++;
    await new Promise(resolve => setTimeout(resolve, this.retryDelay * operation.retryCount));
    
    try {
      await operation.execute();
      return true;
    } catch (error) {
      console.error(`Retry ${operation.retryCount} failed for operation ${operation.id}:`, error);
      return false;
    }
  }

  // ...rest of the code...
}
