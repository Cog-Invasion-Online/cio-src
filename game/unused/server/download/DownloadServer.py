""" The download server for Cog Invasion Online. """

from lib.server.base.MiniServer import MiniServer
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import *
import hashlib

CLIENT_MD5 = 0
SERVER_MD5 = 1

class DownloadServer(MiniServer):
	
	def __init__(self):
		MiniServer.__init__(self, "gameserver.coginvasion.com", 7031, "download")
		self.connectToServer(7032)
		self.sendWhoIAm()
				
	def handleDatagram(self, datagram):
		print "-----------------------------------"
		print "Recieved datagram from %s..." % datagram.getConnection()
		dgi = DatagramIterator(datagram)
		type = dgi.getUint16()
		if type == CLIENT_MD5:
			self.handleClientMD5(dgi, datagram)
			
	def handleClientMD5(self, dgi, datagram):
		file = dgi.getString()
		if ".." in file:
			file = "../Panda3D-Toontown/direct/distributed/ClientRepository.py"
		md5 = dgi.getString()
		server_md5 = hashlib.md5(open(file).read()).hexdigest()
		self.sendServerMD5(server_md5, datagram.getConnection())
		
	def sendServerMD5(self, md5, connection):
		pkg = PyDatagram()
		pkg.addUint16(SERVER_MD5)
		pkg.addString(md5)
		self.cWriter.send(pkg, connection)
		
DownloadServer()
run()
