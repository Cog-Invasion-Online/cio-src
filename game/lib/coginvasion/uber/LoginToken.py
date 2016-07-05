"""

  Filename: LoginToken.py
  Created by: DuckyDuck1553 (08Dec14)

"""

class LoginToken:
	
	def __init__(self, token, ip):
		self.setToken(token)
		self.setIP(ip)
		self.deleteTask = "disactivateToken-" + str(id)
		
	def getDeleteTask(self):
		return self.deleteTask
		
	def setToken(self, token):
		self.token = token
		
	def getToken(self):
		return self.token
		
	def setIP(self, ip):
		self.ip = ip
		
	def getIP(self):
		return self.ip
		
	def cleanup(self):
		del self.token
		del self.ip
		del self.deleteTask
