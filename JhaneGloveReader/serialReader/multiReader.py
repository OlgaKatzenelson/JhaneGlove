#!/usr/bin/python
from __future__ import print_function

import asyncore
import collections
import logging
import socket
import serial
import time

MAX_MESSAGE_LENGTH = 1024
ARDUINO_ERROR = "Arduino doesn't connected\n";

def readSerial(client):
    isOpened = True
    while True:
        try:
            ser = serial.Serial('/dev/tty.usbserial-AH01GOI0',38400,timeout=1)
            ser.close()
            ser.open()
        except:
            isOpened = False
            print (ARDUINO_ERROR)

        if isOpened == True:
            while True:
            # open serial port
                try:
                    data = ser.readline();
                    ts = str(int(time.time()))
                    fullData = '1;' + ts + ";" + data
#                    client.say(fullData)
                    client.say("kuk" + ts)
                except:
                    print (ARDUINO_ERROR)
                    ser.close()
                    ser.open()



class Client(asyncore.dispatcher):

    def __init__(self, host_address, name):
        asyncore.dispatcher.__init__(self)
        self.log = logging.getLogger('Client (%7s)' % name)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        self.log.info('Connecting to host at %s', host_address)
        self.connect(host_address)
        self.outbox = collections.deque()

    def say(self, message):
        self.outbox.append(message)
        self.log.info('Enqueued message: %s', message)

    def handle_write(self):
        if not self.outbox:
            return
        message = self.outbox.popleft()
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError('Message too long')
        self.send(message)

#    def handle_read(self):
#        message = self.recv(MAX_MESSAGE_LENGTH)
#        self.log.info('Received message: %s', message)

def getData():
    return str(int(time.time()))

def main():
    logging.basicConfig(level=logging.INFO)
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 12345                # Reserve a port for your service.

    client = Client(('127.0.0.1', 12345), 'Alice')
    i = 5
#    while (i>0):
##        client.say("Kyyyyyy\n");
#        client.say("11111111111111111111\n")
#        i= i-1

#    client.say("Kyyyyyy1\n");
#    client.say("Kyyyyyy2\n");
#    client.say("Kyyyyyy3\n");
#    readSerial(client)
    while True:
        client.say("11111111111111111111\n")
        asyncore.loop()
#        time.sleep(10)

    logging.info('Looping')
    asyncore.loop()


