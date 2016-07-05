"""

  Filename: MiniServer.py
  Created by: DuckyDuck1553 (08Nov14)

"""

from panda3d.core import *
from pandac.PandaModules import *
ConfigVariableString("window-type", "none").setValue("none")
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.task import Task
from direct.distributed.MsgTypes import *
from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionReader, ConnectionWriter, QueuedConnectionListener, NetAddress
#from direct.showbase.ShowBase import *
#base = ShowBase()

IM_THE_ACC_SERVER = 1
IM_THE_DL_SERVER = 2

UBERDOG_CHANNEL = 1000000

class MiniServer:

    def __init__(self, host, port, channel, serverType):
        self.port = port
        self.host = host
        self.channel = channel
        self.serverType = serverType
        self.Connections = {}
        self.startConnectionMgr()
        self.locked = 0
        #base.taskMgr.add(self.displayServerStatusTask, "displayServerStatus")
        return

    def connectToServer(self, port):
        # Connect our MiniServer to the main server.
        self.serverConnection = self.cMgr.openTCPClientConnection(self.host,
                            port, 5000)
        if self.serverConnection:
            self.cReader.addConnection(self.serverConnection)
            self.handleConnected()

    def handleConnected(self):
        self.registerChannel()

    def registerChannel(self):
        dg = PyDatagram()
        dg.addServerControlHeader(CONTROL_ADD_CHANNEL)
        dg.addChannel(self.channel)
        self.cWriter.send(dg, self.serverConnection)
        print "Registered channel: " + str(self.channel)

    def setLocked(self, value):
        if value:
            self.locked = 1
        elif not value:
            self.locked = 0

    def displayServerStatusTask(self, task):
        self.displayServerStatus()
        task.delayTime = 30
        return Task.again

    def displayServerStatus(self):
        print "-----------------------------------"
        print "Server Status..."
        print "Host: %s" % self.host
        print "Port: %s" % self.port
        print "Number of active connections: %s" % len(self.Connections)

    def startConnectionMgr(self):
        self.cMgr = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cMgr, 0)
        self.cReader = QueuedConnectionReader(self.cMgr, 0)
        self.cWriter = ConnectionWriter(self.cMgr, 0)
        self.tcpSocket = self.cMgr.openTCPServerRendezvous('', self.port, 10)
        self.cListener.addConnection(self.tcpSocket)
        taskMgr.add(self.listenerPoll, "listenForConnections", -39)
        taskMgr.add(self.datagramPoll, "listenForDatagrams", -40)
        taskMgr.add(self.disconnectionPoll, "listenForDisconnections", -41)
        print "%s server started." % self.serverType.capitalize()

    def listenerPoll(self, task):
        """ Listen for connections. """
        if not self.locked:
            if self.cListener.newConnectionAvailable():
                print "-----------------------------------"
                print "New connection available..."
                rendezvous = PointerToConnection()
                netAddress = NetAddress()
                newConnection = PointerToConnection()
                if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                    newConnection = newConnection.p()
                    self.Connections[str(newConnection.this)] = rendezvous
                    self.cReader.addConnection(newConnection)
                    print "IP Address: %s" % newConnection.getAddress()
                    print "ConnectionID: %s" % newConnection.this
                    self.displayServerStatus()
                    #if self.__class__.__name__ == 'LoginServer':
                     #   self.sendServerMessage('ciac',
                      #                         newConnection)
        return Task.cont

    def datagramPoll(self, task):
        if self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                self.handleDatagram(datagram)
        return Task.cont

    def disconnectionPoll(self, task):
        if self.cMgr.resetConnectionAvailable():
            connectionPointer = PointerToConnection()
            self.cMgr.getResetConnection(connectionPointer)
            lostConnection = connectionPointer.p()
            print "-----------------------------------"
            print "Farewell connection..."
            print "IP Address: %s" % lostConnection.getAddress()
            print "ConnectionID: %s" % lostConnection.this
            del self.Connections[str(lostConnection.this)]
            self.cMgr.closeConnection(lostConnection)
            self.displayServerStatus()
        return Task.cont
