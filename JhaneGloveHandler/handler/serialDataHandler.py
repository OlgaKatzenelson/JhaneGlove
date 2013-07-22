#!/usr/bin/python           # This is server.py file

import socket               # Import socket module

def main():
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 12345                # Reserve a port for your service.
    s.bind((host, port))        # Bind to the port

    s.listen(5)                 # Now wait for client connection.
    while True:
        conn, addr = s.accept()     # Establish connection with client.
        print 'Got connection from', addr
        conn.send('Thank you for connecting')

#        data = conn.recv(1024)
#        print data

        while 1:
            data = conn.recv(1024)
            if data:
                print data


#            if not data: break
#            conn.send(data)

        conn.close()                # Close the connection