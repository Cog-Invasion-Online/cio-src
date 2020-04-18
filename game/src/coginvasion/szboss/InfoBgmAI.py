from DistributedEntityAI import DistributedEntityAI

class InfoBgmAI(DistributedEntityAI):
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.songName = ""
        self.volume = 1.0
        self.looping = False
        
    def delete(self):
        self.songName = None
        self.volume = None
        self.looping = None
        DistributedEntityAI.delete(self)
        
    def loadEntityValues(self):
        self.songName = self.getEntityValue("songName")
        self.looping = self.getEntityValueBool("looping")
        self.volume = self.getEntityValueFloat("volume")
        
    def getSongName(self):
        return self.songName
        
    def getLooping(self):
        return self.looping
        
    def getVolume(self):
        return self.volume

    def PlayMusic(self, song = None, volume = None, looping = None):
        self.sendUpdate('playMusic')
        
    def StopMusic(self):
        self.sendUpdate('stopMusic')
        
    def FadeOut(self, time = 1.0):
        time = float(time)
        self.sendUpdate('fadeOut', [time])
