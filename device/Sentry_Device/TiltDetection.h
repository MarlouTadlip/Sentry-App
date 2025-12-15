#ifndef TILTDETECTION_H
#define TILTDETECTION_H

void calculateTilt(float ax, float ay, float az, float &roll, float &pitch);
bool isTiltExceeded(float roll, float pitch, float threshold = 180.0);

#endif
