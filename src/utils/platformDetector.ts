export class PlatformDetector {
  getCurrentPlatform(): string {
    if (this.isMobile()) {
      return 'mobile';
    }
    return 'web';
  }

  private isMobile(): boolean {
    if (typeof window === 'undefined') return false;
    
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i
      .test(navigator.userAgent);
  }

  getDeviceCapabilities(): Record<string, boolean> {
    return {
      hasCamera: this.checkCameraSupport(),
      hasFileSystem: this.checkFileSystemSupport(),
      hasOfflineSupport: this.checkOfflineSupport(),
      hasHighPerformance: this.checkPerformanceSupport()
    };
  }

  private checkCameraSupport(): boolean {
    return !!(navigator?.mediaDevices?.getUserMedia);
  }

  private checkFileSystemSupport(): boolean {
    return 'showOpenFilePicker' in window;
  }

  private checkOfflineSupport(): boolean {
    return 'serviceWorker' in navigator;
  }

  private checkPerformanceSupport(): boolean {
    return 'performance' in window;
  }
}
