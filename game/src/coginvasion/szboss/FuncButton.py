from panda3d.core import NodePath, Point3, Vec3

from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpPosInterval

from UseableObject import UseableObject
from Entity import Entity

class FuncButton(UseableObject, Entity):

    def __init__(self):
        Entity.__init__(self)
        UseableObject.__init__(self)
        self.pressSound = None
        self.pressIval = None

        self.assignToTrigger = False
        
    def startUse(self):
        UseableObject.startUse(self)
        self.press()
        
    def getUseableBounds(self, min, max):
        self.cEntity.getModelBounds(min, max)

    def load(self):
        self.assign(self.cEntity.getModelNp())
        
        Entity.load(self)
        UseableObject.load(self)
        
        self.pressSound = base.audio3d.loadSfx("phase_3.5/audio/sfx/AV_hit_button.ogg")
        base.audio3d.attachSoundToObject(self.pressSound, self.cEntity.getModelNp())
        self.origin = self.getPos()
        loader = self.cEntity.getLoader()
        entnum = self.cEntity.getBspEntnum()
        self.speed = loader.getEntityValueFloat("speed")
        self.wait = loader.getEntityValueFloat(entnum, "wait")
        self.mins = Point3(0)
        self.maxs = Point3(0)
        self.cEntity.getModelBounds(self.mins, self.maxs)

    def activate(self):
        if self.pressIval:
            self.pressIval.finish()
            self.pressIval = None

        posDelta = (self.maxs - self.mins)
        posDelta.componentwiseMult(Vec3.forward() * 0.9)
        duration = posDelta.length() / self.speed
        startPos = self.origin
        endPos = self.origin + posDelta
        self.pressIval = Sequence(Func(self.pressSound.play), LerpPosInterval(self, duration, endPos, startPos))
        if self.wait != -1:
           self.pressIval.append(Wait(self.wait))
           self.pressIval.append(LerpPosInterval(self, duration, startPos, endPos))
        self.pressIval.start()
