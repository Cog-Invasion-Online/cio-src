from panda3d.core import NodePath, ModelNode

from src.coginvasion.szboss.DistributedEntity import DistributedEntity

import random
import fnmatch

class AmbientGeneric(DistributedEntity):
    
    StateStopped = 0
    StatePlaying = 1
    
    # Spawn flags
    SF_PlayEverywhere = 1 << 0
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.assign(NodePath(ModelNode('ambientGeneric')))
        self.node().setPreserveTransform(ModelNode.PTLocal)

        self.sndFile = ""
        self.looping = False
        self.volume = 1.0
        
        self.numWildcardSounds = 0
        
    def fadeIn(self, time):
        self.setEntityState(self.StatePlaying)
        for snd in self.sounds.values():
            base.fadeAudio(time, snd, 0.0, self.volume)
            
    def fadeOut(self, time):
        for snd in self.sounds.values():
            base.fadeAudio(time, snd, self.volume, 0.0)
        
    def setSoundFile(self, sndfile):
        self.sndFile = sndfile
        
    def setLooping(self, looping):
        self.looping = (looping == 1)
        
    def setVolume(self, volume):
        self.volume = volume
        
    def soundHasWildcard(self):
        return "*" in self.sndFile
        
    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)

        if self.soundHasWildcard():
            from panda3d.core import VirtualFileSystem, Filename
            fsnd = Filename.fromOsSpecific(self.sndFile)
            vfs = VirtualFileSystem.getGlobalPtr()
            flist = vfs.scanDirectory(fsnd.getDirname())
            soundFiles = []
            for f in flist.getFiles():
                if fnmatch.fnmatch(f.getFilename().getBasename(), fsnd.getBasename()):
                    soundFiles.append(f.getFilename())
            self.numWildcardSounds = len(soundFiles)
            for i in range(self.numWildcardSounds):
                soundfname = soundFiles[i]
                self.addSound("sound{0}".format(i), soundfname.getFullpath(), not self.hasSpawnFlags(self.SF_PlayEverywhere))
        else:
            self.addSound("sound", self.sndFile, not self.hasSpawnFlags(self.SF_PlayEverywhere))
            
        # Now that we have the sounds, reset the state in case we are currently playing
        self.setEntityState(self.entState)
        
    def setEntityState(self, state):
        self.stopAllSounds()
        
        if state == self.StatePlaying:
            print "SetEntityState: play sound!"
            idx = ""
            if self.soundHasWildcard():
                idx = random.randint(0, self.numWildcardSounds - 1)
            if self.looping:
                self.loopSound("sound{0}".format(idx), self.volume)
            else:
                self.playSound("sound{0}".format(idx), self.volume)

    def unload(self):
        self.sndFile = None
        self.looping = None
        self.volume = None
        self.numWildcardSounds = None
        DistributedEntity.unload(self)
