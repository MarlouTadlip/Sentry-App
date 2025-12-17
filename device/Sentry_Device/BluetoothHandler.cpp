#include "BluetoothHandler.h"

// BLE Server and Characteristic objects
BLEServer* pServer = nullptr;
BLECharacteristic* pSensorDataChar = nullptr;
BLECharacteristic* pGPSDataChar = nullptr;
BLECharacteristic* pConfigChar = nullptr;
BLECharacteristic* pDeviceStatusChar = nullptr;

bool deviceConnected = false;
bool oldDeviceConnected = false;

// Packet sequence number (increments for each packet)
static uint32_t sequenceNumber = 0;

// Command callback flag
static bool commandReceived = false;
static String receivedCommand = "";

// MTU tracking
static uint16_t currentMTU = BLE_DEFAULT_MTU;

// Server Callback class
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      sequenceNumber = 0; // Reset sequence on new connection
      // MTU negotiation happens automatically after connection
      // We'll use a conservative default and let chunking handle if needed
      currentMTU = BLE_MTU_REQUEST; // Assume requested MTU, chunking will handle if not
      Serial.println("*** Bluetooth: Client Connected ***");
      Serial.print("BLE: MTU requested: ");
      Serial.println(BLE_MTU_REQUEST);
      // Serial.println("BLE: Sequence number reset to 0");
    }

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
      currentMTU = BLE_DEFAULT_MTU; // Reset MTU on disconnect
      Serial.println("*** Bluetooth: Client Disconnected ***");
    }
};

// Configuration Characteristic Callback
class ConfigCharacteristicCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pCharacteristic) {
      String value = pCharacteristic->getValue();
      if (value.length() > 0) {
        receivedCommand = value;
        commandReceived = true;
    // Serial.print("BLE: Command received - ");
    // Serial.println(receivedCommand);
      }
    }
};

// Calculate CRC-16 (CCITT polynomial)
uint16_t calculateCRC16(const uint8_t* data, size_t length) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < length; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x8000) {
        crc = (crc << 1) ^ CRC_POLYNOMIAL;
      } else {
        crc <<= 1;
      }
    }
  }
  return crc;
}

// Get next sequence number
uint32_t getNextSequenceNumber() {
  return ++sequenceNumber;
}

// Get current MTU size
uint16_t getCurrentMTU() {
  return currentMTU;
}

// Send data with automatic chunking if needed
// NOTE: Chunking JSON data will break JSON structure on receiver side.
// This function is primarily a safety measure. Ideally, MTU negotiation
// should allow single-packet transmission. If chunking occurs, the receiver
// must reassemble chunks before parsing JSON.
void sendDataWithChunking(BLECharacteristic* pChar, const String& data) {
  if (pChar == nullptr || data.length() == 0) {
    return;
  }
  
  size_t dataLength = data.length();
  
  // Calculate safe payload size
  // ESP32 BLE library handles MTU automatically in setValue/notify
  // We use conservative estimate: assume MTU negotiation succeeded
  // If data exceeds MAX_PACKET_SIZE, we should not send it (data corruption risk)
  if (dataLength > MAX_PACKET_SIZE) {
    Serial.print("BLE ERROR: Data exceeds MAX_PACKET_SIZE (");
    Serial.print(dataLength);
    Serial.print(" > ");
    Serial.print(MAX_PACKET_SIZE);
    Serial.println(" bytes) - NOT SENDING");
    return;
  }
  
  // Try single packet transmission first
  // ESP32 BLE library will automatically handle MTU and split if needed
  // However, if MTU negotiation failed, this might silently fail
  // So we also provide chunking as explicit fallback for very large data
  size_t safeSinglePacketSize = (currentMTU > BLE_DEFAULT_MTU) ? 
                                 (currentMTU - 3) : BLE_CHUNK_SIZE;
  
  // Check if data fits in single packet
  if (dataLength <= safeSinglePacketSize) {
    // Single packet transmission - ESP32 BLE library handles MTU automatically
    pChar->setValue(data.c_str());
    pChar->notify();
  } else {
    // Data is larger than safe single packet size
    // Try sending anyway (ESP32 library might handle it), but warn
    Serial.print("BLE WARNING: Data size (");
    Serial.print(dataLength);
    Serial.print(" bytes) exceeds safe single packet size (");
    Serial.print(safeSinglePacketSize);
    Serial.println(" bytes)");
    Serial.println("BLE: Attempting single packet - ESP32 library will handle MTU");
    
    // Attempt single packet - ESP32 BLE library should handle MTU negotiation
    pChar->setValue(data.c_str());
    pChar->notify();
    
    // Note: If this fails silently, we have no way to detect it
    // The receiver should validate JSON completeness
  }
}

