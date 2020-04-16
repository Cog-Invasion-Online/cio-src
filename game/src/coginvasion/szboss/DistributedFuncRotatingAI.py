from DistributedEntityAI import DistributedEntityAI
from direct.fsm.FSM import FSM

class DistributedFuncRotatingAI(DistributedEntityAI, FSM):

    StartsRotating = 1

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        FSM.__init__(self, 'func_rotating_ai')
        self.state = 0
        self.timeToWind = 5.0
        self.spawnflags = 0
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        if self.spawnflags & self.StartsRotating:
            self.b_setState(1)
        
    def loadEntityValues(self):
        self.timeToWind = self.getEntityValueFloat("timeToFull")
        self.spawnflags = self.getEntityValueInt("spawnflags")
        
    def Start(self):
        self.b_setState(2)
        
    def Stop(self):
        self.b_setState(3)
        
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
            
    def b_setState(self, state):
        self.sendUpdate('setState', [state])
        self.setState(state)
        
    def getState(self):
        return self.state
            
    def enterStopped(self):
        self.dispatchOutput("OnStop")
        
    def exitStopped(self):
        pass
        
    def enterRotating(self):
        print "enterRotating"
        self.dispatchOutput("OnStart")
        
    def exitRotating(self):
        pass
        
    def enterStartRotating(self):
        taskMgr.doMethodLater(self.timeToWind, self.__doNextState,
                              name = self.uniqueName('srot'), extraArgs = [1],
                              appendTask = True)
                              
    def exitStartRotating(self):
        taskMgr.remove(self.uniqueName('srot'))
        
    def enterStopRotating(self):
        taskMgr.doMethodLater(self.timeToWind, self.__doNextState,
                              name = self.uniqueName('strot'), extraArgs = [0],
                              appendTask = True)
                              
    def exitStopRotating(self):
        taskMgr.remove(self.uniqueName('strot'))
        
    def __doNextState(self, state, task):
        self.b_setState(state)
        return task.done
        
    def delete(self):
        self.request('Off')
        self.state = None
        self.timeToWind = None
        self.spawnflags = None
        DistributedEntityAI.delete(self)