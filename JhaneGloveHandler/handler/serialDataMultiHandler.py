from __future__ import print_function

import asyncore
import collections
import logging
import socket

import MySQLdb


MAX_MESSAGE_LENGTH = 1024

db = MySQLdb.connect(host="localhost",
    user="root",
    passwd="",
    db="glow")

# you must create a Cursor object. It will let
#  you execute all the query you need
cursor = db.cursor()

sql = """INSERT INTO raw_data(user_id,
         time, data)
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
                        cursor.execute(sql, (vals[0], vals[1], vals[2]))
                        db.commit()
                    except MySQLdb.Error, e:
                        print ("An error has been passed. %s" %e)
                        db.rollback()
#        self.host.broadcast(client_message)

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

    def __init__(self, address=('localhost', 12346)):
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
#        for remote_client in self.remote_clients:
#            remote_client.say(message)


def main():

    # Use all the SQL you like
#    cur.execute("SELECT * FROM JhaneGlove_cell")
#
#    for row in cur.fetchall():
#        print (row[0])

    logging.basicConfig(level=logging.INFO)
    logging.info('Creating host')
    host = Host()
#    logging.info('Creating clients')
#    print (host.getsockname())
#    alice = Client(host.getsockname(), 'Alice')
#    bob = Client(host.getsockname(), 'Bob')
#    alice.say('Hello, everybody!')
    logging.info('Looping')
    asyncore.loop()


