"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LoginServerConnection.py
@author Maverick Liberty
@date July 28, 2016

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from LoginToken import LoginToken
import socket
import thread
import threading

uberRepo = None

SRV_CREATE_TOKEN = 0
SRV_NTWK_MESSAGE = 1

class LoginServerConnection:
    notify = directNotify.newCategory('LoginServerConnection')
    
    def __init__(self, repository, port):
        self.server = None
        
        self.socket = socket.socket()
        self.socket.bind(('localhost', port))
        self.socket.listen(5)
        self.closeRequested = False
        
        thread.start_new_thread(self.handleConnection, ())
        self.notify.info('Successfully started LoginServerConnection Server!')
        
        global uberRepo
        uberRepo = repository
        
    def handleConnection(self):
        while not self.closeRequested:
            socket, ipAddress = self.socket.accept()
            threading.Thread(target = self.handleClient, args = (socket, ipAddress)).start()
        self.socket.close()
        
    def handleClient(self, socket, ipAddress):
        self.notify.info('Opened a connection!')
        while not self.closeRequested:
            data = []
            for s in socket.recv(2048).splitlines():
                s = s.strip()
                
                if len(data) == 0:
                    # The very first line is going to be the id of the datagram.
                    # Some weird ASCII characters begin the lines, so let's just use the
                    # last character of the first line because our ids range from [0-9].
                    s = s[-1]
                    
                    try:
                        int(s)
                        data.append(s)
                    except ValueError:
                        # This means that what we got wasn't an int
                        pass
                else:
                    data.append(s)
            
            if len(data) > 0:
                datagramId = int(data[0])
                
                if datagramId == SRV_CREATE_TOKEN:
                    ipAddress = data[1]
                    token = data[2]
                    self.generateToken(ipAddress, token)
                elif datagramId == SRV_NTWK_MESSAGE:
                    message = data[1]
                    self.sendNetworkMessage(message)
            
    def generateToken(self, ipAddress, token):
        global uberRepo
        uberRepo.storeToken(LoginToken(token, ipAddress))
        self.notify.info('Stored token %s for IP: %s' % (token, ipAddress))
    
    def sendNetworkMessage(self, message):
        global uberRepo
        uberRepo.csm.d_networkMessage(message)
        self.notify.info('Login Server published this network message: {0}.'.format(message))
        
    def close(self):
        self.closeRequested = True
