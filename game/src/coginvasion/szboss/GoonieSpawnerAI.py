from src.coginvasion.szboss.EntityAI import EntityAI

from direct.showbase.DirectObject import DirectObject
import random

class GoonieSpawnerAI(EntityAI, DirectObject):

    def __init__(self, air = None, dispatch = None):
        EntityAI.__init__(self, air, dispatch)
        
        self.numSpawned = 0
        self.maxSpawned = 5
        self.startedSpawning = False
        self.lastSpawnTime = 0.0
        self.spawnIval = 0.0
        
        self.spawnScript = None
        
    def think(self):
        if self.startedSpawning:
            now = globalClock.getFrameTime()
            if now - self.lastSpawnTime >= self.spawnIval:
                self.Spawn()
                
                self.spawnIval = random.uniform(5.0, 15.0)
                self.lastSpawnTime = globalClock.getFrameTime()
        
    def load(self):
        EntityAI.load(self)
        self.enableThink()
        self.accept('goonie_die', self.handleDie)
        
        ssName = self.getEntityValue("spawnScript")
        if len(ssName):
            self.spawnScript = self.bspLoader.getPyEntityByTargetName(ssName)
        
    def handleDie(self):
        self.numSpawned -= 1
        
    def unload(self):
        self.ignore('goonie_die')
        self.spawnScript = None
        self.numSpawned = None
        self.maxSpawned = None
        self.lastSpawnTime = None
        self.spawnIval = None
        self.startedSpawning = None
        EntityAI.unload(self)
        
    def StartSpawning(self):
        # Spawn one now and begin
        self.startedSpawning = True
        self.spawnIval = 0.0
        
    def StopSpawning(self):
        self.startedSpawning = False
        
    def Spawn(self):
        if self.numSpawned >= self.maxSpawned:
            return
        
        from src.coginvasion.szboss.goon.NPC_GoonAI import NPC_GoonAI
        
        goon = NPC_GoonAI(self.air, self.dispatch)
        goon.setPos(self.cEntity.getOrigin())
        goon.setHpr(self.cEntity.getAngles())
        hp = random.randint(25, 50)
        goon.setMaxHealth(hp)
        goon.setHealth(hp)
        goon.generateWithRequired(self.dispatch.zoneId)
        
        if self.spawnScript:
            self.spawnScript.ExecuteScript(goon)
        
        self.dispatchOutput("OnSpawn")
        
        self.numSpawned += 1
