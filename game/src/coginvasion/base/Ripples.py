# File: R (Python 2.4)

from panda3d.core import *
from direct.interval.IntervalGlobal import *

class Ripples(NodePath):
    rippleCount = 0
    
    def __init__(self, parent = hidden):
        NodePath.__init__(self)
        self.assign(loader.loadModel("phase_4/models/props/ripples.bam"))
        self.reparentTo(parent)
        self.getChild(0).setZ(0.10000000000000001)
        self.seqNode = self.find('**/+SequenceNode').node()
        self.seqNode.setPlayRate(0)
        self.track = None
        self.trackId = Ripples.rippleCount
        Ripples.rippleCount += 1
        self.setBin('fixed', 100, 1)
        self.hide()
    
    def createTrack(self, rate = 1):
        tflipDuration = self.seqNode.getNumChildren() / float(rate) * 24
        self.track = Sequence(Func(self.show), Func(self.seqNode.play, 0, self.seqNode.getNumFrames() - 1),
                              Func(self.seqNode.setPlayRate, rate), Wait(tflipDuration), Func(self.seqNode.setPlayRate, 0),
                              Func(self.hide), name = 'ripples-track-%d' % self.trackId)

    def play(self, rate = 1):
        self.stop()
        self.createTrack(rate)
        self.track.start()

    def loop(self, rate = 1):
        self.stop()
        self.createTrack(rate)
        self.track.loop()

    def stop(self):
        if self.track:
            self.track.finish()

    def destroy(self):
        self.stop()
        self.track = None
        del self.seqNode
        self.removeNode()