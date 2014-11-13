
#include "controller.h"


ControllerContext controller_new (float setpoint, float Kp,
                                  float Ki, float Kd) {
    ControllerContext ctx;

    ctx.setpoint = setpoint;
    ctx.Kp = Kp;
    ctx.Ki = Ki;
    ctx.Kd = Kd;

    ctx.integral = 0;
    ctx.previous_error = 0;

    return ctx;
}


/** Run a single iteration of the controller.
 *
 * :param ctx: Pointer to an initialized ControllerContext.
 * :param dt: Number of seconds since the last iteration.
 * :param T: The current temperature in degrees C.
 *
 * :returns: 0 <= retval <= 1.
 *
 */
float controller_power (ControllerContext *ctx, float dt, float T) {
    float error, derivative, output;

    error = ctx->setpoint - T;
    ctx->integral += error * dt;

    if (dt == 0) {
        derivative = 0;
    } else {
        derivative = (error - ctx->previous_error) / dt;
    }

    output = ctx->Kp * error + 
             ctx->Ki * ctx->integral + 
             ctx->Kd * derivative;
    ctx->previous_error = error;

    return output;
}
