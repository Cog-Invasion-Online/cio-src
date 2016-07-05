"""
  
  Filename: ToontownConnectionManager.py
  Created by: blach (17June14)
  
"""

from lib.toontown.globals import CIGlobals 
from lib.toontown.online.OnlineGlobals import *
from direct.distributed.MsgTypesCMU import MsgName2Id
from pandac.PandaModules import *
from panda3d.core import *
from direct.actor.Actor import *
from lib.toontown.gui.Dialog import *
from direct.task import Task
from direct.showbase.Transitions import *
from direct.directnotify.DirectNotify import *
from direct.showbase import Audio3DManager
import sys
import os
import random

connectionNotify = DirectNotify().newCategory("ToontownConnectionManager")

it = loader.loadFont("phase_3/models/fonts/ImpressBT.ttf")
dialog_box = loader.loadModel("phase_3/models/gui/dialog_box_gui.bam")
dialog_btns = loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam")
fade = loader.loadModel("phase_3/models/misc/fade.bam")

host = base.config.GetString('server-address')
port = base.config.GetString('server-port')
url = URLSpec("http://%s:%s" % (host, port))

class ToontownConnectionManager:
	def __init__(self, cr):
		self.cr = cr
		
		base.accept("readyToConnect", self.createMenu, extraArgs=['connecting'])
		
		self.files_updated = None
		self.fade_img = None
		self.msg_dialog = None
		
	def createMenu(self, menuType, reason=None):
		self.currentMenu = menuType
		if self.msg_dialog:
			self.msg_dialog.cleanup()
			self.msg_dialog = None
		dialogText = ''
		dialogStyle = 0
		dialogEvent = ""
		if menuType == 'connecting':
			dialogText = CIGlobals.ConnectingMsg
			self.cr.connect([url], self.connectionSuccess, [], self.createMenu, ['noConnection'])
		elif menuType == 'joining':
			dialogText = CIGlobals.JoiningMsg
		elif menuType == 'died':
			aspect2d.show()
			render2d.show()
			dialogText = CIGlobals.SuitDefeatMsg
			dialogStyle = 1
			dialogEvent = "defeatRestart"
		elif menuType == 'outdated_files':
			dialogText = CIGlobals.OutdatedFilesMsg
			dialogStyle = 3
			dialogEvent = "disconnectOk"
		elif menuType == 'joinFailure':
			taskMgr.remove("handleNoCommunication")
			dialogText = CIGlobals.JoinFailureMsg
			dialogStyle = 3
			dialogEvent = "disconnectOk"
		elif menuType == 'disconnected':
			dialogText = CIGlobals.DisconnectionMsg
			dialogStyle = 3
			dialogEvent = "disconnectOk"
		elif menuType == 'noConnection':
			connectionNotify.warning("Unable to connect to gameserver, notifying user.")
			dialogText = CIGlobals.NoConnectionMsg
			dialogStyle = 2
			dialogEvent = "retryConnection"
		elif menuType == 'booted':
			dialogText = CIGlobals.BootedMsg
			dialogStyle = 2
			dialogEvent = "retryBooted"
		elif menuType == 'locked':
			connectionNotify.warning("server is locked, notifying user.")
			taskMgr.remove("handleNoCommunication")
			dialogText = CIGlobals.ServerLockedMsg
			dialogStyle = 2
			dialogEvent = "retryLocked"
		if dialogEvent != '':
			base.acceptOnce(dialogEvent, self.handleDialogEvent, [dialogEvent])
		self.msg_dialog = GlobalDialog(message = dialogText, style = dialogStyle, doneEvent = dialogEvent)
		self.msg_dialog.show()
		base.graphicsEngine.renderFrame()
		base.graphicsEngine.renderFrame()
		
	def handleDialogEvent(self, event):
		value = self.msg_dialog.doneStatus
		if value == "ok":
			value = 1
		elif value == "cancel":
			value = 0
		else:
			value = -1
		if event == "retryConnection" or event == "retryBooted":
			if value:
				self.createMenu("connecting")
		elif event == "retryLocked":
			if value:
				self.cr.sendDisconnect()
				self.createMenu("connecting")
				render.show()
				base.enableAllAudio()
		elif event == "retryDefeated":
			if value:
				self.msg_dialog.cleanup()
				messenger.send("enterPickAToon")
		if not value or event == "disconnectOk":
			sys.exit(0)
		
	def connectionSuccess(self):
		self.cr.askServerInfo()
		base.accept("serverLocked", self.createMenu)
		base.accept("serverUnlocked", self.checkVersion)
		base.accept("serverFull", self.handleFullServer)
		taskMgr.doMethodLater(16, self.handleNoCommunication, "handleNoCommunication")
		
	def joinGame(self):
		self.createMenu("joining")
		
	def continueIntoGame(self):
		taskMgr.remove("handleNoCommunication")
		self.msg_dialog.cleanup()
		messenger.send("enterPickAToon")
		base.accept("died", self.createMenu, extraArgs=["died"])
		taskMgr.add(self.monitorConnection, "monitorConnection")

	def handleNoCommunication(self, task):
		if not self.currentMenu == "locked":
			# We've waited 16 seconds with still no response
			# from the server.
			connectionNotify.warning("No response from server.")
			self.createMenu("joinFailure")
		return task.done
		
	def monitorConnection(self, task):
		if self.cr.isConnected()==0:
			messenger.send("lostConnection")
			self.createMenu('disconnected')
			return task.done
		return task.cont
		
	def handleFullServer(self):
		base.ignore("serverLocked")
		base.ignore("serverUnlocked")
		taskMgr.remove("downloadTask")
		taskMgr.remove("handleNoCommunication")
		self.createMenu("booted", reason="Server is full.")
		
	def checkVersion(self):
		self.joinGame()
		connectionNotify.info("Checking if files are up to date...")
		self.http = HTTPClient()
		self.channel = self.http.makeChannel(True)
		self.channel.beginGetDocument(DocumentSpec(CIGlobals.GameVersionURL))
		self.rf = Ramfile()
		self.channel.downloadToRam(self.rf)
		taskMgr.add(self.downloadTask, "downloadTask")
		
	def downloadTask(self, task):
		if self.channel.run():
			return task.cont
		if not self.channel.isDownloadComplete():
			connectionNotify.warning("could not check server version.")
			self.createMenu('joinFailure')
			return task.done
		data = self.rf.getData()
		if not data == open("gameversion.txt", "r").read():
			connectionNotify.warning("Files are out of date, cannot proceed into game.")
			taskMgr.remove("handleNoCommunication")
			self.createMenu('outdated_files')
		else:
			connectionNotify.info("Files are up to date, proceeding into game...")
			self.continueIntoGame()
		return task.done
