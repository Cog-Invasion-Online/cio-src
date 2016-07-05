########################################
# Filename: ToontownClientRepository.py
# Created by: blach (17Jun14)
########################################

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gui.ToontownLoadingScreen import ToontownLoadingScreen
from lib.coginvasion.manager.ToontownConnectionManager import ToontownConnectionManager
from lib.coginvasion.toon.ToonBase import ToonBase
from lib.coginvasion.toon.NamePicker import NamePicker
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.gui.PickAToon import PickAToon
from pandac.PandaModules import *
from direct.directnotify.DirectNotify import DirectNotify
from lib.coginvasion.manager.SettingsManager import SettingsManager
from lib.coginvasion.gui import Whisper
import json

notify = DirectNotify().newCategory("ToontownClientRepository")

class ToontownClientRepository:
	
	def __init__(self):
		base.tcr = self
		self.cr = ClientRepository(dcFileNames=['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'])
		self.ttls = ToontownLoadingScreen()
		self.ttcm = ToontownConnectionManager(self.cr)
		base.accept("enterPickAToon", self.callPickAToon)
		base.accept("quitCreateAToon", self.callPickAToon)
		base.accept("toonCreated", self.callNamePicker)
		base.accept("nameConfirmed", self.saveToonInfo)
		base.accept("playGame", self.playGame)
		base.accept("PandaPaused", base.disableAllAudio)
		base.accept("PandaRestarted", base.enableAllAudio)
		base.accept("SysMsg", self.createSystemMessage)
		
		self.callToontownLoad()
		
	def createSystemMessage(self, message, important = 0):
		Whisper.Whisper().createSystemMessage(message, important)
		
	def callPatcher(self):
		self.filePatcher = filePatcher()
		
	def callPickAToon(self, fromOther=0):
		PAT = PickAToon(self.cr)
		PAT.createGui(fromOther=fromOther)
		
	def callNamePicker(self, head, headtype, headcolor, torsocolor, legcolor, gender, torsotype,
					legtype, slot, shirtcolor, shortscolor, shirt, short, sleeve):
		self.head = head
		self.headtype = headtype
		self.headcolor = headcolor
		self.torsocolor = torsocolor
		self.legcolor = legcolor
		self.gender = gender
		self.torsotype = torsotype
		self.legtype = legtype
		self.slot = slot
		self.shirtcolor = shirtcolor
		self.shortscolor = shortscolor
		self.shirt = shirt
		self.short = short
		self.sleeve = sleeve
		
		self.namePicker = NamePicker()
		
	def saveToonInfo(self, name):
		self.name = name
		notify.info("saving toon info...")
		infoFile = open("toons/toons.json")
		jsonInfo = json.load(infoFile)
		jsonInfo.update({"toon" + str(self.slot): {"name": self.name, "head": self.head, "headtype": self.headtype,
						"headcolor": self.headcolor, "torsocolor": self.torsocolor, "legcolor": self.legcolor,
						"gender": self.gender, "torsotype": self.torsotype, "legtype": self.legtype,
						"shirtcolor": self.shirtcolor, "shortscolor": self.shortscolor, "shirt": self.shirt,
						"short": self.short, "sleeve": self.sleeve}})
		l = open("toons/toons.json", "w")
		json.dump(jsonInfo, l)
		infoFile.close()
		l.close()
		
		self.callToonBase()
		
	def playGame(self, head, headtype, headcolor, torsocolor, legcolor, gender,
				torsotype, legtype, name, shirtcolor, shortscolor, shirt, short, sleeve):
		self.head = head
		self.headtype = headtype
		self.headcolor = headcolor
		self.torsocolor = torsocolor
		self.legcolor = legcolor
		self.gender = gender
		self.torsotype = torsotype
		self.legtype = legtype
		self.name = name
		self.shirtcolor = shirtcolor
		self.shortscolor = shortscolor
		self.shirt = shirt
		self.short = short
		self.sleeve = sleeve
		self.callToonBase()
		
	def callToonBase(self):
		self.toonBase = ToonBase(self.cr, self.head, self.headtype, self.headcolor,
							self.torsocolor, self.legcolor, self.gender, self.torsotype, self.legtype,
							self.name, self.shirtcolor, self.shortscolor, self.shirt, self.short, self.sleeve)
		base.hoodBGM.stop()
		
	def callToontownLoad(self):
		self.ttls.createMenu()
