from panda3d.core import Point3, Vec3

from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait, Func
from direct.fsm.FSM import FSM

from UseableObject import UseableObject
from DistributedEntity import DistributedEntity

DOORSTATE_CLOSED = 0
DOORSTATE_OPENING = 1
DOORSTATE_OPENED = 2
DOORSTATE_CLOSING = 3

class DistributedFuncDoor(DistributedEntity, UseableObject, FSM):
    
    StartsOpen  = 1
    UseOpens    = 4
    TouchOpens  = 8
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        UseableObject.__init__(self)
        FSM.__init__(self, 'FuncDoor')
        self.state = 0
        self.moveDir = Vec3(0)
        self.speed = 0
        self.wait = 0
        self.moveSound = None
        self.stopSound = None
        self.origin = Point3(0)
        self.spawnflags = 0
        self.moveIval = None
        self.mins = Point3(0)
        self.maxs = Point3(0)
        self.wasTouching = False
        
        self.hasPhysGeom = False
        self.underneathSelf = True
        
    def playMoveSound(self):
        if self.moveSound:
            self.moveSound.play()

    def stopMoveSound(self):
        if self.moveSound:
            self.moveSound.stop()

    def playStopSound(self):
        if self.stopSound:
            self.stopSound.play()
        
    def getDoorData(self):
        posDelta = self.maxs - self.mins
        posDelta.componentwiseMult(self.moveDir)
        openPos = self.origin + posDelta
        closedPos = self.origin
        duration = (posDelta.length() * 16.0) / self.speed
        
        return [posDelta, openPos, closedPos, duration]
        
    def enterOpening(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        
        posDelta, openPos, closedPos, duration = self.getDoorData()
            
        self.moveIval = Sequence(Func(self.playMoveSound),
                                 LerpPosInterval(self, pos = openPos, startPos = closedPos, duration = duration),
                                 Func(self.stopMoveSound),
                                 Func(self.playStopSound))
        
        self.moveIval.start()
        
    def exitOpening(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
            
    def enterClosing(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
            
        posDelta, openPos, closedPos, duration = self.getDoorData()
        
        self.moveIval = Sequence()
        self.moveIval.append(Func(self.playMoveSound))
        self.moveIval.append(LerpPosInterval(self, pos = closedPos, startPos = openPos, duration = duration))
        self.moveIval.append(Func(self.stopMoveSound))
        self.moveIval.append(Func(self.playStopSound))
        self.moveIval.start()
        
    def exitClosing(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
            
    def enterOpened(self):
        openPos = self.getDoorData()[1]
        self.setPos(openPos)
        
    def exitOpened(self):
        pass
        
    def enterClosed(self):
        closedPos = self.getDoorData()[2]
        self.setPos(closedPos)
        
    def exitClosed(self):
        pass
        
    def setDoorState(self, state):
        self.state = state
        if state == DOORSTATE_CLOSED:
            self.request('Closed')
        elif state == DOORSTATE_OPENING:
            self.request('Opening')
        elif state == DOORSTATE_OPENED:
            self.request('Opened')
        elif state == DOORSTATE_CLOSING:
            self.request('Closing')
        
    def getUseableBounds(self, min, max):
        self.cEntity.getModelBounds(min, max)

    def load(self):
        self.assign(self.cEntity.getModelNp())

        DistributedEntity.load(self)
        UseableObject.load(self)

        entnum = self.cEntity.getEntnum()
        loader = self.cEntity.getLoader()
        self.spawnflags = loader.getEntityValueInt(entnum, "spawnflags")
        self.moveDir = loader.getEntityValueVector(entnum, "movedir")
        self.speed = loader.getEntityValueFloat(entnum, "speed")
        self.wait = loader.getEntityValueFloat(entnum, "wait")

        movesnd = loader.getEntityValue(entnum, "movesnd")
        if len(movesnd) > 0:
            self.moveSound = base.audio3d.loadSfx(movesnd)
            self.moveSound.setLoop(bool(loader.getEntityValueInt(entnum, "loop_movesnd")))
            base.audio3d.attachSoundToObject(self.moveSound, self.cEntity.getModelNp())

        stopsnd = loader.getEntityValue(entnum, "stopsnd")
        if len(stopsnd) > 0:
            self.stopSound = base.audio3d.loadSfx(stopsnd)
            base.audio3d.attachSoundToObject(self.stopSound, self.cEntity.getModelNp())

        self.origin = self.getPos()
        self.cEntity.getModelBounds(self.mins, self.maxs)

        self.updateTask = taskMgr.add(self.__updateTask, self.uniqueName("updateTask"))
        
    def __updateTask(self, task):
        if not (self.spawnflags & DistributedFuncDoor.TouchOpens):
            return task.cont
        
        elif self.playerIsTouching():
            if not self.wasTouching:
                self.wasTouching = True
                self.sendUpdate('requestOpen')
                
        else:
            self.wasTouching = False

        return task.cont
        
    def unload(self):
        DistributedEntity.unload(self)
        if self.updateTask:
            self.updateTask.remove()
            self.updateTask = None
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        self.origin = None
        self.spawnflags = None
        self.isOpen = None
        self.moveDir = None
        self.speed = None
        self.wait = None
        self.moveSound = None
        self.stopSound = None
        self.mins = None
        self.maxs = None
        self.removeNode()
