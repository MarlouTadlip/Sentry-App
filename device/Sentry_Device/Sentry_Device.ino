#include <Arduino.h>
#include "MPU6050Handler.h"
#include "TiltDetection.h"
#include "BluetoothHandler.h"

// Data collection variables
unsigned long lastSendTime = 0;
const unsigned long SEND_INTERVAL = 2500;  // Send every 2.5n  seconds

// Tilt detection configuration
const float TILT_THRESHOLD = 60.0;  // degrees - adjust for sensitivity (lower = more sensitive)

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("=== SENTRY DEVICE INITIALIZING ===");

  // Initialize Bluetooth
  initBluetooth("Sentry-Device");

  // Initialize MPU6050
  initMPU();
  Serial.println("MPU6050 initialized");
  
  lastSendTime = millis();
  Serial.println("Device Ready - Waiting for Bluetooth connection...");
}

void loop() {
  // Handle Bluetooth reconnection
  handleBluetoothReconnection();

  // Read sensor data from MPU6050
  float ax, ay, az;
  readAccel(ax, ay, az);

  // Calculate tilt angles
  float roll, pitch;
  calculateTilt(ax, ay, az, roll, pitch);

  // Check if tilt exceeds threshold (accident detection)
  bool currentTilt = isTiltExceeded(roll, pitch, TILT_THRESHOLD);

  // Send data via Bluetooth every SEND_INTERVAL milliseconds
  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    if (isBluetoothConnected()) {
      // Get MPU6050 status message and status code
      const char* mpuStatusMsg = getMPUStatusMessage();
      int mpuStatus = getMPUStatus();
      
      // Send real sensor data from MPU6050 with status message and status code
      sendSensorData(ax, ay, az, roll, pitch, currentTilt, mpuStatusMsg, mpuStatus);
      
      // Display appropriate status message based on MPU6050 state
      if (mpuStatus == 0) {
        // MPU6050 device not working
        Serial.print("BLE: MPU6050 Status [Code: 0] - ⚠️ MPU6050 device not working - Check connections");
        Serial.println();
      } else if (mpuStatus == 1) {
        // MPU6050 readings unstable
        Serial.print("BLE: MPU6050 Status [Code: 1] - ⚠️ MPU6050 readings unstable - Check sensor");
        Serial.println();
      } else if (mpuStatus == 2) {
        // MPU6050 working
        if (currentTilt) {
          Serial.println("BLE: ⚠️ ACCIDENT DETECTED! Sensor data sent");
        } else {
          Serial.println("BLE: Sensor data sent");
        }
      }
      
      // Send device status
      sendDeviceStatus(false, -1);
      Serial.println("BLE: Device status sent");
      
      Serial.println("---");
    } else {
      Serial.println("BLE: Waiting for connection...");
    }
    
    lastSendTime = currentTime;
  }

  delay(500);
}