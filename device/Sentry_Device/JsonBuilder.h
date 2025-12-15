#ifndef JSONBUILDER_H
#define JSONBUILDER_H

#include <ArduinoJson.h>

// ArduinoJson by Benoit Blanchon...

// Builds JSON payload for tilt data
void buildTiltJson(
    String &out,
    float ax,
    float ay,
    float az,
    float roll,
    float pitch,
    bool alert
);

// Builds JSON payload for status data with arrays of roll/pitch readings
void buildStatusJson(
    String &out,
    const float* rolls,
    const float* pitches,
    int count,
    bool tiltDetected
);

#endif
