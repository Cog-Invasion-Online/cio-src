from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI
from direct.interval.IntervalGlobal import LerpPosInterval

class FuncElevatorAI(DistributedEntityAI):

    StateStopped = 0
    StateMoving = 1

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.startPoint = None
        self.endPoint = None
        self.moveTrack = None
        self.speed = 0.0
        
    def clearMoveTrack(self):
        if self.moveTrack:
            self.moveTrack.pause()
            self.moveTrack = None
        
    def setEntityState(self, state):
        DistributedEntityAI.setEntityState(self, state)
        
        self.clearMoveTrack()
        
        if state == self.StateMoving:
            
            if (not self.startPoint) or (not self.endPoint):
                print("FuncElevatorAI ERROR: Missing either start or end point")
                return
                
            startPos = self.startPoint.cEntity.getOrigin()
            endPos = self.endPoint.cEntity.getOrigin()
            dist = (endPos - startPos).length()
            duration = (dist * 16) / self.speed
            self.moveTrack = LerpPosInterval(self, duration, endPos, startPos)
            self.moveTrack.start()
            
            self.dispatchOutput("OnStartMove")
            
    def Move(self):
        self.b_setEntityState(self.StateMoving)
            
    def loadEntityValues(self):
        startPointName = self.getEntityValue("startPoint")
        endPointName = self.getEntityValue("endPoint")
        self.startPoint = self.bspLoader.getPyEntityByTargetName(startPointName)
        self.endPoint = self.bspLoader.getPyEntityByTargetName(endPointName)
        self.speed = self.getEntityValueFloat("speed")
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        self.startPosHprBroadcast()
        render.ls()
        
