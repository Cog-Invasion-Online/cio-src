from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

import random

class AmbientGenericAI(DistributedEntityAI):
    StateStopped = 0
    StatePlaying = 1
    
    LoopNo = 0
    LoopYes = 1
    LoopRandom = 2 # Looping with random delay
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        
        self.entState = self.StateStopped

        self.sndFile = ""
        self.looping = self.LoopNo
        self.volume = 1.0
        
        self.randomDelayMin = 1
        self.randomDelayMax = 20
        self.randomDelay = 0.0
        
    def getSoundFile(self):
        return self.sndFile
        
    def getLooping(self):
        return int(self.looping)
        
    def getVolume(self):
        return self.volume
        
    def loadEntityValues(self):
        self.sndFile = self.getEntityValue("soundfile")
        self.looping = self.getEntityValueInt("looping")
        self.volume = self.getEntityValueFloat("volume")
        self.randomDelayMin = self.getEntityValueFloat("randomDelayMin")
        self.randomDelayMax = self.getEntityValueFloat("randomDelayMax")
        
    def think(self):
        if self.getEntityState() == self.StatePlaying:
            if self.looping == self.LoopRandom:
                if self.getEntityStateElapsed() >= self.randomDelay:
                    self.Play()
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        print self.getEntityValueBool("playnow")
        if self.getEntityValueBool("playnow"):
            print "Play now!"
            self.Play()
            
    def FadeIn(self, time = 1.0):
        self.sendUpdate('fadeIn', [float(time)])
        self.setEntityState(self.StatePlaying)
        
    def FadeOut(self, time = 1.0):
        self.sendUpdate('fadeOut', [float(time)])
        self.setEntityState(self.StateStopped)
                
    def Play(self):
        self.b_setEntityState(self.StatePlaying)
        
        if self.looping == self.LoopRandom:
            self.randomDelay = random.uniform(self.randomDelayMin, self.randomDelayMax)
            
    def Stop(self):
        self.b_setEntityState(self.StateStopped)

    def unload(self):
        self.sndFile = None
        self.looping = None
        self.volume = None
        self.randomDelay = None
        self.randomDelayMin = None
        self.randomDelayMax = None
        DistributedEntityAI.unload(self)
