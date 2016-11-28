""" This file includes the ServerGui class, the user interface for the Cog Invasion Online Server. """

from pandac.PandaModules import *
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.gui.DirectGui import *
from lib.toontown.globals import ToontownGlobals

class ServerGui:
	
	def __init__(self):
		self.bg = None
		self.sysmsg_entry = None
		self.sysMsg_btn = None
		self.kick_btn = None
		self.grant_btn = None
		self.suits_btn = None
		self.invPage = 0
		self.connections = -1 # We don't want the AI to be included in our active connections, so we'll set the default value to -1.
		self.highestConnectionCount = -1 # The highest number of clients we've had online at the same time.
		self.guiFSM = ClassicFSM('Server', [State('off', self.enterOff, self.exitOff),
								State('sysMsg', self.enterSysMsg, self.exitSysMsg),
								State('suits', self.enterSuits, self.exitSuits),
								State('kick', self.enterKick, self.exitKick),
								State('grant', self.enterGrant, self.exitGrant)], 'off', 'off')
		self.createGui()
		return
		
	def newConnection(self):
		self.connections += 1
		self.connection_lbl['text'] = "Clients: %s" % self.connections
		if self.connections > self.highestConnectionCount:
			self.highestConnectionCount = self.connections
			self.highest_client_lbl['text'] = "Highest Client Count: %s" % self.highestConnectionCount
		
	def disconnection(self):
		self.connections -= 1
		self.connection_lbl['text'] = "Clients: %s" % self.connections
		
	def createGui(self):
		self.sgui = loader.loadModel("lib/server/game/server_gui.egg")
		
		self.bg = OnscreenImage(image=self.sgui.find('**/gui_background'), parent=render2d, scale=2)
		self.bg.setTransparency(True)
		
		self.connection_lbl = DirectLabel(text="Clients: %s" % self.connections, scale=0.08, text_fg=(1,1,1,1),
										text_shadow=(0,0,0,1), pos=(1.0, 0, 0.805), relief=None)
										
		self.highest_client_lbl = DirectLabel(text="Highest Client Count: %s" % self.highestConnectionCount, relief=None,
											scale=0.08, text_fg=(1,1,1,1), text_shadow=(0,0,0,1), pos=(0.075, 0, 0.92))
		
		self.lock_btn = DirectButton(geom=(self.sgui.find('**/unlocked'),
										self.sgui.find('**/locked'),
										self.sgui.find('**/locked'),
										self.sgui.find('**/unlocked')), relief=None, 
									geom_scale=0.15, geom1_scale=0.17, geom2_scale=0.17, command=self.lockServer, pos=(0.6, 0, 0.89))
		
		self.sysMsg_btn = DirectButton(text="SysMsg", scale=0.08, pos=(-1.08, 0.0, 0.80),
									command=self.guiFSM.request, extraArgs=['sysMsg'])	
		self.kick_btn = DirectButton(text="Kick", scale=0.093, pos=(-0.84, 0.0, 0.785),
									command=self.guiFSM.request, extraArgs=['kick'])					
		self.grant_btn = DirectButton(text="Grant", scale=0.1, pos=(-0.605, 0.0, 0.785),
									command=self.guiFSM.request, extraArgs=['grant'])					
		self.suits_btn = DirectButton(text="Suits", scale=0.094, pos=(-0.35, 0.0, 0.785),
									command=self.guiFSM.request, extraArgs=['suits'])
									
	def lockServer(self):
		base.sr.serverLocked = 1
		print "Server is locked."
		self.lock_btn['geom'] = (self.sgui.find('**/locked'),
								self.sgui.find('**/unlocked'),
								self.sgui.find('**/unlocked'),
								self.sgui.find('**/locked'))
		self.lock_btn['command'] = self.unlockServer
		
	def unlockServer(self):
		base.sr.serverLocked = 0
		print "Server is unlocked."
		self.lock_btn['geom'] = (self.sgui.find('**/unlocked'),
								self.sgui.find('**/locked'),
								self.sgui.find('**/locked'),
								self.sgui.find('**/unlocked'))
		self.lock_btn['command'] = self.lockServer
		
	def destroyGui(self):
		self.bg.destroy()
		self.bg = None
		
	def enterOff(self):
		pass
		
	def exitOff(self):
		pass
		
	def enterSysMsg(self):
		self.sysmsg_entry = DirectEntry(initialText="System Message...", scale=0.055, width=15,
									numLines=4, command=base.air.sendSysMessage, pos=(-0.4, 0, 0))
		self.regUpdate5Min_btn = DirectButton(text="Update: Reg\n5 Min", scale=0.08, pos=(-0.7, 0, 0.3),
									command=base.air.sendSysMessage, extraArgs=[ToontownGlobals.UpdateReg5Min])
		self.regUpdate1Min_btn = DirectButton(text="Update: Reg\n1 Min", scale=0.08, pos=(-0.7, 0, 0.0),
									command=base.air.sendSysMessage, extraArgs=[ToontownGlobals.UpdateReg1Min])
		self.regUpdateClosed_btn = DirectButton(text="Update: Reg\nClosed", scale=0.08, pos=(-0.7, 0, -0.3),
									command=base.air.sendSysMessage, extraArgs=[ToontownGlobals.UpdateRegClosed])
		self.emgUpdate5Min_btn = DirectButton(text="Update: Emg\n5 Min", scale=0.08, pos=(0.7, 0, 0.3),
									command=base.air.sendSysMessage, extraArgs=[ToontownGlobals.UpdateEmg5Min])
		self.emgUpdate1Min_btn = DirectButton(text="Update: Emg\n1 Min", scale=0.08, pos=(0.7, 0, 0.0),
									command=base.air.sendSysMessage, extraArgs=[ToontownGlobals.UpdateEmg1Min])
		self.emgUpdateClosed_btn = DirectButton(text="Update: Emg\nClosed", scale=0.08, pos=(0.7, 0, -0.3),
									command=base.air.sendSysMessage, extraArgs=[ToontownGlobals.UpdateEmgClosed])
									
	def exitSysMsg(self):
		self.sysmsg_entry.destroy(); self.sysmsg_entry = None
		self.regUpdate5Min_btn.destroy(); self.regUpdate5Min_btn = None
		self.regUpdate1Min_btn.destroy(); self.regUpdate1Min_btn = None
		self.regUpdateClosed_btn.destroy(); self.regUpdateClosed_btn = None
		self.emgUpdate5Min_btn.destroy(); self.emgUpdate5Min_btn = None
		self.emgUpdate1Min_btn.destroy(); self.emgUpdate1Min_btn = None
		self.emgUpdateClosed_btn.destroy(); self.emgUpdateClosed_btn = None
		
	def enterSuits(self):
		if base.config.GetBool('want-suits', True):
			self.invPage = 0
			self.suitA_btn = DirectButton(text="Suit-A", scale=0.1, pos=(-0.5, 0, 0.6), command=base.air.createSuit,
										extraArgs=["A", None, None, 1, base.air.skeleton])
			self.suitB_btn = DirectButton(text="Suit-B", scale=0.1, pos=(0, 0, 0.6), command=base.air.createSuit,
										extraArgs=["B", None, None, 1, base.air.skeleton])
			self.suitC_btn = DirectButton(text="Suit-C", scale=0.1, pos=(0.5, 0, 0.6), command=base.air.createSuit,
										extraArgs=["C", None, None, 1, base.air.skeleton])
										
			self.skeleton_btn = DirectButton(text="Skeletons Off", scale=0.1, pos=(0, 0, 0.4), command=self.enableSkeletons)
			if base.air.skeleton == 1:
				self.skeleton_btn['text'] = 'Skeletons On'
				self.skeleton_btn['command'] = self.disableSkeletons
			self.autosuits_btn = DirectButton(text="Auto-Suits Off", scale=0.1, pos=(0.75, 0, -0.6), command=self.enableAutoSuits)
			if base.air.automaticSuits == 1:
				self.autosuits_btn['text'] = 'Auto-Suits On'
				self.autosuits_btn['command'] = self.disableAutoSuits
			self.tournament_btn = DirectButton(text="Tournament", scale=0.1, pos=(0, 0, -0.6), command=self.startTournament)
			self.kill_btn = DirectButton(text="Kill All Suits", scale=0.1, pos=(-0.75, 0, -0.6), command=base.air.killAllSuits)
			self.vp_btn = DirectButton(text="Vice President", scale=0.1, pos=(0, 0, -0.4), command=self.spawnVP)				
			if base.config.GetBool('want-suit-invasions', True):
				self.invasion_btn = DirectButton(text="Suit Invasion", scale=0.15, command=self.invasionOptions)
			
	def spawnVP(self):
		base.air.createSuit("A", "vp", "s", 0)
			
	def startTournament(self):
		base.air.tournament.initiateTournament()
			
	def enableAutoSuits(self):
		self.autosuits_btn['text'] = 'Auto-Suits On'
		self.autosuits_btn['command'] = self.disableAutoSuits
		base.air.enableAutoSuits()
		
	def disableAutoSuits(self):
		self.autosuits_btn['text'] = 'Auto-Suits Off'
		self.autosuits_btn['command'] = self.enableAutoSuits
		base.air.disableAutoSuits()
			
	def enableSkeletons(self):
		self.skeleton_btn['text'] = 'Skeletons On'
		self.skeleton_btn['command'] = self.disableSkeletons
		base.air.skeleton = 1
		self.updateSuitArgs()
		
	def disableSkeletons(self):
		self.skeleton_btn['text'] = 'Skeletons Off'
		self.skeleton_btn['command'] = self.enableSkeletons
		base.air.skeleton = 0
		self.updateSuitArgs()
		
	def updateSuitArgs(self):
		self.suitA_btn['extraArgs'] = ["A", None, None, 1, base.air.skeleton]
		self.suitB_btn['extraArgs'] = ["B", None, None, 1, base.air.skeleton]
		self.suitC_btn['extraArgs'] = ["C", None, None, 1, base.air.skeleton]
			
	def invasionOptions(self):
		if base.air.activeInvasion:
			return
		self.invPage = 1
		self.invasion_btn.hide()
		self.all_btn = DirectButton(text="All Suits", command=self.invasionSizeOptions, extraArgs=["ABC"], scale=0.1, pos=(0, 0, 0))
		self.a_btn = DirectButton(text="Suit A", command=self.invasionSizeOptions, extraArgs=["A"], scale=0.08, pos=(0.25, 0, -0.2))
		self.b_btn = DirectButton(text="Suit B", command=self.invasionSizeOptions, extraArgs=["B"], scale=0.08, pos=(0, 0, -0.2))
		self.c_btn = DirectButton(text="Suit C", command=self.invasionSizeOptions, extraArgs=["C"], scale=0.08, pos=(-0.25, 0, -0.2))
		
	def invasionSizeOptions(self, suit):
		self.invPage = 2
		base.air.suit = suit
		self.all_btn.destroy()
		self.a_btn.destroy()
		self.b_btn.destroy()
		self.c_btn.destroy()
		self.large_btn = DirectButton(text="Large", command=self.invasionDifficultyOptions, extraArgs=["large"], scale=0.125, pos=(-0.5, 0, 0))
		self.med_btn = DirectButton(text="Medium", command=self.invasionDifficultyOptions, extraArgs=["medium"], scale=0.1, pos=(0, 0, 0))
		self.small_btn = DirectButton(text="Small", command=self.invasionDifficultyOptions, extraArgs=["small"], scale=0.075, pos=(0.5, 0, 0))
		
	def invasionDifficultyOptions(self, size):
		self.invPage = 3
		base.air.size = size
		self.large_btn.destroy()
		self.med_btn.destroy()
		self.small_btn.destroy()
		self.mixed_btn = DirectButton(text="Mixed", command=self.beginInvasion, extraArgs=["all"], scale=0.135, pos=(0, 0, 0.15))
		self.hard_btn = DirectButton(text="Hard", command=self.beginInvasion, extraArgs=["hard"], scale=0.125, pos=(-0.5, 0, 0))
		self.normal_btn = DirectButton(text="Normal", command=self.beginInvasion, extraArgs=["normal"], scale=0.1, pos=(0, 0, 0))
		self.easy_btn = DirectButton(text="Easy", command=self.beginInvasion, extraArgs=["easy"], scale=0.075, pos=(0.5, 0, 0))
	
	def beginInvasion(self, difficulty):
		base.air.difficulty = difficulty
		if base.air.size == "large":
			base.air.invasionSize = 3
			taskMgr.add(base.air.startInvasion, "startLargeInvasion", extraArgs=[base.air.skeleton], appendTask=True)
		elif base.air.size == "medium":
			base.air.invasionSize = 2
			taskMgr.add(base.air.startInvasion, "startMedInvasion", extraArgs=[base.air.skeleton], appendTask=True)
		elif base.air.size == "small":
			base.air.invasionSize = 1
			taskMgr.add(base.air.startInvasion, "startSmallInvasion", extraArgs=[base.air.skeleton], appendTask=True)
		else:
			base.air.invasionSize = 0
			notify.warning("invalid size! Invasion will not start.")
		self.hard_btn.destroy()
		self.normal_btn.destroy()
		self.easy_btn.destroy()
		self.mixed_btn.destroy()
		self.invasion_btn.show()
		self.invPage = 0	
	
	def exitSuits(self):
		if base.config.GetBool('want-suits', True):
			self.suitA_btn.destroy(); self.suitA_btn = None
			self.suitB_btn.destroy(); self.suitB_btn = None
			self.suitC_btn.destroy(); self.suitC_btn = None
			self.skeleton_btn.destroy(); self.skeleton_btn = None
			self.autosuits_btn.destroy(); self.autosuits_btn = None
			self.tournament_btn.destroy(); self.tournament_btn = None
			self.kill_btn.destroy(); self.kill_btn = None
			self.vp_btn.destroy(); self.vp_btn = None
			if base.config.GetBool('want-suit-invasions', True):
				self.invasion_btn.destroy(); self.invasion_btn = None
				if self.invPage == 1:
					self.all_btn.destroy(); self.all_btn = None
					self.a_btn.destroy(); self.a_btn = None
					self.b_btn.destroy(); self.b_btn = None
					self.c_btn.destroy(); self.c_btn = None
				elif self.invPage == 2:
					self.large_btn.destroy(); self.large_btn = None
					self.med_btn.destroy(); self.med_btn = None
					self.small_btn.destroy(); self.small_btn = None
				elif self.invPage == 3:
					self.hard_btn.destroy(); self.hard_btn = None
					self.normal_btn.destroy(); self.normal_btn = None
					self.easy_btn.destroy(); self.easy_btn = None
					self.mixed_btn.destroy(); self.mixed_btn = None
		
	def enterKick(self):
		self.doId2kick_entry = DirectEntry(width=10, scale=0.12, pos=(-0.59, 0, 0.15), command=self.sendKickMessage)
		self.kickDoId_btn = DirectButton(text="Kick DoId", scale=0.12, pos=(0, 0, -0.15), command=self.sendKickMessage,
							extraArgs=[self.doId2kick_entry.get()])
							
	def sendKickMessage(self, textEntered):
		base.sb.sendKickMessage(self.doId2kick_entry.get())
		
	def exitKick(self):
		self.doId2kick_entry.destroy()
		self.kickDoId_btn.destroy()
		self.doId2kick_entry = None
		self.kickDoId_btn = None
		
	def enterGrant(self):
		if base.config.GetBool('want-admins', True):
			self.doId2grant_entry = DirectEntry(width=10, scale=0.12, pos=(-0.59, 0, 0.15), command=self.sendGrantMessage)
			self.grantDoId_btn = DirectButton(text="Grant DoId", scale=0.12, pos=(0, 0, -0.15), command=self.sendGrantMessage, extraArgs=[self.doId2grant_entry.get()])
		
	def sendGrantMessage(self, textEntered):
		base.sb.sendGrantMessage(self.doId2grant_entry.get())
		
	def exitGrant(self):
		if base.config.GetBool('want-admins', True):
			self.doId2grant_entry.destroy()
			self.grantDoId_btn.destroy()
			self.doId2grant_entry = None
			self.grantDoId_btn = None
