from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

#from src.mod.ModGlobals import LocalAvatarID

class TriggerChangeLevelAI(DistributedEntityAI):
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.nextLevelName = ""

    def delete(self):
        self.nextLevelName = None
        DistributedEntityAI.delete(self)

    def loadEntityValues(self):
        self.nextLevelName = self.getEntityValue("nextLevel")

    def think(self):
        pass
        # This only works in singleplayer
        #plyr = base.air.doId2do.get(LocalAvatarID)
        #if self.cEntity.isInside(plyr.getPos(render)):
        #    self.ChangeLevel()
        #    self.setNextThink(-1)

    def ChangeLevel(self):
        myName = self.getEntityValue("targetname")
        self.dispatch.transitionToMap(self.nextLevelName, myName)
