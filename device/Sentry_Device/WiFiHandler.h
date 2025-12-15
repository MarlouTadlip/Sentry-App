#ifndef WIFIHANDLER_H
#define WIFIHANDLER_H

void connectWiFi(const char* ssid, const char* password);
bool isWiFiConnected();
void maintainWiFiConnection(const char* ssid, const char* password);

#endif