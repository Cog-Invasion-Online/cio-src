from panda3d.core import NodePath

from Entity import Entity

class TriggerOnce(Entity):
    """Listens for an avatar entry only once, then disables."""

    def __init__(self):
        Entity.__init__(self)
        self.wasInside = False
        self.watchTask = None
        
    def Enable(self):
        self.enabled = True
        
    def Disable(self):
        self.enabled = False
        
    def load(self):
        Entity.load(self)
        loader = self.cEntity.getLoader()
        entnum = self.cEntity.getEntnum()
        self.enabled = not bool(loader.getEntityValueInt(entnum, "StartDisabled"))
        self.watchTask = taskMgr.add(self._triggerTask, "triggerTask-" + str(self.cEntity.getEntnum()))
        
    def _triggerTask(self, task):
        if not self.enabled:
            return task.cont
            
        inside = self.cEntity.isInside(base.localAvatar.getPos(render))
        if inside and not self.wasInside:
            self.dispatchOutput("OnEnter")
            self.wasInside = True
            self.Disable()
        elif not inside and self.wasInside:
            self.dispatchOutput("OnExit")
            self.wasInside = False
            
        return task.cont

    def unload(self):
        Entity.unload(self)
        if self.watchTask:
            self.watchTask.remove()
            self.watchTask = None
        self.wasInside = None
        self.enabled = None
            
class TriggerMultiple(TriggerOnce):
    """Listens for an unlimited number of avatar entries, unless explicitly disabled."""

    def __init__(self):
        TriggerOnce.__init__(self)
        self.delay = 0.0
        self.lastExitTime = 0.0
        
    def load(self):
        TriggerOnce.load(self)
        loader = self.cEntity.getLoader()
        entnum = self.cEntity.getEntnum()
        self.delay = loader.getEntityValueFloat(entnum, "delay")
        
    def _triggerTask(self, task):
        if not self.enabled:
            return task.cont
            
        now = globalClock.getFrameTime()
            
        inside = self.cEntity.isInside(base.localAvatar.getPos(render))
        if inside and not self.wasInside:
            if now - self.lastExitTime >= self.delay:
                self.dispatchOutput("OnEnter")
                self.wasInside = True
        elif not inside and self.wasInside:
            self.dispatchOutput("OnExit")
            self.lastExitTime = now
            self.wasInside = False
            
        return task.cont
