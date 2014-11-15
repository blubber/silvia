'''
    Postprocess teensy ouput
    ~~~~~~~~~~~~~~~~~~~~~~~~
'''

import argparse
import csv
import time
import os
import sys


def create_filename (Kp, Ki, Kd, setpoint):
    parts = [
        'teensy-output',
        'Kp={}'.format(Kp),
        'Ki={}'.format(Ki),
        'Kd={}'.format(Kd),
        time.strftime('%Y-%m-%d_%H,%M')
    ]
    return '{}.log'.format('_'.join(parts))


def log_lines (log):
    for line in log:
        line = line.strip()
        if line == '' or line[0] == ':':
            continue
        yield [float(_) for _ in line.split('\t')]


def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', help='Log file from the teensy.')
    parser.add_argument('kp', type=float)
    parser.add_argument('ki', default=0, nargs='?', type=float)
    parser.add_argument('kd', default=0, nargs='?', type=float)
    parser.add_argument('setpoint', default=100, nargs='?', type=float)
    parser.add_argument('cycle', default=500, nargs='?', type=int)

    args = parser.parse_args()

    if not os.path.isfile(args.logfile):
        print('{}: no such file'.format(args.logfile))
        return -1

    Kp = args.kp
    Ki = args.ki
    Kd = args.kd
    setpoint = args.setpoint

    filename = create_filename(Kp, Ki, Kd, setpoint)

    if os.path.isfile(filename):
        print('Output file {} already exists.'.format(filename))
        return -2

    with open(args.logfile) as log, open(filename, 'w') as out:
        vals = log_lines(log)
        writer = csv.writer(out, delimiter='\t')

        writer.writerow([
            time.strftime('%Y-%m-%d %H:%M:%S'),
            'Kp={}'.format(Kp),
            'Ki={}'.format(Ki),
            'Kd={}'.format(Kd),
            'setpoint={}'.format(setpoint),
            'cycle={}'.format(args.cycle),
        ])
        writer.writerow(['On','T','Output', 'dt', 'cycle', 't'])
        writer.writerows(vals)



if __name__ == '__main__':
    sys.exit(main())
