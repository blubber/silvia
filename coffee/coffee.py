'''
'''

import argparse
import enum
import os
import struct
import sys
import struct
import time

import serial

from coffee.channel import SerialChannel, FakeChannel
from coffee.output import Progress, Spinner
from coffee.message import (
    Status1Message,
    Status2Message,
    Status3Message,
    SetpointMessage,
    StartPumpMessage,
    StopPumpMessage
)

def get_status (channel):
    retval = {}
    for message in [
            Status1Message(),
            Status2Message(),
            Status3Message()]:
        retval.update(channel.dispatch(message))
    return retval


def status_command (args, channel):
    print(''.join([
        'Heater Cycle  On /',
        '   Off'
        '  | Pump Cycle    ',
        '    P',
        '       T',
        '    dt',
        '    Pump',
        '   Heater'
    ]))
    fmt = ''.join([
            '{heater_on_cycle:16d}',
            '     {heater_off_cycle:3d}',
            '  |      {pump_on_cycle:5d}'
            '     {power:4.2f}'
            '   {temp:5.2f}'
            '   {dt:3d}',
            '       {pump_on:1d}',
            '        {heater_on:1d}'
        ])

    while True:
        status = get_status(channel)
        sys.stdout.write('\b' * 80)
        sys.stdout.write(fmt.format(**status))
        sys.stdout.write('\r')
        sys.stdout.flush()

        if args.watch:
            time.sleep(args.watch)
        else:
            break

    print('')
    return 0


def setpoint_command (args, channel):
    message = SetpointMessage(args.setpoint)
    retval = channel.dispatch(message)
    print('Setpoint changed {previous:.2f} -> {setpoint:.2f}'.format(**retval))


def start_pump_command (args, channel):
    cnt = 0
    message = StartPumpMessage(5000)
    spinner = Spinner('Pumping')

    try:
        while True:
            if cnt % 10 == 0:
                channel.dispatch(message)

            spinner.spin(cnt / 10.0, unit='s')
            cnt += 1
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('')
        channel.dispatch(StopPumpMessage())


def brew (channel, duration, label=None, include_temperature=False):
    ''' Brew coffee.

    :param channel: The channel to use for comms.
    :param duration: Number of seconds to brew.
    :param label: Optional progress bar label.
    :param include_temperature: Include temp reading in label?

    :returns: The progress bar used (caller should .finish())
    '''
    assert 2 < duration < 40, "Duration not sane."

    label = label or ''
    duration_ms = int(duration * 1000)

    if include_temperature:
        label = '{} {{temp:6.2f}} C'.format(label)

    status = get_status(channel)
    temp = status['temp']

    progress = Progress(duration, label=label.format(temp=temp), unit='s')
    progress.update(0)

    channel.dispatch(StartPumpMessage(duration_ms))
    current = 0
    count = 0

    try:
        while current < duration_ms:
            status = get_status(channel)
            temp = status['temp']
            current = duration_ms - status['pump_on_cycle']
            progress.label = label.format(temp=temp)
            progress.update((current + 50) / 1000.0)
    except KeyboardInterrupt:
        progress.finish('Aborted', error=True)
        channel.dispatch(StopPumpMessage())
        print('')
        sys.exit(-1)

    return progress


def brew_command (args, channel):

    if args.preinfuse:
        T = args.preinfuse
        progress = Progress(T + 2, 'Preinfuse {:5.2}s'.format(T), unit='s')
        pos = 0
        channel.dispatch(StartPumpMessage(int(T * 1000)))
        while pos < (T + 2):
            progress.update(pos)
            pos += 0.1
            time.sleep(0.1)
        progress.finish()
        time.sleep(0.5)

    progress = brew(channel, args.duration, 'Brewing', True)
    progress.finish('Enjoy!')
    print('')


def backflush_command (args, channel):
    duration = args.interval
    pause = args.pause
    cycles = args.cycles

    for i in range(cycles):
        label = 'Backflush {:2d} / {:2d}'.format(i + 1, cycles)
        brew(channel, duration, label, include_temperature=True).finish()
        progress = Progress(pause, '{}         '.format(label), unit='s')

        try:
            progress.run(0.1, 0.1)
        except KeyboardInterrupt:
            progress.finish('Aborted!', error=True)
            sys.exit(-1)

        if i == cycles - 1:
            progress.finish('Done!')
        else:
            progress.finish()
    print('')


def main ():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands')

    parser.add_argument('-s', '--serial', default=None,
        help='Specify the serial port to use.')

    status_parser = subparsers.add_parser('status')
    status_parser.add_argument('-w', '--watch', required=False,
        type=float, help="Watch the status, specify s interval.")
    status_parser.set_defaults(func=status_command)

    setpoint_parser = subparsers.add_parser('setpoint')
    setpoint_parser.add_argument('setpoint', type=float)
    setpoint_parser.add_argument('-s', '--status', type=bool, default=False)
    setpoint_parser.set_defaults(func=setpoint_command)    

    start_pump_parser = subparsers.add_parser('pump')
    start_pump_parser.add_argument('-H', '--force-heater', type=bool, default=False)
    start_pump_parser.set_defaults(func=start_pump_command)

    brew_parser = subparsers.add_parser('brew')
    brew_parser.add_argument('-H', '--force-heater', type=bool, default=False)
    brew_parser.add_argument('-P', '--preinfuse', type=float, default=0.0)    
    brew_parser.add_argument('duration', type=float)
    brew_parser.set_defaults(func=brew_command)

    backflush_parser = subparsers.add_parser('backflush')
    backflush_parser.add_argument('-I', '--interval', default=12, type=float)
    backflush_parser.add_argument('-P', '--pause', default=6, type=float)
    backflush_parser.add_argument('cycles', type=int)
    backflush_parser.set_defaults(func=backflush_command)

    args = parser.parse_args()

    serial_port = args.serial or \
        os.getenv('COFFEE_SERIAL_PORT', None)

    if serial_port is None:
        print('Please specify a serial port to use.')
        return -1

    retval = -2

    try:
        with serial.Serial(serial_port, 9600) as fp:
            # if True:
            channel = SerialChannel(fp)
            # channel = FakeChannel()
            retval = args.func(args, channel)
    except KeyboardInterrupt:
        print('')

    return retval


if __name__ == '__main__':
    sys.exit(main())
