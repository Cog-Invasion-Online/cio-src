# Filename: DistributedBattleShop.py
# Created by:  blach (14Jun15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectLabel

from lib.coginvasion.hood.DistributedShop import DistributedShop
from lib.coginvasion.npc.NPCGlobals import NPC_DNA
from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gui.BattleShop import BattleShop

class DistributedBattleShop(DistributedShop):
	notify = directNotify.newCategory("DistributedBattleShop")
	
	def __init__(self, cr):
		try:
			self.DistributedBattleShop_initialized
			return
		except:
			self.DistributedBattleShop_initialized = 1
		DistributedShop.__init__(self, cr)
		self.shopStateData = BattleShop(self, 'battleShopDone')
		self.stand = None
		self.standText = None
		
	def enterAccepted(self):
		if not self.inShop:
			self.acceptOnce(self.shopStateData.doneEvent, self.handleShopDone)
			self.shopStateData.load()
			self.shopStateData.enter()
			self.inShop = True
	
	def handleShopDone(self):
		self.shopStateData.exit()
		self.shopStateData.unload()
		self.d_requestExit()
	
	def setupClerk(self):
		self.clerk = Toon(self.cr)
		self.clerk.setDNAStrand(NPC_DNA['Coach'])
		self.clerk.setName('Coach')
		self.clerk.generateToon()
		self.clerk.reparentTo(self)
		self.clerk.setupNameTag()
		self.clerk.animFSM.request('neutral')
		self.clerk.setH(180)
		self.clerk.setY(2.2)
		self.clerk.setZ(1)
		self.stand = loader.loadModel("phase_4/models/props/bubblestand.egg")
		self.stand.reparentTo(self)
		self.stand.setScale(1.1)
		self.standText = DirectLabel(text = "Coach's Battle Shop",
			text_fg = (0.6, 0, 0, 1), text_decal = True, relief = None,
			parent = self.stand, pos = (0, -0.875, 5.2), scale = 0.45,
			text_font = CIGlobals.getMickeyFont())
		self.snp.setY(-1)
		
	def removeClerk(self):
		DistributedShop.removeClerk(self)
		self.standText.destroy()
		self.standText = None
		self.stand.removeNode()
		self.stand = None