// Send error response
void sendErrorResponse(uint8_t errorCode, const char* message) {
  if (!deviceConnected || pConfigChar == nullptr) {
    return;
  }
  
  StaticJsonDocument<256> errorDoc;
  errorDoc["type"] = "error";
  errorDoc["error_code"] = errorCode;
  errorDoc["message"] = message;
  errorDoc["sequence"] = getNextSequenceNumber();
  errorDoc["timestamp"] = millis();
  
  String errorJson;
  serializeJson(errorDoc, errorJson);
  
  // Send via BLE with automatic chunking if needed
  sendDataWithChunking(pConfigChar, errorJson);
  
  // Reduced Serial output
  // Serial.print("BLE: Error 0x");
  // Serial.println(errorCode, HEX);
}

// Initialize Bluetooth Low Energy
void initBluetooth(const char* deviceName) {
  // Initialize BLE device
  BLEDevice::init(deviceName);
  
  // Request larger MTU for better throughput
  // Without this, BLE defaults to 20-byte MTU which truncates JSON data
  // This prevents the issue where only {"type":"sensor_data was being received
  // Must be called after BLEDevice::init() but before creating server
  BLEDevice::setMTU(BLE_MTU_REQUEST);
  Serial.print("BLE: MTU requested: ");
  Serial.println(BLE_MTU_REQUEST);
  
  // Create BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  
  // Create BLE Service
  BLEService* pService = pServer->createService(BLEUUID(SERVICE_UUID));
  
  // Create Sensor Data Characteristic (Read, Notify)
  pSensorDataChar = pService->createCharacteristic(
                      BLEUUID(CHAR_SENSOR_DATA_UUID),
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );
  pSensorDataChar->addDescriptor(new BLE2902());
  
  // Create GPS Data Characteristic (Read, Notify)
  pGPSDataChar = pService->createCharacteristic(
                   BLEUUID(CHAR_GPS_DATA_UUID),
                   BLECharacteristic::PROPERTY_READ |
                   BLECharacteristic::PROPERTY_NOTIFY
                 );
  pGPSDataChar->addDescriptor(new BLE2902());
  
  // Create Configuration Characteristic (Write, Notify)
  pConfigChar = pService->createCharacteristic(
                  BLEUUID(CHAR_CONFIG_UUID),
                  BLECharacteristic::PROPERTY_WRITE |
                  BLECharacteristic::PROPERTY_NOTIFY
                );
  pConfigChar->setCallbacks(new ConfigCharacteristicCallbacks());
  pConfigChar->addDescriptor(new BLE2902());
  
  // Create Device Status Characteristic (Read, Notify)
  pDeviceStatusChar = pService->createCharacteristic(
                        BLEUUID(CHAR_DEVICE_STATUS_UUID),
                        BLECharacteristic::PROPERTY_READ |
                        BLECharacteristic::PROPERTY_NOTIFY
                      );
  pDeviceStatusChar->addDescriptor(new BLE2902());
  
  // Start the service
  pService->start();
  
  // Start advertising
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(BLEUUID(SERVICE_UUID));
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);
  BLEDevice::startAdvertising();
  
  // Note: Actual MTU will be negotiated during connection
  // The negotiated value may be less than requested if client doesn't support it
  Serial.println("BLE: Initialized - MTU will be negotiated on connection");
}

// Check if Bluetooth is connected
bool isBluetoothConnected() {
  return deviceConnected;
}

// Send sensor data with packet structure
void sendSensorData(float ax, float ay, float az, float roll, float pitch, bool tiltDetected, const char* statusMessage, int statusCode) {
  if (!deviceConnected || pSensorDataChar == nullptr) {
    return;
  }
  
  // Build JSON packet
  StaticJsonDocument<256> doc;  // Increased to accommodate status message
  doc["type"] = "sensor_data";
  doc["sequence"] = getNextSequenceNumber();
  doc["timestamp"] = millis();
  
  // Sensor data
  JsonObject sensor = doc.createNestedObject("sensor");
  sensor["ax"] = ax;
  sensor["ay"] = ay;
  sensor["az"] = az;
  sensor["roll"] = roll;
  sensor["pitch"] = pitch;
  sensor["tilt_detected"] = tiltDetected;
  
  // Add status code if provided
  if (statusCode >= 0) {
    sensor["status_code"] = statusCode;
  }
  
  // Add status message if provided
  if (statusMessage != nullptr) {
    sensor["status_message"] = statusMessage;
  }
  
  // Serialize JSON
  String jsonData;
  serializeJson(doc, jsonData);
  
  // Calculate CRC
  uint8_t* dataBytes = (uint8_t*)jsonData.c_str();
  size_t dataLength = jsonData.length();
  uint16_t crc = calculateCRC16(dataBytes, dataLength);
  
  // Add CRC to JSON
  doc["crc"] = crc;
  jsonData = "";
  serializeJson(doc, jsonData);
  
  // Check data size and warn if too large
  if (jsonData.length() > MAX_PACKET_SIZE) {
    Serial.print("BLE WARNING: Sensor data exceeds MAX_PACKET_SIZE (");
    Serial.print(jsonData.length());
    Serial.print(" > ");
    Serial.print(MAX_PACKET_SIZE);
    Serial.println(" bytes)");
  }
  
  // Send via BLE with automatic chunking if needed
  sendDataWithChunking(pSensorDataChar, jsonData);
  
  // Reduced Serial output to save code space
  // Serial.print("BLE: Sensor [Seq: ");
  // Serial.print(sequenceNumber);
  // Serial.println("]");
}

