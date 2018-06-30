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

class LoginServerConnectionHandler(SocketServer.BaseRequestHandler):
    notify = directNotify.newCategory('LoginServerConnectionHandler')
    
    def handle(self):
        # Java gets very upset whenever this method returns.
        while True:
            self.data = []
            try:
                for s in self.request.recv(1024).splitlines():
                    self.data.append(s.strip())
                
                tokenIP = self.data[0][2:len(self.data[0])]
                token = self.data[1]
                self.request.sendall('%s %s' % (tokenIP, token))
                
                # Let's store the token we received.
                loginToken = LoginToken(token, tokenIP)
                
                global uberRepo
                uberRepo.storeToken(loginToken)
                self.notify.debug('Stored token %s for IP: %s' % (token, tokenIP))
            except Exception:
                self.notify.warning('Client disconnected while processing login token data.')
                return

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
