from panda3d.core import Vec3

from DistributedTNT import DistributedTNT

class LocalTNT(DistributedTNT):

    def __init__(self, gag, cr):
        DistributedTNT.__init__(self, cr)
        self.gag = gag
        self.gotOwnership = False
        self.explodeTask = None

    def toss(self, power = 20.0):
        self.explodeTask = taskMgr.doMethodLater(2.5, self.__explodeTask, 'TNT_explodeTask')

        # Toss the TNT!
        vel = camera.getQuat(render).xform(Vec3.forward()) * power
        self.node().setLinearVelocity(vel)

    def ownershipGranted(self, doId):
        self.doId = doId
        self.setLocation(base.localAvatar.parentId, base.localAvatar.zoneId)
        self.startPosHprBroadcast()
        self.gotOwnership = True
        print "Woohoo got ownership!"

    def b_explode(self):
        self.explode()
        if self.gotOwnership:
            self.sendUpdate('explode')
        self.gag.activate(self)

    def getPhysBody(self):
        body = DistributedTNT.getPhysBody(self)
        body.setKinematic(False)
        body.setMass(5.0)
        body.setAngularDamping(0.3)
        #body.setLinearDamping(5.0)
        return body

    def doSetupPhysics(self):
        self.setupPhysics(self.getPhysBody(), False)

    def __explodeTask(self, task):
        self.b_explode()
        if self.gotOwnership:
            print "Exploded: has ownership"
            self.cr.deleteObject(self.doId)
        else:
            print "Exploded: not ownership"
            self.disable()
            self.delete()
        return task.done

    def disable(self):
        print "disable"
        self.stopPosHprBroadcast()
        self.gag = None
        if self.explodeTask:
            self.explodeTask.remove()
        self.explodeTask = None
        DistributedTNT.disable(self)