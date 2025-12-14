#include "WiFiHandler.h"
#include <WiFi.h>

void connectWiFi(const char* ssid, const char* password) {
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected!");
    Serial.print("IP: "); Serial.println(WiFi.localIP());
}
