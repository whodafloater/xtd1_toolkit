# Exploring the X-Tool Serial port

Yes, it does support some GRBL thru the  serial port.

![screenshot](media/serialsender1.png "XTool serial sender/reader")

Put on a cpp hat and do some Qt

The Qt "Blocking Master Example" was tweaked get some useful interaction with the X-Tool D1.

* [Qt Blocking Master Doc] [qtdoc]
* [Qt example source code] [qtgit]

## Adjustments to Suit X-Tool

  * Baudrate: 230400
  * command terminator is a newline, 0x0a

Without the newline terminator the XTool does nothing.

Code snippets from senderthread.cpp:

        // serial port setup for XTool D1
        serial.setBaudRate(230400);
        serial.setParity(QSerialPort::NoParity);
        serial.setDataBits(QSerialPort::Data8);
        serial.setFlowControl(QSerialPort::NoFlowControl);
        serial.setStopBits(QSerialPort::OneStop);

        // XTool D1 commands require a newline terminator
        requestData.append(0x0a);


## To build and run blockingsender

To get a log on the console, build the debug version. 

        cd blockingsender
        qmake
        make debug

And, run it:

        debug/blockingsender.exe


Some sample debug output:
    
        sent:  "?\n"
                     recv:  "ok\n<MPos:0.000000,0.000000,0.000000,0.000000>\n"
        sent:  "\n"
                     recv:  "ok\n"
        sent:  "$I\n"
                     recv:  "[xTool D1:ver 40.30.009.01 B7]\nok\n"
        sent:  "\n"
                     recv:  "ok\n"
        sent:  "$H\n"
                     recv:  "ok\n"
        sent:  "\n"
                     recv:  "start_home x \r\nleft limit trigged\r\nstart_home y \r\nup limit trigged\r\n<MPos:0.000000,0.000000,0.000000>\nM28\nok\n"
        sent:  "\n"
                     recv:  "ok\n"
        sent:  "$I\n"
                     recv:  "ok\n[xTool D1:ver 40.30.009.01 B7]\n"



[qtdoc]: <https://doc.qt.io/qt-5/qtserialport-blockingmaster-example.html>
[qtgit]: <https://github.com/qt/qtserialport/tree/dev/examples/serialport/blockingsender>
