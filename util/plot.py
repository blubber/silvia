'''
    Plot
    ~~~~
    Plot one or more teensy data files.
'''
#!/usr/bin/env python

import csv
import itertools
import os
import sys

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

colors = [
    (1, 0, 1),
    (0, 1, 1),
    (1, 0, 0),
    (0, 1, 0),
]


plt.figure()
logs = sys.argv[1]

for color, entry in zip(itertools.cycle(colors), os.listdir(logs)):
    if not entry.endswith('.log'):
        continue

    path = os.path.join(logs, entry)
    with open(path) as fp:
        reader = csv.reader(fp, delimiter='\t')
        params = dict(_.split('=') for _ in next(reader)[1:])
        headers = next(reader)
        index_t = headers.index('t')
        index_T = headers.index('T')

        t_, T_ = zip(*((row[index_t], row[index_T]) for row in reader))
        t = [float(_) / 1000 for _ in t_]
        T = map(float, T_)

        plt.plot(t, list(T), label='Tm (Kp={})'.format(params['Kp']),
                 color=color, linewidth=1)


plt.xlabel('time')

font_properties = FontProperties()
font_properties.set_size('x-small')
legend = plt.legend(loc=0, prop=font_properties)
plt.setp(legend.get_title(), fontsize='x-small')

plt.savefig("imbabimbaresult_pid.png", dpi=150)
