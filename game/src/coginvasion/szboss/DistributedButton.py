from panda3d.core import Point3, Vec3

from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait, Func
from direct.fsm.FSM import FSM

from UseableObject import UseableObject
from DistributedEntity import DistributedEntity

class DistributedButton(DistributedEntity, UseableObject, FSM):
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        UseableObject.__init__(self)
        FSM.__init__(self, 'button')
        self.state = 0
        self.moveDir = Vec3(0)
        self.speed = 0
        self.moveIval = None
        self.mins = Point3(0)
        self.maxs = Point3(0)
        self.origin = Point3(0)
        self.pressSound = None
        
        self.hasPhysGeom = False
        self.underneathSelf = True
        
    def startUse(self):
        UseableObject.startUse(self)
        self.d_requestPress()
        
    def d_requestPress(self):
        self.sendUpdate('requestPress')
        
    def load(self):
        self.assign(self.cEntity.getModelNp())

        DistributedEntity.load(self)
        UseableObject.load(self)

        entnum = self.cEntity.getEntnum()
        loader = self.cEntity.getLoader()
        self.moveDir = loader.getEntityValueVector(entnum, "movedir")
        self.speed = loader.getEntityValueFloat(entnum, "speed")
        self.wait = loader.getEntityValueFloat(entnum, "wait")

        movesnd = loader.getEntityValue(entnum, "sounds")
        if len(movesnd) > 0:
            self.pressSound = base.audio3d.loadSfx(movesnd)
            base.audio3d.attachSoundToObject(self.pressSound, self.cEntity.getModelNp())

        self.origin = self.getPos()
        self.cEntity.getModelBounds(self.mins, self.maxs)
        
    def getMoveData(self):
        posDelta = self.maxs - self.mins
        posDelta.componentwiseMult(self.moveDir)
        openPos = self.origin + posDelta
        closedPos = self.origin
        duration = (posDelta.length() * 16.0) / self.speed
        
        return [posDelta, openPos, closedPos, duration]
        
    def enterDepressed(self):
        pos = self.getMoveData()[2]
        self.setPos(pos)
        
    def exitDepressed(self):
        pass
        
    def enterPressed(self):
        pos = self.getMoveData()[1]
        self.setPos(pos)
        
    def exitPressed(self):
        pass
        
    def playPressSound(self):
        if self.pressSound:
            self.pressSound.play()
            
    def enterDepressing(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
            
        posDelta, openPos, closedPos, duration = self.getMoveData()
        
        self.moveIval = Sequence()
        self.moveIval.append(LerpPosInterval(self, pos = closedPos, startPos = openPos, duration = duration))
        self.moveIval.start()
        
    def exitDepressing(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        
    def enterPressing(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
        
        posDelta, openPos, closedPos, duration = self.getMoveData()
            
        self.moveIval = Sequence(Func(self.playPressSound),
                                 LerpPosInterval(self, pos = openPos, startPos = closedPos, duration = duration))
        
        self.moveIval.start()
        
    def exitPressing(self):
        if self.moveIval:
            self.moveIval.finish()
            self.moveIval = None
            
    def getUseableBounds(self, min, max):
        self.cEntity.getModelBounds(min, max)
        
    def unload(self):
        DistributedEntity.unload(self)
        self.request('Off')
        self.moveIval = None
        self.origin = None
        self.mins = None
        self.maxs = None
        self.speed = None
        self.wait = None
        self.moveDir = None
        self.pressSound = None
        self.state = None
        self.removeNode()
    
    def setState(self, state):
        self.state = state
        if state == 0:
            self.request('Depressed')
        elif state == 1:
            self.request('Pressing')
        elif state == 2:
            self.request('Pressed')
        elif state == 3:
            self.request('Depressing')