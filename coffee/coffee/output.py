'''
    coffee.output
    ~~~~~~~~~~~~~
    Utilities for outputting information to the terminal.
'''

import itertools
import os
import sys
import time

from termcolor import colored


def get_window_width ():
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(columns)


class ClearMixin (object):

    def clear (self):
        cols = get_window_width()
        self.fp.write('\b' * cols)


class Spinner (ClearMixin):

    def __init__ (self, label=None, fp=sys.stdout):
        self.iter = itertools.cycle([
                '|',
                '/',
                '-',
                '\\',
            ])
        self.label = label
        self.fp = fp


    def spin (self, counter=None, unit=None):
        self.clear()
        self.fp.write('    ')
        self.fp.write(next(self.iter))

        if self.label:
            self.fp.write('  {}'.format(self.label))

        if counter:
            unit = unit or ''
            self.fp.write('  ({:.1f}{})'.format(counter, unit))
        self.fp.write('\r')

        self.fp.flush()


class Progress (ClearMixin):

    def __init__ (self, target, label=None, fp=sys.stdout, unit=None):
        self.label = label
        self.target = target
        self.current = 0
        self.fp = fp
        self.unit = unit
        self.prefix_length = 0


    def update (self, current, color=None):
        self.current = current
        width = get_window_width()
        color = color or 'on_cyan'

        ratio = self.current / float(self.target)
        if ratio > 1:
            ratio = 1

        left = self.target - self.current
        if left < 0:
            left = 0

        prefix_parts = ['    ']
        if self.label:
            prefix_parts.append('{}  '.format(self.label))
        prefix_parts.append('{:5.1f}'.format(left))
        if self.unit:
            prefix_parts.append(self.unit)
        prefix_parts.append('    ')
        prefix = ''.join(prefix_parts)
        self.prefix_length = len(prefix)


        suffix = '    {:5.1f}%    '.format(ratio * 100)

        N = width - len(suffix) - len(prefix) - 5
        n = int(ratio * N)
        point = '>' if n < N else '='

        self.clear()
        self.fp.write(prefix)
        self.fp.write('{}{}'.format(
            colored(' ' * n, 'yellow', color, attrs=['bold']),
            colored(' ' * (N - n), 'white', 'on_blue')))
        self.fp.write(suffix)
        self.fp.flush()


    def run (self, increment, sleep):
        while self.current < self.target:
            self.update(self.current + increment)
            time.sleep(sleep)


    def finish (self, label=None, error=False):
        color = 'on_red' if error else None
        self.update(self.target, color=color)
        if label:
            ws = self.prefix_length - 8 - len(label)
            self.fp.write('\r    {}    '.format(label))
            if ws > 0:
                self.fp.write(' ' * ws)
