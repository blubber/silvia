#ifndef __CONTROLLER_H__
#define __CONTROLLER_H__ 1

typedef struct {
    float     setpoint;
    float     Kp;
    float     Ki;
    float     Kd;

    float     integral;
    float     previous_error;
} ControllerContext;

#endif /* __CONTROLLER_H__ */
