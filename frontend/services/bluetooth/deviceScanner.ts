/** Device scanner for BLE devices. */

import { BLEManager } from './bleManager';
import { BLEDevice } from '@/types/device';

export class DeviceScanner {
  private bleManager: BLEManager;

  constructor() {
    this.bleManager = new BLEManager();
  }

  /**
   * Scan and connect to Sentry device
   */
  async scanAndConnect(): Promise<BLEDevice | null> {
    await this.bleManager.initialize();
    const devices = await this.bleManager.scanForDevices();

    if (devices.length > 0) {
      // Connect to first found device (or let user choose)
      const device = devices[0];
      const connected = await this.bleManager.connect(device.id);

      if (connected) {
        return { ...device, connected: true };
      }
    }

    return null;
  }

  /**
   * Get BLE manager instance
   */
  getBLEManager(): BLEManager {
    return this.bleManager;
  }
}

