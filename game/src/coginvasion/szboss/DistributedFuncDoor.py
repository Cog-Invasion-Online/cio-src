from UseableObject import UseableObject
from DistributedEntity import DistributedEntity

class DistributedFuncDoor(DistributedEntity, UseableObject):
    
    StartsOpen  = 1
    UseOpens    = 4
    TouchOpens  = 8
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        UseableObject.__init__(self, False)
        self.wasTouching = False
        
        self.hasPhysGeom = True
        self.underneathSelf = True
        
    def getUseableBounds(self, min, max):
        self.cEntity.getModelBounds(min, max)

    def load(self):

        DistributedEntity.load(self)
        UseableObject.load(self)

        movesnd = self.getEntityValue("movesnd")
        if len(movesnd) > 0:
            self.addSound("movesnd", movesnd)

        stopsnd = self.getEntityValue("stopsnd")
        if len(stopsnd) > 0:
            self.addSound("stopsnd", stopsnd)
            
        lockedsnd = self.getEntityValue("locked_sound")
        if len(lockedsnd) > 0:
            self.addSound("locked", lockedsnd)
            
        unlockedsnd = self.getEntityValue("unlocked_sound")
        if len(unlockedsnd) > 0:
            self.addSound("unlocked", unlockedsnd)

        self.updateTask = taskMgr.add(self.__updateTask, self.uniqueName("updateTask"))
        
    def startUse(self):
        UseableObject.startUse(self)
        if self.hasSpawnFlags(self.UseOpens):
            self.sendUpdate('requestOpen')
        
    def __updateTask(self, task):
        if not self.hasSpawnFlags(DistributedFuncDoor.TouchOpens):
            return task.cont
        
        elif self.playerIsTouching():
            if not self.wasTouching:
                self.wasTouching = True
                self.sendUpdate('requestOpen')
                
        else:
            self.wasTouching = False

        return task.cont
        
    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        self.startSmooth()
        
    def unload(self):
        self.stopSmooth()
        DistributedEntity.unload(self)
        if self.updateTask:
            self.updateTask.remove()
            self.updateTask = None
        self.loopMoveSound = None
        self.removeNode()
