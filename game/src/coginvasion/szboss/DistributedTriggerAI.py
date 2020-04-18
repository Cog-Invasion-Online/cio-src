from DistributedEntityAI import DistributedEntityAI

class DistributedTriggerOnceAI(DistributedEntityAI):

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.enabled = False

    def load(self):
        DistributedEntityAI.load(self)
        self.enabled = not self.getEntityValueBool("StartDisabled")

    def Disable(self):
        self.enabled = False

    def Enable(self):
        self.enabled = True

    def onPlayerEnter(self):
        if self.enabled:
            self.dispatchOutput("OnEnter")
            self.Disable()

    def onPlayerExit(self):
        if self.enabled:
            self.dispatchOutput("OnExit")

    def delete(self):
        DistributedEntityAI.delete(self)
        self.enabled = None

class DistributedTriggerMultipleAI(DistributedTriggerOnceAI):

    def __init__(self, air, dispatch):
        DistributedTriggerOnceAI.__init__(self, air, dispatch)
        self.delay = 0.0
        self.lastExitTime = 0.0

    def load(self):
        DistributedTriggerOnceAI.load(self)
        self.delay = self.getEntityValueFloat("delay")

    def onPlayerEnter(self):
        if self.enabled:
            now = globalClock.getFrameTime()
            if now - self.lastExitTime >= self.delay:
                self.dispatchOutput("OnEnter")

    def onPlayerExit(self):
        if self.enabled:
            self.dispatchOutput("OnExit")
            self.lastExitTime = globalClock.getFrameTime()

    def delete(self):
        DistributedTriggerOnceAI.delete(self)
        self.delay = None
        self.lastExitTime = None
