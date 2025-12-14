#ifndef MPU6050HANDLER_H
#define MPU6050HANDLER_H

#include <MPU6050.h>

extern MPU6050 mpu;

void initMPU();
void readAccel(float &ax, float &ay, float &az);

#endif
