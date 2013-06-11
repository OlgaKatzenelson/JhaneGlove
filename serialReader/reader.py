import os
import serial
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

if isOpened == True:
    while True:
         # open serial port
        try:
            f.write(ser.readline())
    #             print self.
        except:
            print "Arduino doesn't connected"
            f.write("Arduino doesn't connected\n")
            ser.close()
            ser.open()
        f.flush()

    f.close()
# 	while True:
# 		words = ser.readline().split()
# 		print(words[1])
# 		#for word in words:
# 	        # prints each word on a line
# 		#	print(word)
#
# 	ser.close()