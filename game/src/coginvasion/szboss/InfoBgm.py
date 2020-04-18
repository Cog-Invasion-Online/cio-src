from DistributedEntity import DistributedEntity

class InfoBgm(DistributedEntity):
    
    NeedNode = False
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.songName = ""
        self.volume = 1.0
        self.looping = False
        
    def setSongName(self, name):
        self.songName = name

    def setVolume(self, volume):
        self.volume = volume
        
    def setLooping(self, looping):
        self.looping = looping
        
    def playMusic(self):
        base.playMusic(self.songName, self.looping, self.volume)
        
    def fadeOut(self, time = 1.0):
        base.fadeOutMusic(time)
        
    def stopMusic(self):
        base.stopMusic()
        
    def delete(self):
        self.songName = None
        self.volume = None
        self.looping = None
        DistributedEntity.delete(self)
