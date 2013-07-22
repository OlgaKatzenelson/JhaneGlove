import os
import serial
import sys
import random
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print('----------------------- ;) ')

path = os.path.dirname(os.path.dirname(__file__)) + '/serialReader/data.txt'
f = open( path, 'w' )

isOpened = True
try:
    ser = serial.Serial('/dev/tty.usbserial-AH01GOI0',9600,timeout=1)
    ser.close()
    ser.open()
except:
    isOpened = False
    print "Arduino doesn't connected"
    f.write("Arduino doesn't connected\n")
    f.flush()
#    ARDUINO_ERROR = "Arduino doesn't connected\n";

if isOpened == True:
    while True:
         # open serial port
        try:
            data = ser.readline();
#            data = "o g o g g {0}\n".format(random.randint(0, 4))
            f.write(data)
    #             print self.
        except:
            print "Arduino doesn't connected"
            f.write("Arduino doesn't connected\n")
            ser.close()
            ser.open()
        f.flush()

    f.close()

#        time.sleep(10)






# 	while True:
# 		words = ser.readline().split()
# 		print(words[1])
# 		#for word in words:
# 	        # prints each word on a line
# 		#	print(word)
#
# 	ser.close()