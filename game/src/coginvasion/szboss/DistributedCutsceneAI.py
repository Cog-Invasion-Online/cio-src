from DistributedEntityAI import DistributedEntityAI

class DistributedCutsceneAI(DistributedEntityAI):

    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.cutsceneId = ""
        self.length = 0.0
        self.inProgress = False

    def delete(self):
        taskMgr.remove(self.taskName("handleCutsceneOver"))
        self.cutsceneId = None
        self.length = None
        self.inProgress = None
        DistributedEntityAI.delete(self)

    def loadEntityValues(self):
        self.cutsceneId = self.getEntityValue("cutsceneId")
        self.length = self.getEntityValueFloat("length")

    def DoCutscene(self):
        if self.inProgress:
            return
            
        print "DoCutscene", self.length

        self.sendUpdate('doCutscene', [self.cutsceneId])
        self.dispatchOutput("OnBegin")
        taskMgr.doMethodLater(self.length, self.__handleCutsceneOver, self.taskName("handleCutsceneOver"))

        self.inProgress = True

    def __handleCutsceneOver(self, task):
        self.inProgress = False
        self.dispatchOutput("OnFinish")
        self.sendUpdate('endCutscene')