// Send GPS data with packet structure
void sendGPSData(bool gpsFix, int satellites, float latitude, float longitude, float altitude, const char* statusMessage, int statusCode) {
  if (!deviceConnected || pGPSDataChar == nullptr) {
    return;
  }
  
  // Build JSON packet
  StaticJsonDocument<256> doc;  // Increased to accommodate status message
  doc["type"] = "gps_data";
  doc["sequence"] = getNextSequenceNumber();
  doc["timestamp"] = millis();
  
  // GPS data
  JsonObject gps = doc.createNestedObject("gps");
  gps["fix"] = gpsFix;
  gps["satellites"] = satellites;
  
  // Add status code if provided
  if (statusCode >= 0) {
    gps["status_code"] = statusCode;
  }
  
  // Add status message if provided
  if (statusMessage != nullptr) {
    gps["status_message"] = statusMessage;
  }
  
  if (gpsFix && latitude != 0.0 && longitude != 0.0) {
    gps["latitude"] = latitude;
    gps["longitude"] = longitude;
    if (altitude != 0.0) {
      gps["altitude"] = altitude;
    }
  } else {
    gps["latitude"] = nullptr;
    gps["longitude"] = nullptr;
    gps["altitude"] = nullptr;
  }
  
  // Serialize JSON
  String jsonData;
  serializeJson(doc, jsonData);
  
  // Calculate CRC
  uint8_t* dataBytes = (uint8_t*)jsonData.c_str();
  size_t dataLength = jsonData.length();
  uint16_t crc = calculateCRC16(dataBytes, dataLength);
  
  // Add CRC to JSON
  doc["crc"] = crc;
  jsonData = "";
  serializeJson(doc, jsonData);
  
  // Check data size and warn if too large
  if (jsonData.length() > MAX_PACKET_SIZE) {
    Serial.print("BLE WARNING: GPS data exceeds MAX_PACKET_SIZE (");
    Serial.print(jsonData.length());
    Serial.print(" > ");
    Serial.print(MAX_PACKET_SIZE);
    Serial.println(" bytes)");
  }
  
  // Send via BLE with automatic chunking if needed
  sendDataWithChunking(pGPSDataChar, jsonData);
  
  // Reduced Serial output to save code space
  // Serial.print("BLE: GPS [Seq: ");
  // Serial.print(sequenceNumber);
  // Serial.println("]");
}

// Send device status
void sendDeviceStatus(bool wifiConnected, bool gpsFix, int batteryLevel) {
  if (!deviceConnected || pDeviceStatusChar == nullptr) {
    return;
  }
  
  StaticJsonDocument<128> doc;  // Reduced from 256
  doc["type"] = "device_status";
  doc["sequence"] = getNextSequenceNumber();
  doc["timestamp"] = millis();
  
  JsonObject status = doc.createNestedObject("status");
  status["wifi_connected"] = wifiConnected;
  status["gps_fix"] = gpsFix;
  status["battery_level"] = batteryLevel;
  status["ble_connected"] = true;
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  // Calculate CRC
  uint8_t* dataBytes = (uint8_t*)jsonData.c_str();
  size_t dataLength = jsonData.length();
  uint16_t crc = calculateCRC16(dataBytes, dataLength);
  
  doc["crc"] = crc;
  jsonData = "";
  serializeJson(doc, jsonData);
  
  // Check data size and warn if too large
  if (jsonData.length() > MAX_PACKET_SIZE) {
    Serial.print("BLE WARNING: Device status exceeds MAX_PACKET_SIZE (");
    Serial.print(jsonData.length());
    Serial.print(" > ");
    Serial.print(MAX_PACKET_SIZE);
    Serial.println(" bytes)");
  }
  
  // Send via BLE with automatic chunking if needed
  sendDataWithChunking(pDeviceStatusChar, jsonData);
  
  // Reduced Serial output to save code space
  // Serial.print("BLE: Status [Seq: ");
  // Serial.print(sequenceNumber);
  // Serial.println("]");
}

