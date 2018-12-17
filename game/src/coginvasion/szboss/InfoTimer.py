from EntityAI import EntityAI

class InfoTimer(EntityAI):

    def __init__(self, air = None, dispatch = None):
        EntityAI.__init__(self, air, dispatch)
        self.delay = 0.0
        self.loop = False
        
        self.__time = 0.0
        self.timerTask = None
        
    def unload(self):
        if self.timerTask:
            self.timerTask.remove()
        self.timerTask = None
        self.__time = None
        self.delay = None
        self.loop = None
        
    def load(self):
        EntityAI.load(self)
        
        self.delay = self.getEntityValueFloat("delay")
        self.loop = bool(self.getEntityValueInt("loop"))
        
    def __timerTask(self, task):
        self.__time += task.getDt()
        if self.__time >= self.delay:
            self.dispatchOutput("OnTimeout")
            if self.loop:
                self.__time = 0.0
            else:
                return task.done
        
        return task.cont
        
    ####### Inputs ########
    
    def Start(self):
        self.timerTask = taskMgr.add(self.__timerTask, self.entityTaskName("info_timer_task"))
        self.dispatchOutput("OnStart")
        
    def Stop(self):
        if self.timerTask:
            self.timerTask.remove()
            self.timerTask = None
            self.dispatchOutput("OnStop")
            
    def Reset(self):
        self.__time = 0.0
        
    def SetDelay(self, delay):
        self.delay = float(delay)
        
    def SetLoop(self, loop):
        self.loop = bool(loop)