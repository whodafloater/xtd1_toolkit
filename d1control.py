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

ip = '192.168.0.106'

actions = {
    '--status':       lambda: machine.get_status(),
    '--stop':         lambda: machine.stop(),
    '--gcode':        lambda: machine.execute_gcode_command(' '.join(sys.argv[2:])),
    '--test':         lambda: machine.test(a[0], a[1], a[2], a[3]),
    '--cutfile':      lambda: machine.cutfile_upload(filename),
    '--framefile':    lambda: machine.framefile_upload(filename),
}

a = []
action_key = ''
filename = ''
   
#print(f'num args = {len(sys.argv)}')
while len(sys.argv) > 0:
   arg = sys.argv.pop(0)
#   print(arg)
   if arg == '--ip':
      ip = sys.argv.pop(0)
      continue

   # this consumes all the remaining args
   if arg == '--test':
      action_key = arg
      while len(sys.argv) > 0:
         a.append(sys.argv.pop(0))

   if arg == '--cutfile' or arg == '--framefile':
      action_key = arg
      filename = sys.argv.pop(0)
      continue

# machine.test requires 4 args
while len(a) < 4:
   a.append(0)

#print(f'action_key = {action_key}')
#print(a)

try:
    machine = XTD1(IP=ip)
    action = actions[action_key]
except KeyError:
    print(f'Unknown option {action}', file=sys.stderr)
    for option in actions.keys(): print(option)
    sys.exit(1)
except IndexError:
    print('Supported options: ')
    for option in actions.keys(): print(option)
    sys.exit(2)

try:
    # call the lambda fn and print the result
    print(action())
except IndexError as ex:
    print(f'\nERROR: Option {action_key} {a[0]} needs argument(s). Please look at the code.\n\n')
    traceback.print_exception(type(ex), ex, ex.__traceback__)
    sys.exit(3)