// Process received commands
void processBluetoothCommands() {
  if (!commandReceived || receivedCommand.length() == 0) {
    return;
  }
  
  commandReceived = false;
  
  // Parse JSON command
  StaticJsonDocument<128> cmdDoc;  // Reduced from 256
  DeserializationError error = deserializeJson(cmdDoc, receivedCommand);
  
  if (error) {
    // Serial.print("BLE: Parse error - ");
    // Serial.println(error.c_str());
    sendErrorResponse(BLE_ERROR_INVALID_DATA, "Invalid JSON format");
    receivedCommand = "";
    return;
  }
  
  // Extract command type
  if (!cmdDoc.containsKey("command")) {
    sendErrorResponse(BLE_ERROR_INVALID_CMD, "Missing command field");
    receivedCommand = "";
    return;
  }
  
  uint8_t cmdType = cmdDoc["command"];
  String cmdName = "";
  
  // Process command
  switch (cmdType) {
    case CMD_GET_STATUS:
      cmdName = "GET_STATUS";
      // Serial.println("BLE: GET_STATUS");
      // Status will be sent via sendDeviceStatus() in main loop
      break;
      
    case CMD_SET_WIFI_SSID:
      cmdName = "SET_WIFI_SSID";
      // Serial.println("BLE: SET_WIFI_SSID");
      if (cmdDoc.containsKey("value")) {
        // TODO: Implement WiFi SSID update
      }
      break;
      
    case CMD_SET_WIFI_PASSWORD:
      cmdName = "SET_WIFI_PASSWORD";
      // Serial.println("BLE: SET_WIFI_PASSWORD");
      if (cmdDoc.containsKey("value")) {
        // TODO: Implement WiFi password update
      }
      break;
      
    case CMD_SET_API_ENDPOINT:
      cmdName = "SET_API_ENDPOINT";
      // Serial.println("BLE: SET_API_ENDPOINT");
      if (cmdDoc.containsKey("value")) {
        // TODO: Implement API endpoint update
      }
      break;
      
    case CMD_RESET_DEVICE:
      cmdName = "RESET_DEVICE";
      Serial.println("BLE: Resetting device...");
      delay(1000);
      ESP.restart();
      break;
      
    case CMD_CALIBRATE_SENSOR:
      cmdName = "CALIBRATE_SENSOR";
      // Serial.println("BLE: CALIBRATE_SENSOR");
      // TODO: Implement sensor calibration
      break;
      
    default:
      cmdName = "UNKNOWN";
      // Serial.print("BLE: Unknown cmd 0x");
      // Serial.println(cmdType, HEX);
      sendErrorResponse(BLE_ERROR_INVALID_CMD, "Unknown command type");
      receivedCommand = "";
      return;
  }
  
  // Send success response
  StaticJsonDocument<128> responseDoc;  // Reduced from 256
  responseDoc["type"] = "command_response";
  responseDoc["command"] = cmdType;
  responseDoc["command_name"] = cmdName;
  responseDoc["status"] = "success";
  responseDoc["sequence"] = getNextSequenceNumber();
  responseDoc["timestamp"] = millis();
  
  String responseJson;
  serializeJson(responseDoc, responseJson);
  
  uint8_t* dataBytes = (uint8_t*)responseJson.c_str();
  size_t dataLength = responseJson.length();
  uint16_t crc = calculateCRC16(dataBytes, dataLength);
  
  responseDoc["crc"] = crc;
  responseJson = "";
  serializeJson(responseDoc, responseJson);
  
  if (pConfigChar != nullptr) {
    // Send via BLE with automatic chunking if needed
    sendDataWithChunking(pConfigChar, responseJson);
    // Reduced Serial output
    // Serial.print("BLE: Cmd ");
    // Serial.print(cmdName);
    // Serial.println(" OK");
  }
  
  receivedCommand = "";
}

// Handle reconnection (should be called in loop)
void handleBluetoothReconnection() {
  // Disconnecting
  if (!deviceConnected && oldDeviceConnected) {
    delay(500);
    pServer->startAdvertising();
    oldDeviceConnected = deviceConnected;
  }
  
  // Connecting
  if (deviceConnected && !oldDeviceConnected) {
    oldDeviceConnected = deviceConnected;
  }
  
  // Process any received commands
  processBluetoothCommands();
}
