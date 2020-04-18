from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class EnvParticleSystemAI(DistributedEntityAI):
    
    StartsEnabled = 1 << 0
    
    StateDead = 0
    StateAlive = 1
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.aliveTime = 0.0
        
    def loadEntityValues(self):
        self.aliveTime = self.getEntityValueFloat("aliveTime")
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        
        if self.hasSpawnFlags(self.StartsEnabled):
            print "Smoke starts enabled"
            self.Start()
        
    def think(self):
        DistributedEntityAI.think(self)
        
        state = self.getEntityState()
        elapsed = self.getEntityStateElapsed()
        
        if state == self.StateAlive:
            if self.aliveTime != -1 and elapsed >= self.aliveTime:
                print "ok now stop"
                self.Stop()
                
    def Start(self):
        self.b_setEntityState(self.StateAlive)
        print "Start smoke"
        
    def Stop(self):
        self.b_setEntityState(self.StateDead)
