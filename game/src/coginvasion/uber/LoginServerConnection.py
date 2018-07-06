"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LoginServerConnection.py
@author Maverick Liberty
@date July 28, 2016

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from threading import Thread
from LoginToken import LoginToken
import SocketServer

uberRepo = None

SRV_CREATE_TOKEN = 0
SRV_NTWK_MESSAGE = 1

class LoginServerConnectionHandler(SocketServer.BaseRequestHandler):
    notify = directNotify.newCategory('LoginServerConnectionHandler')
    
    def handle(self):
        # Java gets very upset whenever this method returns.
        while True:
            self.data = []
            try:
                for s in self.request.recv(2048).splitlines():
                    s = s.strip()
                    
                    if len(self.data) == 0:
                        s = s[-1]
                    
                    self.data.append(s)
                
                print self.data
                
                if len(self.data) > 0:
                    datagramId = int(self.data[0])
                    
                    if datagramId == SRV_CREATE_TOKEN:
                        ipAddress = self.data[1]
                        token = self.data[2]
                        self.generateToken(ipAddress, token)
                    elif datagramId == SRV_NTWK_MESSAGE:
                        message = self.data[1]
                        self.sendNetworkMessage(message)
            except Exception:
                self.notify.warning('Client disconnected while processing login token data.')
                return
    
    def generateToken(self, ipAddress, token):
        global uberRepo
        uberRepo.storeToken(LoginToken(token, ipAddress))
        self.notify.debug('Stored token %s for IP: %s' % (token, ipAddress))
    
    def sendNetworkMessage(self, message):
        global uberRepo
        uberRepo.csm.d_networkMessage(message)
        self.notify.debug('Sent network message!')

class LoginServerConnection:
    notify = directNotify.newCategory('LoginServerConnection')
    
    def __init__(self, repository, port):
        self.server = None
        Thread(target = self.startServer, args = (port,)).start()
        self.notify.info('Successfully started LoginServerConnection Server!')
        
        global uberRepo
        uberRepo = repository
        
    def startServer(self, port):
        self.server = SocketServer.TCPServer(('localhost', port), LoginServerConnectionHandler)
        self.server.serve_forever()
    
    def close(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
