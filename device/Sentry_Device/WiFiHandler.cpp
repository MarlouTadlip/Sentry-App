#include "WiFiHandler.h"
#include <WiFi.h>

const unsigned long WIFI_TIMEOUT = 30000;  // 30 seconds timeout
const int MAX_RETRIES = 3;
const unsigned long RECONNECT_CHECK_INTERVAL = 10000;  // Check every 10 seconds
unsigned long lastReconnectCheck = 0;

void connectWiFi(const char* ssid, const char* password) {
    int retryCount = 0;
    
    while (retryCount < MAX_RETRIES) {
        Serial.print("Connecting to Wi-Fi");
        if (retryCount > 0) {
            Serial.print(" (Attempt ");
            Serial.print(retryCount + 1);
            Serial.print("/");
            Serial.print(MAX_RETRIES);
            Serial.print(")");
        }
        Serial.println("...");
        
        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid, password);
        
        unsigned long startTime = millis();
        while (WiFi.status() != WL_CONNECTED) {
            if (millis() - startTime > WIFI_TIMEOUT) {
                Serial.println("\nConnection timeout!");
                break;
            }
            delay(500);
            Serial.print(".");
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\nWiFi connected!");
            Serial.print("IP address: ");
            Serial.println(WiFi.localIP());
            Serial.print("Signal strength (RSSI): ");
            Serial.print(WiFi.RSSI());
            Serial.println(" dBm");
            lastReconnectCheck = millis();
            return;
        } else {
            retryCount++;
            if (retryCount < MAX_RETRIES) {
                Serial.println("Connection failed. Retrying...");
                delay(2000);
            }
        }
    }
    
    Serial.println("\nWiFi connection failed after all retries!");
    Serial.println("Device will continue without WiFi connection.");
}

bool isWiFiConnected() {
    return WiFi.status() == WL_CONNECTED;
}

void maintainWiFiConnection(const char* ssid, const char* password) {
    unsigned long currentTime = millis();
    
    // Check connection status periodically
    if (currentTime - lastReconnectCheck >= RECONNECT_CHECK_INTERVAL) {
        lastReconnectCheck = currentTime;
        
        if (!isWiFiConnected()) {
            Serial.println("WiFi disconnected! Attempting to reconnect...");
            WiFi.disconnect();
            delay(1000);
            connectWiFi(ssid, password);
        }
    }
}