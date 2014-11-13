#ifndef __CONTROLLER_H__
#define __CONTROLLER_H__ 1

typedef unsigned long uint32_t;
typedef struct {
    float     setpoint;
    float     Kp;
    float     Ki;
    float     Kd;

    float     integral;
    float     previous_error;
} ControllerContext;

ControllerContext controller_new (float setpoint, float Kp,
                                  float Ki, float Kd);
float controller_power (ControllerContext *ctx, long dt, float T);

#endif /* __CONTROLLER_H__ */
