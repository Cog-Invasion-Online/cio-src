from direct.interval.IntervalGlobal import Func, LerpHprInterval

from src.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from DistributedEntity import DistributedEntity
from src.coginvasion.globals import CIGlobals
from Goon import Goon

class DistributedGoon(Goon, DistributedAvatar, DistributedEntity):

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        DistributedAvatar.__init__(self, cr)
        Goon.__init__(self)
        self.moveTrack = None

        self.pathVisRoot = render.attachNewNode('pathVisRoot')

        self._watchTarget = None

    def clearMoveTrack(self):
        for child in self.pathVisRoot.getChildren():
            child.removeNode()
        if self.moveTrack:
            self.moveTrack.pause()
            self.moveTrack = None
            
    def generate(self):
        DistributedEntity.generate(self)
        DistributedAvatar.generate(self)

    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        DistributedAvatar.announceGenerate(self)
        taskMgr.add(self.__watchTargetTask, self.uniqueName("watchTarget"))

        self.reparentTo(render)

    def disable(self):
        taskMgr.remove(self.uniqueName("watchTarget"))
        if self.pathVisRoot:
            self.pathVisRoot.removeNode()
            self.pathVisRoot = None
        DistributedAvatar.disable(self)
        DistributedEntity.disable(self)

    def __watchTargetTask(self, task):
        if self._watchTarget:
            self.headsUp(self._watchTarget)

        return task.cont

    def doDetectStuff(self):
        self.detectSound.play()
        self.doDetectGlow()

    def wakeup(self):
        self.setEyeColor(self.IdleEyeColor)
        self.wakeupSound.play()
        self.play("wakeup")

    def doIdle(self):
        self.idleSound.play()
        self.playIdleAnim()

    def stopIdle(self):
        self.idleSound.stop()

    def doScan(self):
        self.request('Scan')

    def doAsleep(self):
        self.setEyeColor(self.AsleepEyeColor)
        self.request('Asleep')
        self.idleSound.stop()

    def watchTarget(self, targetId):
        self._watchTarget = self.cr.doId2do.get(targetId)

    def stopWatchingTarget(self):
        self._watchTarget = None

    def shoot(self, targetId):
        self.request('Shoot', self.cr.doId2do.get(targetId))
        
    def handleHitByToon(self, player, gagId, distance):
        if self.isDead():
            return
            
        self.sendUpdate('hitByGag', [gagId, distance])

    def doMoveTrack(self, path, turnToFirstWP = True, speed = 3.0, doWalkAnims = True):
        self.clearMoveTrack()

        #for pos in path:
        #    smiley = loader.loadModel("models/smiley.egg.pz")
        #    smiley.reparentTo(self.pathVisRoot)
        #    smiley.setPos(pos)
        #    smiley.setTextureOff(1)

        self.moveTrack = CIGlobals.getMoveIvalFromPath(self, path, speed)

        if turnToFirstWP:
            turnHpr = CIGlobals.getHeadsUpAngle(self, path[1])
            turnDist = CIGlobals.getHeadsUpDistance(self, path[1])
            if doWalkAnims:
                self.moveTrack.insert(0, Func(self.playWalkAnim, 1.0))
            self.moveTrack.insert(1, LerpHprInterval(self, duration = turnDist / (speed * 30), hpr = turnHpr))
            if doWalkAnims:
                self.moveTrack.insert(2, Func(self.playWalkAnim, 1.5))
        elif doWalkAnims:
            self.moveTrack.insert(0, Func(self.playWalkAnim, 1.5))

        self.moveTrack.append(Func(self.playIdleAnim))
        self.moveTrack.start()
