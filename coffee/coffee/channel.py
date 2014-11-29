'''
    coffee.channel
    ~~~~~~~~~~~~~~
    Serial and mock channels.
'''

import struct
import time


def expand_format_string (format):
    ''' Returns `format` with ``F`` specifiers expanded to ``BB`` '''
    return format.replace('F', 'BB')


def generate_input_format (fields):
    raw_format = ''.join(list(zip(*fields))[0])
    base = '!B{}'.format(expand_format_string(raw_format))
    size = struct.calcsize(base)

    if size < 8:
        fmt = '{}{}'.format(base, 'B' * (8 - size))
    elif size > 8:
        raise RuntimeError()
    else:
        fmt = base

    return fmt


def unpack_float (integer, fraction):
    return integer + (fraction / 255.0)


def pack_float (val):
    return (int(val), int(255 * (val - int(val))))


def unpack_message (fields, data):
    retval = {}
    index = 0

    for format, label in fields:
        if format == 'F':
            val = unpack_float(data[index], data[index+1])
            index += 2
        else:
            val = data[index]
            index += 1

        retval[label] = val

    return retval


class Channel (object):

    def dispatch (self, message):
        output_format = '!B{}'.format(expand_format_string(message.format))
        output_data = message.data
        input_format = generate_input_format(message.fields)

        assert struct.calcsize(output_format) == 8
        assert struct.calcsize(input_format) == 8

        packed = struct.pack(output_format, int(message.command), *output_data)
        self.send(packed)

        input_data = struct.unpack(input_format, self.receive())
        unpacked = unpack_message(message.fields, input_data[1:])
        return unpacked


    def send (self, packed):
        raise NotImplementedError()


    def receive (self):
        raise NotImplementedError()



class SerialChannel (Channel):

    def __init__ (self, serial_port):
        self.serial_port = serial_port


    def send (self, packed):
        self.serial_port.write(packed)


    def receive (self):
        return self.serial_port.read(8)


class FakeChannel (Channel):

    def __init__ (self):
        self.last_call = 0
        self.status = {
            'heater_on_cycle': 0,
            'heater_off_cycle': 0,
            'dt': 0,
            'heater_on': False,
            'pump_on_cycle': 0,
            'temp': 21.25,
            'pump_on': False,
            'power': 0.42,
        }
        self.retval = None


    def send (self, packed):
        diff = 1000 * (time.time() - self.last_call)
        self.last_call = time.time()
        self.status['pump_on_cycle'] -= int(diff)

        if self.status['pump_on_cycle'] <= 0:
            self.status['pump_on_cycle'] = 0
            self.status['pump_on'] = False
        else:
            self.status['pump_on'] = True

        if packed[0] == 1:
            self.retval = struct.pack('!BHHH?', 1,
                self.status['heater_on_cycle'],
                self.status['heater_off_cycle'],
                self.status['dt'],
                self.status['heater_on'])

        elif packed[0] == 2:
            v1, v2 = pack_float(self.status['temp'])
            self.retval = struct.pack('!BLBB?', 2,
                self.status['pump_on_cycle'], v1, v2,
                self.status['pump_on'])

        elif packed[0] == 3:
            v1, v2 = pack_float(self.status['power'])
            self.retval = struct.pack('!BBBBBBBB', 3, v1, v2, 0, 0, 0, 0, 0)

        elif packed[0] == 10:
            _, v1, v2, *_ = struct.unpack('!BBBBBBBB', packed)
            old = self.status['temp']
            self.status['temp'] = unpack_float(v1, v2)
            a1, a2 = pack_float(old)
            self.retval = struct.pack('!BBBBBBBB', 10, v1, v2, a1, a2, 0, 0, 0)

        elif packed[0] == 20:
            _, self.status['pump_on_cycle'], *_ = struct.unpack('!BHBBBBB', packed)
            self.retval = struct.pack('!BBBBBBBB', 20, 0, 0, 0, 0, 0, 0, 0)

    def receive (self):
        return self.retval

