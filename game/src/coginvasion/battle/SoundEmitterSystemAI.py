"""Class that manages sounds for NPCs to react to."""

from direct.showbase.DirectObject import DirectObject

SOUND_COMBAT    = 1 << 0
SOUND_SPEECH    = 1 << 1
SOUND_MISC      = 1 << 2
SOUND_VP_JUMP   = 1 << 3

class Sound:
    
    def __init__(self, soundType, emitter, pos, volume = 1.0, duration = 1.0):
        self.soundType = soundType
        self.emitter = emitter
        self.origin = pos
        # Volume really means max distance of sound (volume of 1.0 means 75 units max distance)
        self.volume = volume * 75.0
        self.duration = duration
        self.emitTime = globalClock.getFrameTime()
        
    def getLifeTime(self):
        return globalClock.getFrameTime() - self.emitTime
        
    def isExpired(self):
        return self.getLifeTime() > self.duration

class SoundEmitterSystemAI(DirectObject):
    
    def __init__(self):
        self.sounds = []
        
    def startup(self):
        taskMgr.add(self.__update, 'soundEmitterSystem-update')
        
    def shutdown(self):
        taskMgr.remove('soundEmitterSystem-update')
        self.sounds = None
    
    def clearSounds(self):
        self.sounds = []
        
    def getSounds(self):
        """Returns list of currently emitting sounds."""
        return self.sounds
        
    def emitSound(self, soundType, emitter, pos, volume = 1.0, duration = 1.0):
        self.sounds.append(Sound(soundType, emitter, pos, volume, duration))
        
    def __update(self, task):
        if len(self.sounds) == 0:
            return task.cont
            
        expired = []
            
        for sound in self.sounds:
            if sound.isExpired():
                expired.append(sound)
                
        for sound in expired:
            self.sounds.remove(sound)
        
        return task.cont
