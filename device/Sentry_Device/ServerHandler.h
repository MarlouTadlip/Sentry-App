#ifndef SERVERHANDLER_H
#define SERVERHANDLER_H

#include <WebServer.h>
#include <ArduinoJson.h>
#include <functional>

extern WebServer server;

using JsonHandler = std::function<void(const JsonDocument&, JsonDocument&)>;

void startHttpServer();
void handleHttpClient();

void registerPostJson(const char* path, JsonHandler handler);
void setBaseUrl(const String& url);

// --- Client-side helper ---
bool postJson(const String& path, const String& jsonPayload);

#endif
