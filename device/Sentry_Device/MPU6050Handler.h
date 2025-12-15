#ifndef MPU6050HANDLER_H
#define MPU6050HANDLER_H

#include <MPU6050.h>

// MPU6050 by Electronic Cats

extern MPU6050 mpu;

void initMPU();
void readAccel(float &ax, float &ay, float &az);

#endif
