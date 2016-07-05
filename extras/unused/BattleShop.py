# Filename: BattleShop.py
# Created by:  blach (03Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectButton, DirectLabel, DGG

from lib.coginvasion.globals import CIGlobals
from Shop import Shop

class BattleShop(Shop):
	notify = directNotify.newCategory("BattleShop")
	
	def __init__(self, distShop, doneEvent):
		Shop.__init__(self, distShop, doneEvent)
		self.upgradePrices = {
			0: 200 # Turret
		}
		self.maxPU = 1
		self.turret_btn = None
		self.turret_lbl = None
		
	def enter(self):
		Shop.enter(self)
		self.starting_turret = base.localAvatar.getPUInventory()[0]
		self.turret_btn = DirectButton(relief = None, geom = CIGlobals.getDefaultBtnGeom(), text = "Turret", text_scale = 0.055, command = self.purchasePU, extraArgs = [0])
		self.turret_lbl = DirectLabel(relief = None, scale = 0.05, text = "{0}/{1}".format(base.localAvatar.getPUInventory()[0], self.maxPU), pos = (0, 0, -0.1))
	
	def purchasePU(self, index):
		if base.localAvatar.getMoney() < self.upgradePrices[index]:
			self.handleNoMoney()
			return
		if base.localAvatar.getPUInventory()[index] < self.maxPU:
			base.localAvatar.setMoney(base.localAvatar.getMoney() - self.upgradePrices[index])
			base.localAvatar.getPUInventory()[index] = self.maxPU
		self.update()
		
	def update(self):
		Shop.update(self)
		self.turret_lbl['text'] = "{0}/{1}".format(base.localAvatar.getPUInventory()[0], self.maxPU)
		if base.localAvatar.getPUInventory()[0] >= self.maxPU:
			self.turret_btn['state'] = DGG.DISABLED
	
	def confirmPurchase(self):
		array = []
		array.append(base.localAvatar.getPUInventory()[0])
		if base.localAvatar.getPUInventory()[0] > 0:
			if not base.localAvatar.getMyBattle().getTurretManager().myTurret:
				base.localAvatar.getMyBattle().getTurretManager().createTurretButton()
		self.distShop.sendUpdate('confirmPurchase', [array, base.localAvatar.getMoney()])
		Shop.confirmPurchase(self)
	
	def cancelPurchase(self):
		base.localAvatar.setMoney(self.starting_money)
		base.localAvatar.getPUInventory()[0] = self.starting_turret
		Shop.cancelPurchase(self)
	
	def exit(self):
		Shop.exit(self)
		self.turret_btn.destroy()
		del self.turret_btn
		self.turret_lbl.destroy()
		del self.turret_lbl
		return
