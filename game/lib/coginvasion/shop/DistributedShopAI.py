"""

  Filename: DistributedShopAI.py
  Created by: DecodedLogic (13Jul15)

"""

from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedShopAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedShopAI')

    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        self.avatars = []

    def confirmPurchase(self, avId, money):
        self.air.doId2do.get(avId).b_setMoney(money)

    def requestHealth(self, health):
        avId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avId)
        if health > avatar.getMaxHealth():
            self.notify.warning('Suspicious: %s attempted to purchase a large amount of health.' % (avatar.getName()))
        else:
            giveHealth = avatar.getHealth() + health
            amt = health
            if giveHealth > avatar.getMaxHealth():
                giveHealth = avatar.getMaxHealth()
                amt = avatar.getMaxHealth() - avatar.getHealth()
            avatar.b_setHealth(giveHealth)
            avatar.d_announceHealthAndPlaySound(1, amt)
            
    def requestTurretCount(self):
        avId = self.air.getAvatarIdFromSender()
        for obj in self.air.doId2do.values():
            className = obj.__class__.__name__
            if obj.zoneId == self.zoneId:
                if className == 'DistributedCogBattleAI':
                    if obj.getTurretManager():
                        self.sendUpdateToAvatarId(avId, 'updateTurretCount', [obj.getTurretManager().getTurretCount()])

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if not avId in self.avatars:
            avatar = self.air.doId2do.get(avId)
            if avatar.getMoney() > 0:
                self.sendUpdateToAvatarId(avId, 'enterAccepted', [])
                self.avatars.append(avId)
            else:
                self.sendUpdateToAvatarId(avId, 'exitAccepted', [])
                self.sendUpdate('setClerkChat', [1])

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        if avId in self.avatars:
            self.sendUpdateToAvatarId(avId, 'exitAccepted', [])
            self.sendUpdate('setClerkChat', [0])
            self.avatars.remove(avId)

    def disable(self):
        self.avatars = []

    def delete(self):
        DistributedNodeAI.delete(self)
        self.avatars = []
        del self.avatars
