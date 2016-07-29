########################################
# Filename: LoginServerConnection.py
# Created by: DecodedLogic (28Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify
from threading import Thread
from LoginToken import LoginToken
import SocketServer

uberRepo = None

class LoginServerConnectionHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):
        self.data = [s.strip() for s in self.request.recv(1024).splitlines()]
        tokenIP = self.data[0][2:len(self.data[0])]
        token = self.data[1]
        self.request.sendall('%s %s' % (tokenIP, token))
        
        # Let's store the token we received.
        loginToken = LoginToken(token, tokenIP)
        global uberRepo
        uberRepo.storeToken(loginToken)
        print 'Stored token %s' % token

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
