"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LauncherLoginManager.py
@author Brian Lach
@date December 8, 2014

"""

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
import os

class LauncherLoginManager(DistributedObjectGlobal):
	
	def __init__(self, cr):
		DistributedObjectGlobal.__init__(self, cr)
		return
		
	def d_requestLogin(self, username, password):
		self.sendUpdate("requestLogin", [username, password])
		
	def loginAccepted(self, token):
		os.system("set LOGIN_TOKEN=" + str(token))
		messenger.send("loginAccepted")
		
	def loginRejected(self):
		messenger.send("loginRejected")
