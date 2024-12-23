# xTool D1 Toolkit

inspired by https://github.com/fritzw/xtm1_toolkit

## d1control.py

### --framefile, Framing File Upoad
   python d1control.py --ip 192.168.0.106 --framefile ~/tmp/myshape.gcode

1. Read and parse a gcode file to determine the laser cutting extents.
2. Generates framing gcode
3. uploads to the X-Tool D1 as a framing file (blue blinking LED)

At this point, a human can press the D1 button over and over to watch the
machine move around.

This framing file differs from the creative space faming file.
* The laser head covers the actual cutting extents
* The red LED cross hair parks at the gcode origin 0,0

Why do you care? Because the head must move 17mm to the left of the cross hair
to bore a hole at 0,0. This framing code will bump into the frame rails if they are in the way. The Creative space framer wont do that until your actually cutting.

### --cutfile, Cutting File Upoad
   python d1control.py --ip 192.168.0.106 --cutfile ~/tmp/myshape.gcode

1. uploads to the X-Tool D1 as a cutting file (green steady LED)

At this point, a human can press the D1 button over and over to watch the
machine move around and make smoke.
* Wear you glasses
* Put the machine outside


### --test




Various tests to reverse engineer the D1 control model

    python d1control.py --test status
    python d1control.py --test state
    python d1control.py --test cross on
    python d1control.py --test cross off
    python d1control.py --test x+
    python d1control.py --test x-
    python d1control.py --test xy 20 30

Pulse laser:

    python d1control.py --test laser on 1000 30

File loading, test boxes:

    python d1control.py --test frame 40 30
    python d1control.py --test cut 40 30

File loading, real files. The D1 does not change the gcode or laser response
to the Gcode. The difference between a frame file and a cut file is the 
way the one button user interface on the machine behaves.
If you load a "frame" file with the laser basting at 100% it will obey.

    python d1control.py --test fileframe name.gcode
    python d1control.py --test filecut   name.gcode
