from panda3d.bullet import BulletCylinderShape, BulletRigidBodyNode, ZUp

from src.coginvasion.phys.DistributedPhysicsEntityAI import DistributedPhysicsEntityAI
from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack.Attacks import ATTACK_GAG_TNT
from src.coginvasion.globals import CIGlobals
from src.coginvasion.attack.TakeDamageInfo import TakeDamageInfo

class TNTProjectileAI(DistributedPhysicsEntityAI):

    def __init__(self, air, avatar, attack):
        DistributedPhysicsEntityAI.__init__(self, air)
        self.avatar = avatar
        self.attack = attack
    
    def getPhysBody(self):
        shape = BulletCylinderShape(0.3925, 1.4, ZUp)
        body = BulletRigidBodyNode('tntBody')
        body.addShape(shape)
        body.setCcdMotionThreshold(1e-7)
        body.setCcdSweptSphereRadius(0.3925)
        body.setKinematic(False)
        body.setMass(5.0)
        body.setAngularDamping(0.3)
        body.setLinearDamping(0.8)
        return body

    def announceGenerate(self):
        DistributedPhysicsEntityAI.announceGenerate(self)
        taskMgr.doMethodLater(2.1, self.__explodeTask, self.uniqueName('TNT_explodeTask'))

    def delete(self):
        taskMgr.remove(self.uniqueName('TNT_explodeTask'))
        self.avatar = None
        self.attack = None
        DistributedPhysicsEntityAI.delete(self)

    def __explodeTask(self, task):
        self.sendUpdate('explode')

        for obj in self.air.avatars[self.zoneId]:
            if CIGlobals.isAvatar(obj) and self.attack.canDamage(obj):
                dist = obj.getDistance(self)
                if dist <= GagGlobals.TNT_RANGE:
                    info = TakeDamageInfo(self.avatar, ATTACK_GAG_TNT, self.attack.calcDamage(dist), self.getPos())
                    obj.takeDamage(info)

        self.requestDelete()
        return task.done
