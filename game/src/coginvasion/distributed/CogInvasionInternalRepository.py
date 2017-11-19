"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CogInvasionInternalRepository.py
@author Brian Lach
@date December 10, 2014

"""

from direct.distributed.AstronInternalRepository import AstronInternalRepository
from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.distributed.CogInvasionDoGlobals import DO_ID_COGINVASION

class CogInvasionInternalRepository(AstronInternalRepository):
	notify = directNotify.newCategory("CIInternalRepository")
	GameGlobalsId = DO_ID_COGINVASION
	dbId = 4003
	
	def readerPollUntilEmpty(self, task):
		#try:
		return AstronInternalRepository.readerPollUntilEmpty(self, task)
		"""
		except Exception as e:
			self.handleCrash(e)
		return task.done"""
	
	def handleCrash(self, e):
		pass
	
	def handleConnected(self):
		self.netMessenger.register(0, 'avatarOnline')
		self.netMessenger.register(1, 'avatarOffline')
	
	def getAccountIdFromSender(self):
		return (self.getMsgSender() >> 32) & 0xFFFFFFFF
		
	def getAvatarIdFromSender(self):
		return self.getMsgSender() & 0xFFFFFFFF
