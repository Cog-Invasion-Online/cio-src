"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SectionedSound.py
@author Brian Lach
@date August 05, 2015

"""

from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *

class AudioClip(DirectObject):
    notify = directNotify.newCategory("SectionedMusic")

    def __init__(self, chunks):
        DirectObject.__init__(self)
        self.ival = None
        self.chunks = chunks

    def playFromIndex(self, startIndex):
        self.stop()

        self.ival = Sequence()
        index = 0
        for chunk in self.chunks:
            if index >= startIndex:
                self.ival.append(SoundInterval(chunk, volume = 0.5, duration = chunk.length() / 2, taskChain = "TournamentMusicThread"))

                if index < len(self.chunks) - 1:
                    self.ival.append(Func(messenger.send, 'AudioClip_partDone', [index]))
            index += 1
        self.ival.append(Func(messenger.send, 'AudioClip_clipDone'))
        #self.ival.append(Func(self.cleanup))
        self.ival.start()

    def playAllParts(self):
        self.stop()


        self.ival = Sequence()
        index = 0
        for chunk in self.chunks:
            self.ival.append(SoundInterval(chunk, volume = 0.5, duration = chunk.length() / 2, taskChain = "TournamentMusicThread"))

            if index < len(self.chunks) - 1:
                self.ival.append(Func(messenger.send, 'AudioClip_partDone', [index]))
            index += 1
        self.ival.append(Func(messenger.send, 'AudioClip_clipDone'))
        #self.ival.append(Func(self.cleanup))
        self.ival.start()

    def stop(self):
        if self.ival:
            self.ival.pause()
            self.ival = None

    def cleanup(self):
        self.stop()
        self.chunks = None
