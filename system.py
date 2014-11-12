'''
    System
    ~~~~~~
    This module contains all the variables and functions needed to simulate
    the Silvia's thermal system.
'''

import math

# -------------------------------------------------------------------------
# System Parameters

#: Heat capacity of the water inside the boiler.
Cw = 0.23 * 4176.8

#: Radius of the boiler (in m).
r = (7.7/2.0) * 0.01

#: Width of the boiler wall (in m).
d = 0.3 * 0.01

#: Height of the boiler (in m).
h = 9.5 * 0.01

#: Density of brass (boiler material, in Kg/m^3).
rhoBrass = 8520

#: Specific heat of brass (in J/KgK).
cpBrass = 377

#: Heat capacity of the boiler.
Cm = ((math.pi * r**2 - math.pi * (r - d/2)**2) *
      h + 2 * (math.pi * r**2 * d)) * rhoBrass * cpBrass

#: Resistance between brass and boiler.
Rf = 0.15

#: Resistance between brass and environment.
Re = 1.41

#: Ambient tamperature.
Te = 21

#: The power of the heating element (in W).
heater_power = 980


# -------------------------------------------------------------------------
# Model

def model(fn, y, t):
    ''' Simulates the temperature of the water inside the boiler at `t`.

    :param fn: Should be a callable that takes the current time in seconds
               and the current water temperatur in degrees Celsius, and
               returns the desired heater power.
    '''
    return [
        ((-1 / (Rf*Cw)) * y[0] + (1 / (Cw * Rf)) * y[1] + fn(t, y[1]) / Cw),
        ((1 / (Rf * Cm)) * y[0] - (1 / (Rf * Cm) + 1 /
         (Re * Cm)) * y[1] + (1 / (Re * Cm)) * Te)]
