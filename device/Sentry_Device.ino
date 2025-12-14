#include <Arduino.h>
#include "MPU6050Handler.h"
#include "WiFiHandler.h"
#include "TiltDetection.h"
// #include "ServerHandler.h"  // Commented out for testing
// #include "JsonBuilder.h"    // Commented out for testing

// Wi-Fi
const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";

// Endpoint to send data to
// const char* endpoint = "localhost:8080";  // Commented out for testing

// Data collection buffers (assuming ~20 readings per second with 500ms delay)
// const int MAX_READINGS = 200;  // Commented out for testing
// float rollBuffer[MAX_READINGS];  // Commented out for testing
// float pitchBuffer[MAX_READINGS];  // Commented out for testing
// int readingCount = 0;  // Commented out for testing
// unsigned long lastSendTime = 0;  // Commented out for testing
// const unsigned long SEND_INTERVAL = 10000;  // Commented out for testing
// bool tiltDetected = false;  // Commented out for testing

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  connectWiFi(ssid, password);

  // Initialize MPU6050
  initMPU();

  // Register routes - Commented out for testing
  // setBaseUrl(endpoint);
  // registerPostJson("/tilt", [](const JsonDocument& req, JsonDocument& res) {
  //   float roll  = req["roll"]  | 0;
  //   float pitch = req["pitch"] | 0;
  //   res["received"] = true;
  //   res["alert"] = (abs(roll) > 180 || abs(pitch) > 180);
  // });

  // Start HTTP server - Commented out for testing
  // startHttpServer();
  
  // lastSendTime = millis();  // Commented out for testing
}

void loop() {
  // handleHttpClient();  // Commented out for testing

  float ax, ay, az;
  readAccel(ax, ay, az);

  // Calculate tilt
  float roll, pitch;
  calculateTilt(ax, ay, az, roll, pitch);

  // Store readings in buffer - Commented out for testing
  // if (readingCount < MAX_READINGS) {
  //   rollBuffer[readingCount] = roll;
  //   pitchBuffer[readingCount] = pitch;
  //   readingCount++;
  // }

  // Check tilt detection (180 degree threshold)
  bool currentTilt = isTiltExceeded(roll, pitch, 180.0);
  // if (currentTilt) {
  //   tiltDetected = true;
  // }

  // Serial output for roll, pitch, and tilt detection
  Serial.print("Roll: "); 
  Serial.print(roll);
  Serial.print("°, Pitch: "); 
  Serial.print(pitch);
  Serial.print("°, Tilt Detected: ");
  Serial.println(currentTilt ? "YES" : "NO");

  // Send data every 10 seconds - Commented out for testing
  // unsigned long currentTime = millis();
  // if (currentTime - lastSendTime >= SEND_INTERVAL) {
  //   if (readingCount > 0 && WiFi.status() == WL_CONNECTED) {
  //     String jsonPayload;
  //     buildStatusJson(jsonPayload, rollBuffer, pitchBuffer, readingCount, tiltDetected);
  //     
  //     if (postJson("/status", jsonPayload)) {
  //       Serial.println("Data sent to /status endpoint");
  //     }
  //     
  //     // Reset buffers
  //     readingCount = 0;
  //     tiltDetected = false;
  //   }
  //   lastSendTime = currentTime;
  // }

  delay(500); // adjust loop speed
}