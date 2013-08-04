#!/usr/bin/python

import socket
import serial
import time
import fcntl, sys, os
import errno
import random
import time

ARDUINO_ERROR = "Arduino doesn't connected\n";
port = 12345                # Reserve a port for your service.
userId = 13
adruinoUpdated = True;

def updateSerWithRecvData(s, ser):
    updateMsg = getRecvData(s)
    if(updateMsg != None):
        if(updateMsg.startswith("min")):
            global adruinoUpdated
            adruinoUpdated = False
        ser.write(updateMsg)
        ser.flush()
        time.sleep(1.5)


def readSerial(s):
    isOpened = True
    while True:
        try:
            ser = serial.Serial('/dev/tty.usbserial-AH01GOI0',9600,timeout=4)
            ser.close()
            ser.open()
        except:
            isOpened = False
            print ARDUINO_ERROR

        if isOpened == True:
            while True:  # serial port is open
                updateSerWithRecvData(s, ser)

                try:
                    data = ser.readline();
                    ser.flush()
#                    print data
                    global adruinoUpdated
                    if(adruinoUpdated and data.startswith("data:")):
                        ts = str(int(time.time()))
                        fullData = str(userId) +';' + ts + ";" + data[len("data:") :]
                        s.send(fullData)
                    elif(data.startswith("Ready")): #calibration data already updated on arduino
                        adruinoUpdated = True
                    elif(data.startswith("command:")): #received command from arduino
                        ts = str(int(time.time()))
                        fullData = str(userId) +';' + ts + "&" + data[len("command:") :]
                        s.send(fullData)
                    else:
                        s.send("ignore the data") #keep connection

                except IOError as e:
                    print "I/O error({0}): {1}".format(e.errno, e.strerror)
                    print ARDUINO_ERROR
                    ser.close()
                    ser.open()
                except:
                    print "Unexpected error:", sys.exc_info()[0]

def getRecvData(s):
    try:
        msg = s.recv(4096)
    except socket.error, e:
        err = e.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBOCK:
            time.sleep(1)
#            print 'No data available'
        else:
            # a "real" error occurred
            print e
            sys.exit(1)
    else:
        return msg


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
    #    s.settimeout(2)
    host = socket.gethostname() # Get local machine name

    s.connect(('127.0.0.1', port))
    fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)
    #    print s.recv(1024)

    readSerial(s)

    s.close




