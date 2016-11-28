"""

  Filename: LoginServer.py
  Created by: DuckyDuck1553 (07Nov14)

"""

from lib.server.base import MiniServer
from lib.coginvasion.distributed.CogInvasionMsgTypes import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from lib.coginvasion.uber import LoginTokenGenerator
from pandac.PandaModules import *
import json
import hashlib
from passlib.handlers.pbkdf2 import pbkdf2_sha256

CLIENT_MD5 = 0
SERVER_MD5 = 1
REQUEST_BASE_LINK = 101
BASE_LINK = 102
STORE_LOGIN_TOKEN = 100
SERVER_MSG = 103
SERVER_VERSION = "1.0.17"

messages = {'tmaotc': 'At this time, only %d account(s) can be created on each computer.',
    'tmait': 'At this time, Cog Invasion Online only allows a total of %d game account(s) to be created. This amount has already been reached. We apologize for the inconvenience.',
    'cwog': "NOTICE (as of 10/11/15): If you previously had Cog Invasion Online installed on your computer, you MUST COMPLETELY uninstall the old version, and install the new one at http://download.coginvasion.com/installers/setup.exe\n(if you haven't done so already)",
    'ciac': 'Thank you for being apart of the Cog Invasion Online alpha. The server will be taken offline on Sunday, December 6, 2015, at 11:59 PM, Eastern Standard Time. Check the website for more information.'}

baseLink = "http://download.coginvasion.com/"

