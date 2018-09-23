from DistributedEntityAI import DistributedEntityAI

from direct.fsm.FSM import FSM

class DistributedGeneratorAI(DistributedEntityAI, FSM):
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        FSM.__init__(self, 'DGeneratorAI')
        self.state = 0
        
    def delete(self):
        self.request('Off')
        self.state = 0
        DistributedEntityAI.delete(self)
        
    def PowerOn(self):
        if self.state == 1 or self.state == 3:
            self.b_setState(2)
        
    def PowerOff(self):
        if self.state == 0 or self.state == 2:
            self.b_setState(3)
        
    def enterPowerOn(self):
        self.dispatchOutput("OnPowerOn")
        
    def exitPowerOn(self):
        pass
        
    def enterPowerOff(self):
        self.dispatchOutput("OnPowerOff")
        
    def exitPowerOff(self):
        pass
        
    def enterPoweringOff(self):
        taskMgr.doMethodLater(5.21, self.__doNextStateTask, name = self.uniqueName('poweringoff'), extraArgs = [1], appendTask = True)
        
    def exitPoweringOff(self):
        taskMgr.remove(self.uniqueName('poweringoff'))
        
    def enterPoweringOn(self):
        taskMgr.doMethodLater(5.21122, self.__doNextStateTask, name = self.uniqueName('poweringon'), extraArgs = [0], appendTask = True)
        
    def exitPoweringOn(self):
        taskMgr.remove(self.uniqueName('poweringon'))
        
    def __doNextStateTask(self, state, task):
        self.b_setState(state)
        return task.done
        
    def setState(self, state):
        self.state = state
        if state == 0:
            self.request('PowerOn')
            
        elif state == 1:
            self.request('PowerOff')
            
        elif state == 2:
            self.request('PoweringOn')
            
        elif state == 3:
            self.request('PoweringOff')
            
    def getState(self):
        return self.state
            
    def b_setState(self, state):
        self.sendUpdate('setState', [state])
        self.setState(state)