
#include "Controller.h"


double PidController::heaterPower (double dt, double T) {
    double error = setpoint - T;
    double derivative = 0;
    double output = 0;

    integral += error * dt;

    integral = integral > 250 ? 250 : integral;

    derivative = dt == 0 ? 0 : (error - previous_error) / dt;
    previous_error = error;
    output = Kp * error + Ki * integral + Kd * derivative;

    return output;
}
