'''
    coffee.message
    ~~~~~~~~~~~~~~
    Messages.
'''

import enum

from .channel import pack_float


class CommandType (enum.IntEnum):
    Status1      = 1
    Status2      = 2
    Status3      = 3
    Setpoint     = 10
    StartPump    = 20
    StopPump     = 21


class Message (object):

    #: Set this to a struct formatting string that results in 7 bytes
    format = None

    #: Add up to 7 fields that that represent the return value. Each
    #: item should be a ``(format, name)`` tuple.
    fields = []


class Status1Message (Message):
    command = CommandType.Status1
    format = 'BBBBBBB'
    fields = [
        ('H', 'heater_on_cycle'),
        ('H', 'heater_off_cycle'),
        ('H', 'dt'),
        ('?', 'heater_on')
    ]
    data = [0, 0, 0, 0, 0, 0, 0]


class Status2Message (Message):
    command = CommandType.Status2
    format = 'BBBBBBB'
    fields = [
        ('L', 'pump_on_cycle'),
        ('F', 'temp'),
        ('?', 'pump_on')
    ]
    data = [0, 0, 0, 0, 0, 0, 0]


class Status3Message (Message):
    command = CommandType.Status3
    format = 'BBBBBBB'
    fields = [
        ('F', 'power'),
    ]
    data = [0, 0, 0, 0, 0, 0, 0]


class SetpointMessage (Message):
    command = CommandType.Setpoint
    format = 'BBBBBBB'
    fields = [
        ('F', 'setpoint'),
        ('F', 'previous'),
    ]


    def __init__ (self, setpoint):
        self.setpoint = setpoint


    @property
    def data (self):
        return pack_float(self.setpoint) + (5 * (0,))


class StartPumpMessage (Message):
    command = CommandType.StartPump
    format = 'HBBBBB'
    fields = [('B', 'empty')]

    def __init__ (self, duration):
        self.duration = duration


    @property
    def data (self):
        return [self.duration] + [0] * 5


class StopPumpMessage (Message):
    command = CommandType.StartPump
    format = 'BBBBBBB'
    fields = [('B', 'empty')]
    data = [0, 0, 0, 0, 0, 0, 0]


