#include "JsonBuilder.h"

void buildTiltJson(
    String &out,
    float ax,
    float ay,
    float az,
    float roll,
    float pitch,
    bool alert
) {
    StaticJsonDocument<256> doc;

    doc["ax"] = ax;
    doc["ay"] = ay;
    doc["az"] = az;
    doc["roll"] = roll;
    doc["pitch"] = pitch;
    doc["alert"] = alert;

    serializeJson(doc, out);
}

void buildStatusJson(
    String &out,
    const float* rolls,
    const float* pitches,
    int count,
    bool tiltDetected
) {
    StaticJsonDocument<2048> doc;  // Larger for array data
    JsonArray rollArray = doc.createNestedArray("rolls");
    JsonArray pitchArray = doc.createNestedArray("pitches");
    
    for (int i = 0; i < count; i++) {
        rollArray.add(rolls[i]);
        pitchArray.add(pitches[i]);
    }
    
    doc["tiltDetected"] = tiltDetected;
    doc["count"] = count;
    
    serializeJson(doc, out);
}