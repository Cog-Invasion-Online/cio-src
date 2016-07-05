# Filename: DistributedBattleShopAI.py
# Created by:  blach (14Jun15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood.DistributedShopAI import DistributedShopAI

class DistributedBattleShopAI(DistributedShopAI):
	notify = directNotify.newCategory("DistributedBattleShopAI")
	
	def __init__(self, air):
		try:
			self.DistributedBattleShopAI_initialized
			return
		except:
			self.DistributedBattleShopAI_initialized = 1
		DistributedShopAI.__init__(self, air)
		
	def confirmPurchase(self, array, money):
		avId = self.air.getAvatarIdFromSender()
		DistributedShopAI.confirmPurchase(self, avId, money)
		# Make sure there are no power up values over 1
		for value in array:
			if value > 1:
				# Kick this guy for trying to buy more than 1 of the same powerup.
				self.air.eject(avId, 0, "Trying to purchase more than one of the same power up.")
				return
		obj = self.air.doId2do.get(avId)
		obj.b_setPUInventory(array)
