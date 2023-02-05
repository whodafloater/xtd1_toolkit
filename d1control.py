#!/usr/bin/env python3
#
# original from https://github.com/fritzw/xtm1_toolkit
#
# MIT License
# Copyright (c) 2022 Fritz Webering
# 
# xTool D1 tests:
# Copyright (c) 2023 Tom Gray
# 

import sys
import traceback
from xtd1 import XTD1


machine = XTD1('192.168.0.104')
actions = {
    '--status':       lambda: machine.get_status(),
    '--stop':         lambda: machine.stop(),
    '--gcode':        lambda: machine.execute_gcode_command(' '.join(sys.argv[2:])),
    '--test':         lambda: machine.test(sys.argv[2], a3, a4, a5),
}

a3 = 0
a4 = 0
a4 = 0
a5 = 0
print(str(len(sys.argv)))

if len(sys.argv) > 3:
    a3 = sys.argv[3]

if len(sys.argv) > 4:
    a4 = sys.argv[4]

if len(sys.argv) > 5:
    a5 = sys.argv[5]

try:
    action = actions[sys.argv[1]]
except KeyError:
    print(f'Unknown option {sys.argv[1]}', file=sys.stderr)
    for option in actions.keys(): print(option)
    sys.exit(1)
except IndexError:
    print('Supported options: ')
    for option in actions.keys(): print(option)
    sys.exit(2)

try:
    print(action())
except IndexError as ex:
    print(f'\nOption {sys.argv[1]} needs an argument. Please look at the code.\n\n')
    traceback.print_exception(type(ex), ex, ex.__traceback__)
    sys.exit(3)
