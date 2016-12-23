"""

  Filename: ToonFPSGui.py
  Created by: blach (19Jan15)

"""

from src.coginvasion.globals import CIGlobals

from direct.gui.DirectGui import DirectFrame, DirectWaitBar
from direct.gui.DirectGui import DGG, OnscreenText, DirectLabel

from pandac.PandaModules import TextNode

from MinigameUtils import *

class ToonFPSGui:

	def __init__(self, base):
		self.base = base
		self.noAmmoLabel = None
		self.ammo_gui = None
		self.hp_meter = None
		self.crosshair = None
		self.stats_container = None
		self.stats_bg = None
		self.stats_lbl = None
		self.kills_lbl = None
		self.deaths_lbl = None
		self.points_lbl = None

	def load(self):
		self.ammo_gui = loader.loadModel("phase_4/models/minigames/gun_ammo_gui.egg")
		self.ammo_gui.setScale(0.15)
		self.ammo_gui.setPos(0.38, 0, 0.1)
		self.hp_meter = DirectWaitBar(
			text = str(self.base.hp),
			text_roll = -90,
			text_scale = 0.2,
			text_pos = (-0.025, 0),
			relief = DGG.RAISED,
			barColor=(1, 0, 0, 1),
			range=self.base.max_hp,
			value=self.base.hp,
			parent=base.a2dBottomRight,
			scale=0.4,
			pos=(-0.12, 0, 0.2),
			frameSize=(-0.4, 0.4, -0.2, 0.2),
			#borderWidth=(0.02, 0.02),
		)
		self.hp_meter.setR(-90)
		self.hp_meter.hide()

		self.crosshair = getCrosshair()

		font = CIGlobals.getToonFont()
		box = DGG.getDefaultDialogGeom()
		if self.base.__class__.__name__ == "GunGameToonFPS":
			self.stats_container = DirectFrame(
				parent = base.a2dTopLeft,
				pos = (0.3, 0.2, -0.185)
			)
			self.stats_bg = OnscreenImage(
				image = box,
				color = (1, 1, 0.75, 1),
				scale = (0.5, 0.3, 0.3),
				parent = self.stats_container
			)
			self.stats_lbl = OnscreenText(
				font = font,
				text = "Stats",
				pos = (-0.01, 0.08, 0),
				parent = self.stats_container
			)
			self.kills_lbl = OnscreenText(
				font = font,
				text = "Kills: " + str(self.base.kills),
				pos = (-0.235, 0.025, 0),
				scale = 0.055,
				parent = self.stats_container,
				align = TextNode.ALeft
			)
			self.deaths_lbl = OnscreenText(
				font = font,
				text = "Deaths: " + str(self.base.deaths),
				pos = (-0.235, -0.04, 0),
				scale = 0.055,
				parent = self.stats_container,
				align = TextNode.ALeft
			)
			self.points_lbl = OnscreenText(
				font = font,
				text = "Points: " + str(self.base.points),
				pos = (-0.235, -0.105, 0),
				scale = 0.055,
				parent = self.stats_container,
				align = TextNode.ALeft
			)
			self.stats_container.hide()
			del font
			del box

	def start(self):
		self.ammo_gui.reparentTo(base.a2dBottomLeft)
		self.crosshair.show()
		self.hp_meter.show()
		if self.base.__class__.__name__ == "GunGameToonFPS":
			self.stats_container.show()
		#self.finalScoreContainer.show()

	def end(self):
		self.ammo_gui.reparentTo(hidden)
		if self.base.__class__.__name__ == "GunGameToonFPS":
			self.stats_container.hide()
		self.crosshair.hide()
		self.hp_meter.hide()

	def cleanup(self):
		self.ammo_gui.removeNode()
		self.ammo_gui = None
		self.hp_meter.destroy()
		self.hp_meter = None
		self.crosshair.destroy()
		self.crosshair = None
		self.deleteNoAmmoLabel()
		self.deleteStatsGui()

	def deleteStatsGui(self):
		if self.stats_container:
			self.stats_container.destroy()
			self.stats_container = None
		if self.stats_bg:
			self.stats_bg.destroy()
			self.stats_bg = None
		if self.stats_lbl:
			self.stats_lbl.destroy()
			self.stats_lbl = None
		if self.kills_lbl:
			self.kills_lbl.destroy()
			self.kills_lbl = None
		if self.deaths_lbl:
			self.deaths_lbl.destroy()
			self.deaths_lbl = None
		if self.points_lbl:
			self.points_lbl.destroy()
			self.points_lbl = None

	def updateStats(self):
		self.kills_lbl['text'] = "Kills: " + str(self.base.kills)
		self.deaths_lbl['text'] = "Deaths: " + str(self.base.deaths)
		self.points_lbl['text'] = "Points: " + str(self.base.points)

	def deleteNoAmmoLabel(self):
		if self.noAmmoLabel:
			self.noAmmoLabel.destroy()
			self.noAmmoLabel = None

	def adjustAmmoGui(self):
		self.ammo_gui.find('**/bar_' + str(self.base.ammo + 1)).hide()

	def adjustHpMeter(self):
		self.hp_meter['text'] = str(self.base.hp)
		self.hp_meter['value'] = self.base.hp
		if self.base.hp <= 40:
			self.hp_meter['barColor'] = (1, 0, 0, 1)
		else:
			self.hp_meter['barColor'] = (1, 1, 1, 1)

	def resetAmmo(self):
		for bar in self.ammo_gui.findAllMatches('**/bar_*'):
			bar.show()

	def notifyNoAmmo(self):
		self.deleteNoAmmoLabel()
		self.noAmmoLabel = DirectLabel(
			text = "Press R to reload!",
			relief = None,
			text_scale = 0.1,
			text_pos = (0, 0.5, 0),
			text_fg = (1, 1, 1, 1),
			text_shadow = (0, 0, 0, 1)
		)
