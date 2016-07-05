# Filename: DistributedPieTurretManagerAI.py
# Created by:  blach (14Jun15)
# Updated by:  DecodedLogic (10Aug15)

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.battle.DistributedPieTurretAI import DistributedPieTurretAI

class DistributedPieTurretManagerAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedPieTurretManagerAI')

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.turretId2turret = {}

    def killTurret(self, turretId):
        if self.turretId2turret == None:
            return
        turret = self.turretId2turret[turretId]
        turret.disable()
        turret.requestDelete()
        del self.turretId2turret[turretId]

    def requestPlace(self, posHpr):
        if self.turretId2turret == None:
            return
        avId = self.air.getAvatarIdFromSender()
        turret = DistributedPieTurretAI(self.air)
        turret.setManager(self)
        turret.generateWithRequired(self.zoneId)
        turret.b_setMaxHealth(100)
        turret.b_setHealth(100)
        turret.b_setOwner(avId)
        x, y, z, h, p, r = posHpr
        turret.b_setPosHpr(x, y, z, h, p, r)
        turret.b_setParent(CIGlobals.SPRender)
        turret.startScanning()
        self.turretId2turret[turret.doId] = turret
        self.sendUpdateToAvatarId(avId, 'turretPlaced', [turret.doId])

    def disable(self):
        for turret in self.turretId2turret.values():
            turret.requestDelete()
            turret.disable()
            turret.delete()
        self.turretId2turret = None
        
    def getTurretCount(self):
        turrets = 0
            
        for obj in base.air.doId2do.values():
            className = obj.__class__.__name__
            if obj.zoneId == self.zoneId:
                if className == 'DistributedToonAI':
                    if obj.getPUInventory()[0] > 0:
                        turrets += 1
                elif className == 'DistributedPieTurretAI':
                    turrets += 1
        return turrets