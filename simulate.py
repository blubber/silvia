
import functools

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

import system


# -------------------------------------------------------------------------
# Controller implementations

class PidController (object):

    def __init__(self, setpoint, Kp, Ki, Kd):
        self.setpoint = setpoint
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self._previous_t = 0
        self._integral = 0
        self._previous_error = 0

    def __call__(self, t, T):
        dt = t - self._previous_t
        self._previous_t = t

        error = self.setpoint - T
        self._integral += error * dt

        if dt == 0:
            derivative = 0
        else:
            derivative = (error - self._previous_error) / dt

        output = self.Kp * error + \
            self.Ki * self._integral + \
            self.Kd * derivative
        self._previous_error = error

        return system.heater_power * min(1, max(0, output))


# -------------------------------------------------------------------------
# Simulate and plot

# initial conditions.
yW = 20
yM = 20
y0 = [yW, yM]

t = np.arange(0, 1600, 0.05)

controller = PidController(100, 0.025, 0.00001, 0)
model = functools.partial(system.model, controller)
result, info_dict = odeint(model, y0, t, full_output=True)

plt.figure()

plt.plot(t, result[:, 1], label='Tm', color=(0, 0.5, 1), linewidth=2)
plt.plot(t, result[:, 0], label='Tw', color=(1, 0.5, 0), linewidth=2)

controller._integral = 0
controller._previous_t = 0
power = [controller(_t, _T) / system.heater_power * controller.setpoint for
         _t, _T in zip(t, result[:, 1])]
plt.plot(t, power, label='Power', color=(1, 0, 1), linewidth=2)

plt.xlabel('time')
plt.legend(loc=0)
plt.savefig("imbabimbaresult_pid.png", dpi=600)
