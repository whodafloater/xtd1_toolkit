# MIT License
#
# inspired by xTool M1 code from https://github.com/fritzw/xtm1_toolkit
# Copyright (c) 2022 Fritz Webering
#
# This xTool D1 hack:
# Copyright (c) 2023 Tom Gray
#
# various tests to reverse engineer the D1 control model
#
#   python d1control.py --status
#   python d1control.py --test status
#   python d1control.py --test state
#   python d1control.py --test cross on
#   python d1control.py --test cross off
#
# pulse laser:
#   python d1control.py --test laser on 1000 30
#
# file loading:
#   python d1control.py --test frame 40 30
#   python d1control.py --test cut 40 30

#
from genericpath import exists
import io
import requests
import json
import time
import re
import math

class XTD1:

    def __init__(self, IP='201.234.3.1') -> None:
        self.IP = IP
        self.PORT = 8080
        self.CAMERA_PORT = 8329

    def get_status(self):
        self.test('status', 0, 0, 0)
        return 

    def stop(self):
        return self._get_request('/cnc/data?action=stop')

    def execute_gcode_command(self, gcode):
        timestamp = int(time.time() * 1000)
        gcode = gcode.replace(' ', '%20')
        print(gcode)
        return self._get_request(f'/cmd?cmd={gcode}&t={timestamp}')

    def _post_request(self, url, port=None, **kwargs) -> bytes:
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        if port is None: port = self.PORT
        full_url = f'http://{self.IP}:{port}{url}'
        result = requests.post(full_url, headers=headers, timeout=10, **kwargs)
        if result.status_code != 200:
            raise RuntimeError(f'Device returned HTTP status {result.status_code} for POST {full_url}')
        return result.content

    def _get_request(self, url, port=None, **kwargs) -> bytes:
        if port is None: port = self.PORT
        full_url = f'http://{self.IP}:{port}{url}'
        print('url: ' + full_url)
        result = requests.get(full_url, timeout=10, **kwargs)
        if result.status_code != 200:
            print('status: ' + str(result.status_code))
            #raise RuntimeError(f'Device returned HTTP status {result.status_code} for GET {full_url}')
        return result.content

    def blast(self, s):
        for x in s:
            print(x);
            reply = self._get_request(x).decode('utf-8')
            print(reply)

    def test(self, test_arg, a3, a4, a5):

        looks_like_on  = ['on', 'ON', '1', True]
        looks_like_off = ['off', 'OFF', '0', False]

        print('test_arg=' + test_arg);

        # 9007199254740991 = 2^53 - 1
        # max safe integer for representaion in double precision floating point
        #
        # red cross state when machine is idle
        # M97  S0  red cross on when no program is running
        # M97  S1  red cross off when no program is running
        #
        # red cross state when program is running.
        # M106 S1  red cross on, laser stays off regardless of power setting
        # M106 S0  red cross off
        #
        # M9    pulse laser on
        # S     power, S30 -> 3%, S1000 -> 100%
        # N     laser pulse duration in milliseconds
        #       xcs uses 2^53-1 to turn on the laser "forever"
        #
        # M17   enable steppers
        # S     S0 max drive ?
        #       S1 weaker ?
        #       bigger the S, weaker the holding power.
        #       I cant repeat what I think i saw with the S parameter...
        #
        #
        # M18   disable stepper drivers
        #
        # M106
        # M205+X432+Y403    set machine limits ?
        # M101
        # 
        # S    speed, controls laser dutycycle
        #        S30   ->   3%
        #        S1000 -> 100%
        # F    feed rate 
        #        F1000   1000mm/min = 16.7mm/sec
        #
        # both of these work:
        # M3 S30  set power for G1 moves
        # G1 S30  set power for G1 moves
        #
        # G0 F3000 set feedrate for G0 moves (rapid, laser off)
        # G1 F600  set feedrate for G1 moves (cut, laser on)
        #
        # G92  vector from part 0,0 to tool tip
        #
        # G90  absolute programming
        # G91  incremental programming
        #
        # G1   linear interpolation move. F and S are
        #      sticky from the last G1.
        #      Laser is only on during the move
        #
        # G0   rapid move. Laser off, F is sticky from
        #      last G0

        # Separator? These all work. %20 is url encoded " ".
        #    M9S100N1000
        #    M9+S100+N1000
        #    M9,S100,N1000
        #    M9%20S100%20N1000
        #
        # You cannot combine move in a single command.
        # This results in movement to 0, 0 only.
        # The first X,Y are ignored (or just overwritten)
        #    G0 X100 Y30 F2000 G0 X0 Y0
        # Same for G1

        if test_arg == 'v':
            s = ['/system?action=version',
             '/system?action=version_v2',
             '/system?action=mac',
             '/system?action=get_dev_name',
             '/getlaserpowertype',
             '/system?action=dotMode',
             '/system?action=get_working_sta',
             '/peripherystatus',
             '/system?action=offset',
            ]
            self.blast(s)

        if test_arg == 'x+':
            s = [
                 '/cmd?cmd=M17+S1',
                 '/cmd?cmd=G92+X0+Y0',
                 '/cmd?cmd=G90',
                 '/cmd?cmd=G1+X20+F3000+S0',
                ]
            self.blast(s)

        if test_arg == 'x-':
            s = [
                 '/cmd?cmd=M17+S1',
                 '/cmd?cmd=G92+X0+Y0',
                 '/cmd?cmd=G90',
                 '/cmd?cmd=G1+X-20+F3000+S0',
                ]
            self.blast(s)

        # move relative
        if test_arg == 'xy':
            xloc = int(a3)
            yloc = int(a4)
            s = [
                 '/cmd?cmd=M17+S1',
                 '/cmd?cmd=G92+X0+Y0',
                 '/cmd?cmd=G90',
                 '/cmd?cmd=G1+X' + str(xloc) + '+Y' + str(yloc) + '+F3000+S0',
                ]
            self.blast(s)

        # pulse the laser
        # time in milliseconds
        # Example: 500mS, 3%
        #    python d1control.py --test laser on 500 30
        if test_arg == 'laser':
            if a3 in looks_like_on:
                time = int(a4)
                power = int(a5)

                # limit to 10% for testing
                if power > 100:
                    power = 100

                s = ['/cmd?cmd=M9 S' + str(power) + 'N' + str(time),]
            else:
                s = ['/cmd?cmd=M9+S0+N0',]

            self.blast(s)


        if test_arg == 'loff':
            s = ['/cmd?cmd=M9+S0+N0',]
            self.blast(s)


        if test_arg == 'cross':
            if a3 in looks_like_on:
               s = ['/cmd?cmd=M97 S0',]
            else:
               s = ['/cmd?cmd=M97 S1',]

            self.blast(s)


        if test_arg == 'stepper':
            s = [
                 '/cmd?cmd=M17',
                 '/cmd?cmd=G0 X100 Y0 F8000',
                 '/cmd?cmd=G0 X0 Y0    F8000',
                 '/cmd?cmd=',
                ]
            self.blast(s)

        # laser power is constant during G1 moves
        # laser only lights during move
        # M17 enable steppers. S1 ??
        if test_arg == 'box':
            s = [
                 '/cmd?cmd=M17 S1',
                 '/cmd?cmd=M106 S0',
                 '/cmd?cmd=G92 X-30 Y-30',
                 '/cmd?cmd=G90',
                 '/cmd?cmd=G0 X0 Y0 F3000',
                 '/cmd?cmd=G1 X10 F1000 S20',
                 '/cmd?cmd=G1 Y10 F1000 S30',
                 '/cmd?cmd=G1 X0 F1000 S20',
                 '/cmd?cmd=G1 Y0 F1000 S10',
                 '/cmd?cmd=G0 X-30 Y-30 F3000',
                 '/cmd?cmd=M18',
               ]
            self.blast(s)
            return;

        # {"result":"ok","working":"0"}   machine is idle, led is green
        # {"result":"ok","working":"2"}   led is blue. machine is framing, or cutting
        #                                 at the mercy of its tmp.gcode file
        #                                 could be paused (short press)
        # if the state is 2 then xTool creative will not its own "process"
        if test_arg == 'state':
            self.blast({'/system?action=get_working_sta',});
            return

        # {"result":"ok","status":"normal", "sdCard":1}
        # {"result":"ok","status":"normal", "sdCard":0}
        #    sdCard value only updates after power cycle
        if test_arg == 'status':
            self.blast({'/peripherystatus',});
            return

        # kick the machine out of state 2, when tyoe=0 framing only.
        # deletes the tmp.gcode file ...
        # has no effect when processing a type=1 cut file
        if test_arg == 'abort':
            self.blast({'/cmd?cmd=M108',});
            return

        # tmp.gcode file remains.
        # can be restarted with button press.
        if test_arg == 'stop':
            self.blast(['/cnc/data?action=stop','/cmd?cmd=M9+S0+N0']);
            return

        # filetype=0
        # working state goes to 2 after file post
        # short press starts program
        # hope you didn't mess up because it will run to completion.
        # button does not do anything
        # working state stays at 2 forever
        #
        # If you power cycle, state goes back to 0
        # Then the file behaves like a type 1
        # where short press, long press are pause and abort.

        # if red cross is enabled (M106) then it will stay on during
        # gcode run and laser remains off. 
        if test_arg == 'frame':
            redspotter = 1
            gc = self.gcbox(a3, a4, redspotter, 4000, 30)
            print(gc);

            files = {'file': ('tmp.gcode', gc)}
            url = '/cnc/data?filetype=0'
            full_url = f'http://{self.IP}:{self.PORT}{url}'
            result = requests.post(full_url, files=files)

            print(result)
            return

        # filetype=1
        # working state stays at 0 after file post
        # press button to start
        # working state goes to 2
        # short press pause
        # long press cancel
        # short press, repeat
        #
        # working state goes to 0 when program is finished
        if test_arg == 'cut':
            gc = self.gcbox(a3, a4, 0, 1000, 30)
            print(gc);

            files = {'file': ('tmp.gcode', gc)}
            url = '/cnc/data?filetype=1'
            full_url = f'http://{self.IP}:{self.PORT}{url}'
            result = requests.post(full_url, files=files)

            print(result)
            return

        if test_arg == 'fileframe':
            filename = a3
            files = {'file': ('tmp.gcode', open(filename, 'rb'))}
            url = '/cnc/data?filetype=1'
            full_url = f'http://{self.IP}:{self.PORT}{url}'
            result = requests.post(full_url, files=files)
            print(result)
            return

        if test_arg == 'filecut':
            filename = a3
            files = {'file': ('tmp.gcode', open(filename, 'rb'))}
            url = '/cnc/data?filetype=1'
            full_url = f'http://{self.IP}:{self.PORT}{url}'
            result = requests.post(full_url, files=files)
            print(result)
            return


        return

    def gcbox(self, xs, ys, cross, feed, power):
       xsize = float(xs)
       ysize = float(ys)

       # 5% max for testing
       if power > 50:
         power = 50

       x1 = 10
       x2 = x1 + xsize
       y1 = 10
       y2 = y1 + ysize

       gc =  "M17 S1\n"
       gc += f"M106 S{cross}\n"
       gc += "M205 X426 Y403\n"
       gc += "M101\n"
       gc += "G92 X0 Y0\n"
       gc += "G90\n"
       gc += f"G1 F{feed}\n"
       gc += "G0 F3000\n"
       gc += f"G1 S{power}\n"

       gc += f"G0 X{x1} Y{y1}\n"
       gc += f"G1 X{x2} Y{y1}\n"
       gc += f"G1 X{x2} Y{y2}\n"
       gc += f"G1 X{x1} Y{y2}\n"
       gc += f"G1 X{x1} Y{y1}\n"

       gc += "G0 X0 Y0\n"
       gc += "M18\n"
       return gc


if __name__ == '__main__':
    d1 = XTD1()
    print(d1.get_status())
