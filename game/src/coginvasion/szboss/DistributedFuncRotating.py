from panda3d.core import Vec3

from direct.interval.IntervalGlobal import LerpHprInterval

from DistributedEntity import DistributedEntity
from src.coginvasion.phys import PhysicsUtils
from direct.fsm.FSM import FSM

class DistributedFuncRotating(DistributedEntity, FSM):
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        FSM.__init__(self, 'func_rotating')
        self.state = 0
        self.axis = Vec3.up()
        self.timeToFull = 5.0
        self.speed = 50.0
        self.spinTrack = None
        
    def setState(self, state):
        self.state = state
        if state == 0:
            self.request('Stopped')
        elif state == 1:
            self.request('Rotating')
        elif state == 2:
            self.request('StartRotating')
        elif state == 3:
            self.request('StopRotating')
        
    def disable(self):
        self.request('Off')
        self.__cleanupSpin()
        self.state = None
        self.axis = None
        self.timeToFull = None
        self.speed = None
        self.spinTrack = None
        DistributedEntity.disable(self)
        
    def load(self):
        DistributedEntity.load(self)
        
        self.axis = self.getEntityValueVector("axis")
        self.speed = self.getEntityValueFloat("speed")
        self.timeToFull = self.getEntityValueFloat("timeToFull")
        
        base.materialData.update(PhysicsUtils.makeBulletCollFromGeoms(self.cEntity.getModelNp()))
        
    def __getRot(self):
        rot = Vec3(360, 360, 0)
        rot[0] *= self.axis[2]
        rot[1] *= self.axis[1]
        return rot
        
    def enterStopped(self):
        pass
        
    def exitStopped(self):
        pass
        
    def __cleanupSpin(self):
        if self.spinTrack:
            self.spinTrack.pause()
            self.spinTrack = None
        
    def enterRotating(self):
        print self.__getRot()
        print "We are rotating"
        self.spinTrack = LerpHprInterval(self.cEntity.getModelNp(), 60.0 / self.speed, self.__getRot(), startHpr = (0, 0, 0))
        self.spinTrack.loop()
        
    def exitRotating(self):
        self.__cleanupSpin()
        
    def enterStartRotating(self):
        self.startTime = globalClock.getFrameTime()
        taskMgr.add(self.__startRotatingTask, self.uniqueName('srot'))
        
    def __startRotatingTask(self, task):
        currHpr = self.cEntity.getModelNp().getHpr()
        elapsed = globalClock.getFrameTime() - self.startTime
        speed = min(self.speed, self.speed * (elapsed / self.timeToFull))
        newHpr = currHpr + Vec3(self.axis[2] * speed, self.axis[1] * speed, 0)
        self.cEntity.getModelNp().setHpr(newHpr)
        
        return task.cont
        
    def exitStartRotating(self):
        taskMgr.remove(self.uniqueName('srot'))
        del self.startTime
        
    def enterStopRotating(self):
        self.startTime = globalClock.getFrameTime()
        taskMgr.add(self.__stopRotatingTask, self.uniqueName('strot'))
        
    def __stopRotatingTask(self, task):
        currHpr = self.cEntity.getModelNp().getHpr()
        elapsed = globalClock.getFrameTime() - self.startTime
        speed = max(0, self.speed - (self.speed * (elapsed / self.timeToFull)))
        newHpr = currHpr + Vec3(self.axis[2] * speed, self.axis[1] * speed, 0)
        self.cEntity.getModelNp().setHpr(newHpr)
        
        return task.cont
        
    def exitStopRotating(self):
        taskMgr.remove(self.uniqueName('strot'))
        del self.startTime