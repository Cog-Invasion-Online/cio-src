from DistributedEntityAI import DistributedEntityAI

class EnvFogAI(DistributedEntityAI):

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.entState = 1 # Enabled by default

    def loadEntityValues(self):
        startDisabled = self.getEntityValueBool("startDisabled")
        if startDisabled:
            self.entState = 0

    def EnableFog(self):
        self.b_setEntityState(1)
        print "Enabling fog!"

    def DisableFog(self):
        self.b_setEntityState(0)
        print "Disabling fog!"
