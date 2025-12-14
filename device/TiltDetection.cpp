#include "TiltDetection.h"
#include <math.h>

void calculateTilt(float ax, float ay, float az, float &roll, float &pitch) {
    roll  = atan2(ay, az) * 180.0 / M_PI;
    pitch = atan2(-ax, sqrt(ay*ay + az*az)) * 180.0 / M_PI;
}

bool isTiltExceeded(float roll, float pitch, float threshold) {
    return (fabs(roll) > threshold || fabs(pitch) > threshold);
}
