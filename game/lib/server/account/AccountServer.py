"""

  Filename: AccountServer.py
  Created by: DuckyDuck1553 (07Nov14)
  
"""

from lib.server.base.MiniServer import MiniServer
from lib.toontown.distributed.CogInvasionMsgTypes import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import *
import json

class LoginServer(MiniServer):
	
	def __init__(self, dataFileName = 'astron/databases/astrondb/loginAccData'):
		MiniServer.__init__(self, "localhost", 7033, "login")
		self.accInfoFile = None
		self.jsonAccInfo = None
		self.filePath = dataFileName + ".json"
		self.openJSONFile()
		
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
		msgType = dgi.getUint16()
		print msgType
		if msgType == ACC_VALIDATE:
			name = dgi.getString()
			password = dgi.getString()
			doId = dgi.getUint32()
			self.validateAccount(name, password, connection, doId)
		elif msgType == ACC_CREATE:
			name = dgi.getString()
			password = dgi.getString()
			self.createAccount(name, password, connection)
		elif msgType == TDB_REQ_TOON_INFO:
			name = dgi.getString()
			password = dgi.getString()
			doId = dgi.getUint32()
			self.handleToonInfoReq(name, connection, doId)
		elif msgType == TDB_REQ_DEL_TOON:
			name = dgi.getString()
			doId = dgi.getUint32()
			slot = dgi.getUint8()
			self.handleToonDelReq(name, connection, doId, slot)
		elif msgType == TDB_REQ_NEW_TOON:
			accName = dgi.getString()
			accPass = dgi.getString()
			dnaStrand = dgi.getString()
			slot = dgi.getUint8()
			avName = dgi.getString()
			doId = dgi.getUint32()
			if self.isValidAccount(accName, accPass):
				self.handleNewToonReq(accName, accPass, dnaStrand, slot, avName)
				self.sendToonCreated(doId, connection)
			else:
				self.sendInvalidAccount(doId, connection)
		elif msgType == ENTER_GAME_REQ:
			doId = dgi.getUint32()
			self.sendEnterGameResp(connection, doId)
			
	def sendEnterGameResp(self, connection, doId):
		dg = PyDatagram()
		dg.addUint16(ENTER_GAME_RESP)
		dg.addUint32(doId)
		self.cWriter.send(dg, connection)
				
	def handleNewToonReq(self, accName, accPass, dnaStrand, slot, avName):
		print "Storing toon data on account (%s, %s) with data (%s, %s, %s)" % (
				accName, accPass, dnaStrand, slot, avName
				)
		self.jsonAccInfo.get(accName).get("toons").update({"toon" + str(slot):
					{"dna": dnaStrand, "slot": slot, "name": avName}})
		self.flushData(self.jsonAccInfo)
		
	def sendToonCreated(self, doId, connection):
		dg = PyDatagram()
		dg.addUint16(TDB_NEW_TOON_CREATED)
		dg.addUint32(doId)
		self.cWriter.send(dg, connection)
			
	def handleToonDelReq(self, name, connection, doId, slot):
		print "Deleting toon on slot %s for account %s from doId %s, connection %s" %(
				slot, name, doId, connection.getAddress())
		self.jsonAccInfo.get(name).get("toons").update({"toon" + str(slot): {}})
		self.flushData(self.jsonAccInfo)
		self.sendToonDeleted(doId, connection)
		
	def sendToonDeleted(self, doId, connection):
		dg = PyDatagram()
		dg.addUint16(TDB_TOON_DELETED)
		dg.addUint32(doId)
		self.cWriter.send(dg, connection)

	def handleToonInfoReq(self, name, connection, doId):
		numAvs = 0
		avatars = {}
		for i in range(6):
			acc = self.jsonAccInfo.get(name)
			toonnum = "toon" + str(i)
			toons = acc.get("toons")
			toon = toons.get(toonnum)
			dna = toon.get("dna")
			avname = toon.get("name")
			avatars[toonnum] = {"name": "", "dna": "", "slot": 0}
			avatars[toonnum]["name"] = avname
			avatars[toonnum]["dna"] = dna
			avatars[toonnum]["slot"] = i
			numAvs += 1
			if dna == None or avname == None:
				del avatars[toonnum]
				numAvs -= 1
		dg = PyDatagram()
		dg.addUint16(TDB_TOON_INFO)
		dg.addUint32(doId)
		dg.addUint8(numAvs)
		for av in range(6):
			toonnum = "toon" + str(av)
			if avatars.get(toonnum) != None:
				dg.addUint8(avatars[toonnum]["slot"])
				dg.addString(avatars[toonnum]["dna"])
				dg.addString(avatars[toonnum]["name"])
		self.cWriter.send(dg, connection)
			
	def createAccount(self, name, password, connection):
		print "Attemping to create account: %s, %s" % (name, password)
		if self.jsonAccInfo.has_key(name):
			print "Account already exists: %s, %s" % (name, password)
			self.sendAccountExists(connection)
			return
		self.jsonAccInfo[name] = {"password": password, "toons": {"toon0": {},
						"toon1": {}, "toon2": {}, "toon3": {},
						"toon4": {}, "toon5": {}}}
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
			if password == acc.get('password'):
				return True
			else:
				return False
		else:
			return False
		
	def validateAccount(self, name, password, connection, doId):
		print "I'm validating an account with credidentials: %s, %s" % (name, password)
		if self.isValidAccount(name, password):
			self.sendValidAccount(connection, doId)
		else:
			self.sendInvalidAccount(connection, doId)
			
	def sendValidAccount(self, connection, doId):
		print "The account is valid."
		dg = PyDatagram()
		dg.addUint16(ACC_VALID)
		dg.addUint32(doId)
		self.cWriter.send(dg, connection)
		
	def sendInvalidAccount(self, connection, doId):
		print "The account is invalid."
		dg = PyDatagram()
		dg.addUint16(ACC_INVALID)
		dg.addUint32(doId)
		self.cWriter.send(dg, connection)
		
AccountServer()
run()
