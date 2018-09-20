from Entity import Entity

class InfoBgm(Entity):

    def PlayMusic(self, song, volume, looping):
        base.playMusic(song, looping != "0", float(volume))
        
    def StopMusic(self):
        base.stopMusic()