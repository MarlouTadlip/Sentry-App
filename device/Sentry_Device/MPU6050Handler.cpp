#include "MPU6050Handler.h"
#include <SimpleKalmanFilter.h>
#include <Wire.h>

// SimpleKalmanFilter by Denys Sene

MPU6050 mpu;

const float ACCEL_RANGE = 32768.0; // ±2g

// Kalman filters for each axis
SimpleKalmanFilter kalmanAx(2, 2, 0.01);
SimpleKalmanFilter kalmanAy(2, 2, 0.01);
SimpleKalmanFilter kalmanAz(2, 2, 0.01);

// MPU6050 status tracking
static bool mpu6050Initialized = false;
static bool mpu6050Connected = false;
static unsigned long lastValidReading = 0;
static int consecutiveFailures = 0;
const unsigned long MPU_DATA_TIMEOUT = 5000; // 5 seconds timeout for stale data
const int MAX_CONSECUTIVE_FAILURES = 3; // Consider device unstable after 3 failures

void initMPU() {
    Wire.begin(21, 22);  // SDA = 21, SCL = 22
    delay(100); // Give I2C time to stabilize
    
    mpu.initialize();
    if (mpu.testConnection()) {
        mpu6050Connected = true;
        mpu6050Initialized = true;
        lastValidReading = millis();
        consecutiveFailures = 0;
        Serial.println("MPU6050: ✓ Device detected and initialized");
    } else {
        mpu6050Connected = false;
        mpu6050Initialized = false;
        Serial.println("MPU6050: ✗ FAILED - Device not detected");
        Serial.println("MPU6050: Check wiring: VCC, GND, SDA->GPIO21, SCL->GPIO22");
        Serial.println("MPU6050: Device will continue but sensor readings will be invalid");
    }
}

void readAccel(float &ax, float &ay, float &az) {
    if (!mpu6050Connected) {
        ax = 0.0;
        ay = 0.0;
        az = 0.0;
        return;
    }
    
    // Raw sensor values
    int16_t axRaw, ayRaw, azRaw;
    mpu.getAcceleration(&axRaw, &ayRaw, &azRaw);
    
    // Check if values are reasonable (MPU6050 range: -32768 to 32767)
    bool valuesValid = (axRaw >= -32768 && axRaw <= 32767) &&
                       (ayRaw >= -32768 && ayRaw <= 32767) &&
                       (azRaw >= -32768 && azRaw <= 32767);
    
    if (valuesValid) {
        // Apply Kalman filter
        float axFiltered = kalmanAx.updateEstimate(axRaw);
        float ayFiltered = kalmanAy.updateEstimate(ayRaw);
        float azFiltered = kalmanAz.updateEstimate(azRaw);

        // Normalize to -1 to 1 g
        ax = axFiltered / ACCEL_RANGE;
        ay = ayFiltered / ACCEL_RANGE;
        az = azFiltered / ACCEL_RANGE;
        
        lastValidReading = millis();
        consecutiveFailures = 0;
    } else {
        consecutiveFailures++;
        ax = 0.0;
        ay = 0.0;
        az = 0.0;
        
        if (consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
            mpu6050Connected = false;
        }
    }
}

bool isMPU6050Connected() {
    return mpu6050Connected;
}

bool isMPU6050Working() {
    if (!mpu6050Connected) {
        return false;
    }
    
    // Check if data is stale (no valid reading in timeout period)
    if (millis() - lastValidReading > MPU_DATA_TIMEOUT) {
        return false;
    }
    
    return true;
}

// MPU6050 Status Codes:
// 0 = MPU6050 device not working (not connected or no I2C communication)
// 1 = MPU6050 connected but readings unstable/invalid
// 2 = MPU6050 working properly (valid readings)
int getMPUStatus() {
    // Check if MPU6050 is connected via I2C
    if (!mpu6050Connected) {
        return 0; // Device not working
    }
    
    // Check if MPU6050 has valid recent readings
    if (isMPU6050Working() && consecutiveFailures == 0) {
        return 2; // Working properly
    }
    
    // MPU6050 is connected but readings are unstable
    return 1; // Readings unstable
}

// Get user-friendly status message
const char* getMPUStatusMessage() {
    int status = getMPUStatus();
    
    switch (status) {
        case 0:
            return "[Status: 0] MPU6050 device not working - Check connections";
        case 1:
            return "[Status: 1] MPU6050 readings unstable - Check sensor";
        case 2:
            return "[Status: 2] MPU6050 tracking active";
        default:
            return "[Status: ?] MPU6050 status unknown";
    }
}