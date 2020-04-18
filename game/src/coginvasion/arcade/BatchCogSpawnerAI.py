from src.coginvasion.szboss.EntityAI import EntityAI

from direct.showbase.DirectObject import DirectObject

import random

class BatchCogSpawnerAI(EntityAI, DirectObject):
    
    MaxSuits = 10
    NumSuits = 0
    
    def __init__(self, air = None, dispatch = None):
        EntityAI.__init__(self, air, dispatch)
        
        self.ivalMin = 5.0
        self.ivalMax = 10.0
        self.maxBatchMin = 4
        self.maxBatchMax = 8
        
        self.batchSize = 0
        self.ival = 0.0
        
        self.looping = True
        
    def load(self):
        EntityAI.load(self)
        self.ivalMin = self.getEntityValueFloat("ivalMin")
        self.ivalMax = self.getEntityValueFloat("ivalMax")
        self.maxBatchMin = self.getEntityValueInt("maxBatchMin")
        self.maxBatchMax = self.getEntityValueInt("maxBatchMax")
        self.looping = bool(self.getEntityValueInt("looping"))
        
        self.accept('suitDied', self.__handleSuitDied)
        
        if bool(self.getEntityValueInt("startNow")):
            self.Start()
            
    def __handleSuitDied(self, doId):
        BatchCogSpawnerAI.NumSuits -= 1
        
    def unload(self):
        self.ignore('suitDied')
        self.Stop()
        del self.ivalMin
        del self.ivalMax
        del self.maxBatchMin
        del self.maxBatchMax
        del self.batchSize
        del self.ival
        del self.looping
        EntityAI.unload(self)
        
    def getIval(self):
        self.ival = random.uniform(self.ivalMin, self.ivalMax)
        
    def getBatchSize(self):
        self.batchSize = random.randint(self.maxBatchMin, self.maxBatchMax)
        
    def Start(self):
        self.getIval()
        self.getBatchSize()
        
        taskMgr.doMethodLater(self.ival, self.__batchSpawn, self.entityTaskName('batchSpawn'))
        
    def __batchSpawn(self, task):
        spawned = 0
        ents = self.bspLoader.findAllEntities("cogoffice_suitspawn")
        while spawned < self.batchSize and len(ents) and BatchCogSpawnerAI.NumSuits < BatchCogSpawnerAI.MaxSuits and BatchCogSpawnerAI.NumSuits < self.dispatch.waveSuitsRemaining:
            ent = random.choice(ents)
            ent.Spawn()
            spawned += 1
            ents.remove(ent)
        self.dispatchOutput("OnSpawnBatch")
        
        if self.looping:
            self.getIval()
            self.getBatchSize()
            task.delayTime = self.ival
            return task.again
        else:
            return task.done
        
    def Stop(self):
        taskMgr.remove(self.entityTaskName('batchSpawn'))
        
        
