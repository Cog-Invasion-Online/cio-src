"""

  Filename: SeltzerBottle.py
  Created by: DecodedLogic (10Jul15)

"""

from lib.coginvasion.gags.SquirtGag import SquirtGag
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals
from pandac.PandaModules import Point3

class SeltzerBottle(SquirtGag):

    def __init__(self):
        SquirtGag.__init__(self, CIGlobals.SeltzerBottle, "phase_3.5/models/props/bottle.bam", 21,
                            GagGlobals.SELTZER_HIT_SFX, GagGlobals.SELTZER_SPRAY_SFX, GagGlobals.SELTZER_MISS_SFX, 'hold-bottle',
                            30, 64, playRate = 1.2)
        self.setHealth(GagGlobals.SELTZER_HEAL)
        self.setImage('phase_3.5/maps/seltzer_bottle.png')
        self.anim = 'hold-bottle'
        self.holdTime = 2
        self.sprayScale = 0.2
        self.timeout = 3.0

    def start(self):
        super(SeltzerBottle, self).start()
        self.origin = self.getSprayStartPos()

    def release(self):
        if self.isLocal():
            self.startTimeout()
        if self.canSquirt:
            self.sprayRange = self.avatar.getPos(render) + Point3(0, GagGlobals.SELTZER_RANGE, 0)
            self.startSquirt(self.sprayScale, self.holdTime)
        else:
            self.completeSquirt()
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])

    def getSprayStartPos(self):
        self.sprayJoint = self.gag.find('**/joint_toSpray')
        startNode = hidden.attachNewNode('pointBehindSprayProp')
        startNode.reparentTo(self.avatar)
        startNode.setPos(self.sprayJoint.getPos(self.avatar) + Point3(0, -0.4, 0))
        point = startNode.getPos(render)
        startNode.removeNode()
        del startNode
        return point
