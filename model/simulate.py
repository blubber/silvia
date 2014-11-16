#!/usr/bin/env python3

import csv
import ctypes
import functools
import os.path

import numpy as np
from scipy.integrate import odeint, ode
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import system


# -------------------------------------------------------------------------
# Controller implementations

class Controller (object):
    ''' Temperature controller base class, takes care or storing the heater
        output for later plotting.

    :param setpoint: The desired temperature in degrees centigrade.
    '''

    def __init__(self, setpoint):
        self.setpoint = setpoint
        self.power = []

    def heater_power(self, t, T):
        raise NotImplementedError()

    def __call__(self, t, T):
        # At T == 140 the second bimetallic thermostat (T2) disconnects
        if T >= 140:
            return 0

        power = self.heater_power(t, T)
        self.power.append((t, power))

        if t >= 3600:
            return 0
        return power


class ControllerContext (ctypes.Structure):
    _fields_ = [
        ('setpoint', ctypes.c_float),
        ('Kp', ctypes.c_float),
        ('Ki', ctypes.c_float),
        ('Kd', ctypes.c_float),
        ('integral', ctypes.c_float),
        ('previous_error', ctypes.c_float),
    ]


class RealPidController (Controller):

    def __init__(self, setpoint, Kp, Ki, Kd):
        super().__init__(setpoint)
        self.lib = ctypes.cdll.LoadLibrary('./libcontroller.so')
        self.lib.controller_new.restype = ControllerContext
        self.lib.controller_power.restype = ctypes.c_float
        self._last_t = 0

        self._ctx = self.lib.controller_new(
            ctypes.c_float(setpoint),
            ctypes.c_float(Kp),
            ctypes.c_float(Ki),
            ctypes.c_float(Kd))

    def heater_power(self, t, T):
        dt = t - self._last_t
        self._last_t = t

        ratio = self.lib.controller_power(
            ctypes.byref(self._ctx),
            ctypes.c_float(dt), ctypes.c_float(T))

        return system.heater_power * min(1, max(0, ratio))


class PidController (Controller):

    def __init__(self, setpoint, Kp, Ki, Kd):
        super().__init__(setpoint)
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self._previous_t = 0
        self._integral = 0
        self._previous_error = 0

    def heater_power(self, t, T):
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


class ThresholdController (Controller):

    def __init__(self, setpoint):
        super().__init__(setpoint)

    def heater_power(self, t, T):
        return system.heater_power * (T < self.setpoint)

# -------------------------------------------------------------------------
# Solver for stiff systems


def odebdf(model, y0, t):
    result = np.zeros((len(t), len(y0)))
    sys = lambda y, t: model(t, y)  # bdf requires swapped arguments
    r = ode(sys).set_integrator('zvode', method='bdf')
    r.set_initial_value(y0, t[0])
    result[0] = y0
    step = 1
    while r.successful() and (step < len(t)):
        r.integrate(t[step])
        result[step] = np.real(r.y)
        step += 1
    return result


# -------------------------------------------------------------------------
# Tweakable simulation parameters

# Tweakable parameters
t = np.arange(0, 7200, 0.05)
setpoint = 100
Kp = 0.065
Ki = 0
Kd = 0

# Uncomment the controller to use
# controller = RealPidController(setpoint, Kp, Ki, Kd)
controller = PidController(setpoint, Kp, Ki, Kd)
# controller = ThresholdController(setpoint)


# -------------------------------------------------------------------------
# Simulate and plot

# initial conditions.
yW = 20
yM = 20
y0 = [yW, yM]

model = functools.partial(system.model, controller)
result, info_dict = odeint(model, y0, t, full_output=True)

plt.figure()

plt.plot(t, result[:, 1], label='Tm', color=(0, 0.5, 1), linewidth=1)
# plt.plot(t, result[:, 0], label='Tw', color=(1, 0.5, 0), linewidth=1.5)

# _t, _p = zip(*controller.power)
# plt.plot(_t, [_ / system.heater_power * 100 for _ in _p],
#          label='Duty Cycle (%)', color=(1, 0, 1), linewidth=1.5)

with open(os.path.expanduser(('~/Dropbox/silvia_pid_upgrade/data/eerste run/'
                              'teensy-output_Kp=0.065_Ki=0_Kd=0_2014-11-16_14,04.log'))) as fp:
    reader = csv.reader(fp, delimiter='\t')
    params = dict(_.split('=') for _ in next(reader)[1:])
    headers = next(reader)
    index_t = headers.index('t')
    index_T = headers.index('T')

    t_, T_ = zip(*((row[index_t], row[index_T]) for row in reader))
    t = [float(_) / 1000 for _ in t_]
    T = map(float, T_)

    index= [_ >= 7200 for _ in t].index(True)
    t = t[:index]
    T = list(T)[:index]

    plt.plot(t, list(T), label='Tm (Kp={})'.format(params['Kp']),
             color=(1, 0, 0), linewidth=1)


plt.xlabel('time')

font_properties = FontProperties()
font_properties.set_size('x-small')
legend = plt.legend(loc=0, prop=font_properties)
plt.setp(legend.get_title(), fontsize='x-small')

plt.savefig("imbabimbaresult_pid.png", dpi=150)
