from panda3d.core import TransformState
from panda3d.bullet import BulletCylinderShape, BulletSphereShape, BulletRigidBodyNode, ZUp

from src.coginvasion.attack.Attacks import ATTACK_BOMB
from src.coginvasion.attack.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.DistributedPhysicsEntityAI import DistributedPhysicsEntityAI

class BombProjectileAI(DistributedPhysicsEntityAI):

    def __init__(self, air, avatar, attack):
        DistributedPhysicsEntityAI.__init__(self, air)
        self.avatar = avatar
        self.attack = attack
    
    def getPhysBody(self):
        bsph = BulletSphereShape(0.6)
        bcy = BulletCylinderShape(0.25, 0.35, ZUp)
        body = BulletRigidBodyNode('tntBody')
        body.addShape(bsph, TransformState.makePosHpr((0.05, 0, 0.43), (86.597, 24.5539, 98.1435)))
        body.addShape(bcy, TransformState.makePosHpr((0.05, 0.655, 0.35), (86.597, 24.5539, 98.1435)))
        body.setKinematic(False)
        body.setCcdMotionThreshold(1e-7)
        body.setCcdSweptSphereRadius(0.6)
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
            if CIGlobals.isAvatar(obj) and not CIGlobals.avatarsAreFriends(self.avatar, obj):
                dist = obj.getDistance(self)
                if dist <= 10.0:
                    info = TakeDamageInfo(self.avatar, ATTACK_BOMB, self.attack.calcDamage(dist), self.getPos())
                    obj.takeDamage(info)

        self.requestDelete()
        return task.done