class LoginServer(MiniServer.MiniServer):
    version = 1.4

    def __init__(self, dataFileName = 'astron/databases/astrondb/loginAccData'):
        MiniServer.MiniServer.__init__(self, "localhost", 7033, 402000000, "login")
        self.connectToServer(7031)
        self.accInfoFile = None
        self.jsonAccInfo = None
        self.accountLimit = args.acc_limit
        self.accLimitPerComp = args.acc_limit_per_comp
        self.filePath = dataFileName + ".json"
        self.openJSONFile()

    def getAccountLimit(self):
        return int(self.accountLimit)

    def getAccountLimitPerComp(self):
        return int(self.accLimitPerComp)

    def isTotalAccountLimitReached(self):
        return self.getTotalAccounts() >= self.getAccountLimit()

    def getTotalAccounts(self):
        return len(self.jsonAccInfo)

    def canMakeNewAccount(self, mac):
        numAccs = 0
        for accountData in self.jsonAccInfo.values():
            if accountData.get("mac", None) == mac:
                numAccs += 1
        if numAccs >= self.getAccountLimitPerComp():
            return False
        return True

    def handleConnected(self):
        MiniServer.MiniServer.handleConnected(self)
        #dg = PyDatagram()
        #dg.addServerHeader(MiniServer.UBERDOG_CHANNEL, self.channel, STORE_LOGIN_TOKEN)
        #dg.addString("TEST_TOKEN")
        #dg.addString("0.0.0.0")
        #self.cWriter.send(dg, self.serverConnection)
        #print "Sent out a test login token to an uberDOG at: " + str(MiniServer.UBERDOG_CHANNEL)

    def openJSONFile(self):
        self.accInfoFile = open(self.filePath, "r")
        self.jsonAccInfo = json.load(self.accInfoFile)

    def flushData(self, data = None):
        if data:
            file = open(self.filePath, "w+")
            file.write(json.dumps(data))
            file.close()
        self.accInfoFile.flush()

    def handleDatagram(self, datagram):
        print "I got a datagram."
        dgi = DatagramIterator(datagram)
        connection = datagram.getConnection()
        address = datagram.getAddress()
        msgType = dgi.getUint16()
        print msgType
        if msgType == ACC_VALIDATE:
            name = dgi.getString()
            password = dgi.getString()
            self.validateAccount(name, password, connection, address)
        elif msgType == ACC_CREATE:
            name = dgi.getString()
            password = dgi.getString()
            mac = dgi.getString()
            self.createAccount(name, password, mac, connection)
        elif msgType == CLIENT_MD5:
            self.__handleClientMD5(dgi, connection)
        elif msgType == DL_TIME_REPORT:
            self.__handleDownloadTimeReport(dgi, datagram.getAddress())
        elif msgType == LAUNCHER_VERSION:
            self.__handleLauncherVersion(dgi, connection)
        elif msgType == FETCH_DL_LIST:
            self.__handleFetchDLList(connection)
        elif msgType == REQUEST_BASE_LINK:
            self.__handleBaseLinkRequest(connection)

    def __handleBaseLinkRequest(self, connection):
        print "Got a baseLink request"
        dg = PyDatagram()
        dg.addUint16(BASE_LINK)
        dg.addString(baseLink)
        self.cWriter.send(dg, connection)

    def __handleFetchDLList(self, connection):
        dg = PyDatagram()
        dg.addUint16(DL_LIST)
        dg.addString(baseLink)
        dg.addUint8(len(fileNames))
        for fileName in fileNames:
            dg.addString(fileName)
        self.cWriter.send(dg, connection)

    def __handleLauncherVersion(self, dgi, connection):
        version = dgi.getFloat64()
        dg = PyDatagram()
        if version == self.version:
            dg.addUint16(LAUNCHER_GOOD)
        else:
            dg.addUint16(LAUNCHER_BAD)
        self.cWriter.send(dg, connection)

    def __handleDownloadTimeReport(self, dgi, address):
        print "----------DOWNLOAD TIME----------"
        print "From: " + str(address)
        print "Total download time: " + str(dgi.getFloat64()) + " seconds."

    def __handleClientMD5(self, dgi, connection):
        filename = dgi.getString()
        clientmd5 = dgi.getString()
        servermd5 = hashlib.md5(open(filename).read()).hexdigest()
        self.sendServerMD5(servermd5, connection)

    def sendServerMD5(self, md5, connection):
        dg = PyDatagram()
        dg.addUint16(SERVER_MD5)
        dg.addString(md5)
        self.cWriter.send(dg, connection)

    def createAccount(self, name, password, mac, connection):
        name = name.lower()
        print "Attemping to create account: %s, %s" % (name, password)
        if self.jsonAccInfo.has_key(name):
            print "Account already exists: %s, %s" % (name, password)
            self.sendAccountExists(connection)
            return
        elif not self.canMakeNewAccount(mac):
            print "Too many accounts have been created on this computer."
            self.sendServerMessage('tmaotc', connection, self.getAccountLimitPerComp())
            return
        elif self.isTotalAccountLimitReached():
            print "The game's total account limit has already been reached."
            self.sendServerMessage('tmait', connection, self.getAccountLimit())
            return
        print "Hashing password..."
        hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
        self.jsonAccInfo[name] = {"password": hash, "mac": mac}
        self.flushData(self.jsonAccInfo)
        self.sendAccountCreated(connection)
        print "Created account: %s, %s" % (name, password)

    def sendAccountCreated(self, connection):
        dg = PyDatagram()
        dg.addUint16(ACC_CREATED)
        self.cWriter.send(dg, connection)

    def sendAccountExists(self, connection):
        dg = PyDatagram()
        dg.addUint16(ACC_EXISTS)
        self.cWriter.send(dg, connection)

    def isValidAccount(self, name, password):
        accExists = self.jsonAccInfo.has_key(name)
        if accExists:
            acc = self.jsonAccInfo.get(name)
            hash = acc.get('password')
            if pbkdf2_sha256.verify(password, hash):
                return True
            else:
                return False
        else:
            return False

    def validateAccount(self, name, password, connection, address):
        name = name.lower()
        print "I'm validating an account with credidentials: %s, %s" % (name, password)
        if self.isValidAccount(name, password):
            self.sendValidAccount(connection, address)
        else:
            self.sendInvalidAccount(connection)

    def sendValidAccount(self, connection, address):
        print "The account is valid."
        dg = PyDatagram()
        dg.addUint16(ACC_VALID)
        dg.addString("gameserver.coginvasion.com:7032")
        dg.addString(SERVER_VERSION)
        token = LoginTokenGenerator.generateLoginToken(str(address))
        dg.addString(token.getToken())
        self.sendNewLoginToken(token.getToken(), str(address))
        self.cWriter.send(dg, connection)

    def sendNewLoginToken(self, token, address):
        # Tell an uberdog to store a new login token for a potential client.
        dg = PyDatagram()
        dg.addServerHeader(MiniServer.UBERDOG_CHANNEL, self.channel, STORE_LOGIN_TOKEN)
        dg.addString(token)
        dg.addString(address)
        self.cWriter.send(dg, self.serverConnection)

    def sendInvalidAccount(self, connection):
        print "The account is invalid."
        dg = PyDatagram()
        dg.addUint16(ACC_INVALID)
        self.cWriter.send(dg, connection)

    def sendServerMessage(self, message, connection, formatting = None):
        dg = PyDatagram()
        dg.addUint16(SERVER_MSG)
        if formatting:
            dg.addString(messages[message] % formatting)
        else:
            dg.addString(messages[message])
        self.cWriter.send(dg, connection)

LoginServer()
