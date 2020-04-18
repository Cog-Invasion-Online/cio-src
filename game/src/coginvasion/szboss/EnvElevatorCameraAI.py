from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class EnvElevatorCameraAI(DistributedEntityAI):

    def Enable(self):
        self.b_setEntityState(1)
        
    def Disable(self):
        self.b_setEntityState(0)
