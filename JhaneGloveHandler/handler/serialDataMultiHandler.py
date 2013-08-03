from __future__ import print_function

import asyncore
import collections
import logging
import socket
import time

import MySQLdb

userId = '13'

MAX_MESSAGE_LENGTH = 1024
host = 'localhost'
port = 12345

db = MySQLdb.connect(host="localhost",
    user="root",
    passwd="",
    db="glow")

# you must create a Cursor object. It will let
#  you execute all the query you need
cursor = db.cursor()

selectUserDataSql = """SELECT minValuesList, maxValuesList, isDirt FROM JhaneGlove_userdata WHERE userId = %s"""
updateUserDataDirtBitSql = """UPDATE JhaneGlove_userdata SET isDirt=%s WHERE userId = %s"""


insertSql = """INSERT INTO JhaneGlove_serialrawdata(userId, time, data)
                VALUES (%s, %s, %s)"""



class RemoteClient(asyncore.dispatcher):

    """Wraps a remote client socket."""

    def __init__(self, host, socket, address):
        asyncore.dispatcher.__init__(self, socket)
        self.host = host
        self.outbox = collections.deque()

    def say(self, message):
        self.outbox.append(message)

    def handle_read(self):
        client_message = self.recv(MAX_MESSAGE_LENGTH)
        print (client_message)
        if client_message:
            lines = client_message.split("\n")
            for row in lines:
                if row:
                    try:
                        vals = row.split(";") #TODO check the length of array -> case of partial data
                        if(len(vals) == 3):
                            cursor.execute(insertSql, (vals[0], vals[1], vals[2]))
                            db.commit()
                    except MySQLdb.Error, e:
                        print ("An error has been passed. %s" %e)
                        db.rollback()
#        self.host.broadcast(client_message)
        self.host.check_for_client_updates()

    def handle_write(self):
        if not self.outbox:
            return
        message = self.outbox.popleft()
        print (message)
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError('Message too long')
        self.send(message)

class Host(asyncore.dispatcher):

    log = logging.getLogger('Host')
    count = 0
    stepCounter = 0

    def __init__(self, address=(host, port)):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.listen(1)
        self.remote_clients = []

    def handle_accept(self):
        socket, addr = self.accept() # For the remote client.
        self.log.info('Accepted client at %s', addr)
        self.remote_clients.append(RemoteClient(self, socket, addr))

    def handle_read(self):
        self.log.info('Received message: %s', self.read())


    def broadcast(self, message):
        self.log.info('Broadcasting message: %s', message)
        for remote_client in self.remote_clients:
            remote_client.say(message)

    def check_for_client_updates(self):
        if(self.stepCounter >2):
            self.stepCounter =0;
            cursor.execute(selectUserDataSql, (userId))
            data=cursor.fetchone()    #fetchall()
            if(data == None):
                return
            minValuesList = data[0]
            maxValuesList = data[1]
            isDirt = data[2]
            message = None

#            isDirt ==1 : calibration started => send "start" event to arduino
#            isDirt ==2 : "start" event already sent to arduino => if minValuesList ready, send to arduino
#            isDirt ==3 : minValuesList already sent to arduino => if maxValuesList ready, send to arduino

            if(isDirt == 1):
                message = "calStart\n"
                cursor.execute(updateUserDataDirtBitSql, (2, userId))  #update flag
            elif(isDirt == 2 and minValuesList != None):
                message = "min:" + minValuesList.replace('"', '') + "\n"
                cursor.execute(updateUserDataDirtBitSql, (3, userId))  #update flag
            elif(isDirt == 3 and minValuesList != None):
                message ="max:" + maxValuesList.replace('"', '')  + "\n"
                cursor.execute(updateUserDataDirtBitSql, (0, userId))  #update flag

            if(message != None):
                self.broadcast(message)
        self.stepCounter+=1

def main():

    # Use all the SQL you like
#    cur.execute("SELECT * FROM JhaneGlove_cell")
#
#    for row in cur.fetchall():
#        print (row[0])

    logging.basicConfig(level=logging.INFO)
    logging.info('Looping')
    logging.info('Creating host')
    host = Host()
    asyncore.loop()


