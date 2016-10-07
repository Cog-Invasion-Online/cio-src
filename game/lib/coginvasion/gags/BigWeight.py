########################################
# Filename: BigWeight.py
# Created by: DecodedLogic (30Aug15)
########################################

from lib.coginvasion.gags.DropGag import DropGag
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpScaleInterval, Func, Wait, Parallel
from direct.showutil import Effects
from pandac.PandaModules import OmniBoundingVolume, Point3, CollisionSphere, CollisionNode, CollisionHandlerEvent, BitMask32

class BigWeight(DropGag):

    def __init__(self):
        DropGag.__init__(self, CIGlobals.BigWeight, 'phase_5/models/props/weight-mod.bam', 'phase_5/models/props/weight-chan.bam',
                         45, GagGlobals.WEIGHT_DROP_SFX, GagGlobals.WEIGHT_MISS_SFX, 1, 1)
        self.setImage('phase_3.5/maps/big-weight.png')

    def startDrop(self):
        if self.gag and self.dropLoc:
            endPos = self.dropLoc
            startPos = Point3(endPos.getX(), endPos.getY(), endPos.getZ() + 20)
            self.gag.setPos(startPos.getX(), startPos.getY() + 2, startPos.getZ())
            self.gag.setScale(self.gag.getScale() * 0.75)
            self.gag.node().setBounds(OmniBoundingVolume())
            self.gag.node().setFinal(1)
            self.gag.headsUp(self.avatar)
            self.buildCollisions()
            objectTrack = Sequence()
            animProp = LerpPosInterval(self.gag, self.fallDuration, endPos, startPos = startPos)
            bounceProp = Effects.createZBounce(self.gag, 2, endPos, 0.5, 1.5)
            objAnimShrink = Sequence(Wait(0.5), Func(self.gag.reparentTo, render), animProp, bounceProp)
            objectTrack.append(objAnimShrink)
            dropShadow = loader.loadModel('phase_3/models/props/drop_shadow.bam')
            dropShadow.reparentTo(render)
            dropShadow.setPos(endPos)
            shadowTrack = Sequence(LerpScaleInterval(dropShadow, self.fallDuration + 0.1, dropShadow.getScale()*2,
                                startScale=Point3(0.01, 0.01, 0.01)), Wait(0.3), Func(dropShadow.removeNode))
            Parallel(Sequence(Wait(self.fallDuration), Func(self.completeDrop), Wait(4), Func(self.cleanupGag)), objectTrack, shadowTrack).start()
            self.dropLoc = None
            
    def buildCollisions(self):
        gagSph = CollisionSphere(0, 0, 0, 2)
        gagSensor = CollisionNode('gagSensor')
        gagSensor.addSolid(gagSph)
        sensorNP = self.gag.attachNewNode(gagSensor)
        sensorNP.setCollideMask(BitMask32(0))
        sensorNP.node().setFromCollideMask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)
        event = CollisionHandlerEvent()
        event.set_in_pattern("%fn-into")
        event.set_out_pattern("%fn-out")
        base.cTrav.addCollider(sensorNP, event)
        self.avatar.acceptOnce('gagSensor-into', self.onCollision)
