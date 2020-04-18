from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class PropDynamicAI(DistributedEntityAI):

    def loadEntityValues(self):
        self.setModel(self.getEntityValue("modelpath"))
        self.setModelScale(self.getEntityValueVector("scale"))
