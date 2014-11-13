


typedef struct {
    float     setpoint;
    float     Kp;
    float     Ki;
    float     Kd;

    float     integral;
    float     previous_error;
} ControllerContext;


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
 * :param dt: Number of ms since last loop.
 * :param T: The current temperature in degrees C.
 *
 * :returns: 0 <= retval <= 1.
 *
 */
float controller_power (ControllerContext *ctx, uint32_t dt, float T) {
    float dt_seconds = dt / 1000.0;
    float error, derivative, output;

    error = ctx->setpoint - T;
    ctx->integral += error * dt_seconds;

    if (dt_seconds == 0) {
        derivative = 0;
    } else {
        derivative = (error - ctx->previous_error) / dt_seconds;
    }

    output = ctx->Kp * error + 
             ctx->Ki * ctx->integral + 
             ctx->Kd * derivative;
    ctx->previous_error = error;

    return output < 0 ? 0 : (output > 1 ? 1 : output);
}
