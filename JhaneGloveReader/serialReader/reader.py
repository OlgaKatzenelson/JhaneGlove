#!/usr/bin/python

import socket
import serial
import time
import sys
import random
import time

ARDUINO_ERROR = "Arduino doesn't connected\n";

def readSerial(s):
    isOpened = True
    while True:
        try:
            ser = serial.Serial('/dev/tty.usbserial-AH01GOI0',9600,timeout=1)
            ser.close()
            ser.open()
        except:
            isOpened = False
            print ARDUINO_ERROR

        if isOpened == True:
            while True:
                 # open serial port
                try:
                    data = ser.readline();
                    ts = str(int(time.time()))
                    fullData = '1;' + ts + ";" + data
                    s.send(fullData)
                except:
                    print ARDUINO_ERROR
                    ser.close()
                    ser.open()




def main():
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 12346                # Reserve a port for your service.

    s.connect(('127.0.0.1', port))
#    print s.recv(1024)

#    s.send("1;1234;kyky1\n");
#    s.send("1;333333;kyky2\n");
    readSerial(s)

    s.close
# 	while True:
# 		words = ser.readline().split()
# 		print(words[1])
# 		#for word in words:
# 	        # prints each word on a line
# 		#	print(word)
#
# 	ser.close()




