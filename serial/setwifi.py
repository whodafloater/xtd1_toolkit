#!python3
import serial
import threading

port = 'COM19'
command = 'M2001 "TP-LINK_9BE2" "12345678"\n'

ser = serial.Serial(port, 230400, timeout=0.1)
print(f'sending: {command}')
ser.write(bytearray(command, 'ascii'))

stop = False
def serial_poll():
    global stop
    while True:
        a = str(ser.readline())
        if a != "b''": print('read result:' + a)
        if 'M2001' in a: stop = True
        if stop: return

print("Press Ctrl-C to stop polling. Waiting for IP address reply...")
t = threading.Thread(target=serial_poll)
t.start()

try:
   while True:
      if stop: break
except KeyboardInterrupt:
   stop = True

print("wait for polling thread to finish")
t.join()
print("all done")
