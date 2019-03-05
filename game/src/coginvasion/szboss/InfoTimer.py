from EntityAI import EntityAI

class InfoTimer(EntityAI):

    def __init__(self, air = None, dispatch = None):
        EntityAI.__init__(self, air, dispatch)
        self.delay = 0.0
        self.loop = False
        
        self.timerTask = None
        
        self.__startTime = 0.0
        
    def unload(self):
        if self.timerTask:
            self.timerTask.remove()
        self.timerTask = None
        self.__startTime = None
        self.delay = None
        self.loop = None
        
    def load(self):
        EntityAI.load(self)
        
        self.delay = self.getEntityValueFloat("delay")
        self.loop = bool(self.getEntityValueInt("loop"))
        
    def __timerTask(self, task):
        now = globalClock.getFrameTime()
        if now - self.__startTime >= self.delay:
            self.dispatchOutput("OnTimeout")
            if self.loop:
                self.Reset()
            else:
                return task.done
        
        return task.cont
        
    ####### Inputs ########
    
    def Start(self, reset = True):
        if reset:
            self.Reset()
        self.timerTask = taskMgr.add(self.__timerTask, self.entityTaskName("info_timer_task"))
        self.dispatchOutput("OnStart")
        
    def Resume(self):
        self.Start(False)
        
    def Stop(self):
        if self.timerTask:
            self.timerTask.remove()
            self.timerTask = None
            self.dispatchOutput("OnStop")
            
    def Reset(self):
        self.__startTime = globalClock.getFrameTime()
        
    def SetDelay(self, delay):
        self.delay = float(delay)
        
    def SetLoop(self, loop):
        self.loop = bool(loop)
