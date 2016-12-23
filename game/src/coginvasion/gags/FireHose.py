# Filename: FireHose.py
# Created by:  blach (15Nov15)

from pandac.PandaModules import Point3, Vec3

from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval, LerpScaleInterval, Parallel

from src.coginvasion.globals import CIGlobals
from SquirtGag import SquirtGag
import GagGlobals

class FireHose(SquirtGag):

    def __init__(self):
        SquirtGag.__init__(self, CIGlobals.FireHose, "phase_5/models/props/firehose-mod.bam", 30,
                            GagGlobals.NULL_SFX, GagGlobals.FIREHOSE_SFX, GagGlobals.NULL_SFX, 'firehose',
                            0, 0)
        self.setHealth(GagGlobals.FIREHOSE_HEAL)
        self.setImage('phase_3.5/maps/fire-hose.png')
        self.anim = 'phase_5/models/props/firehose-chan.bam'
        self.sprayScale = 0.2
        self.scale = 1.0
        self.holdTime = 0.0
        self.hydrant = None
        self.hydrantNode = None
        self.hydrantScale = None
        self.hoseTrack = None
        self.timeout = 6
        self.sprayRotation = Vec3(0, 5, 0)

    def start(self):
        self.deleteHoseStuff()

        def cleanupHydrantNode():
            if self.hydrantNode:
                self.hydrantNode.removeNode()
                self.hydrentNode = None

        SquirtGag.start(self)
        if self.isLocal():
            self.startTimeout()
        self.origin = self.getSprayStartPos()
        self.hydrant = loader.loadModel('phase_5/models/props/battle_hydrant.bam')
        self.gag.reparentTo(self.hydrant)
        self.gag.pose('chan', 2)
        self.hydrantNode = self.avatar.attachNewNode('hydrantNode')
        self.hydrantNode.clearTransform(self.avatar.getGeomNode().getChild(0))
        self.hydrantScale = self.hydrantNode.attachNewNode('hydrantScale')
        self.hydrant.reparentTo(self.hydrantScale)
        self.avatar.pose('firehose', 30)
        self.avatar.update(0)
        torso = self.avatar.getPart('torso')
        if 'dgm' in self.avatar.getTorso():
            self.hydrant.setPos(torso, 0, 0, -1.85)
        else:
            self.hydrant.setPos(torso, 0, 0, -1.45)
        base = self.hydrant.find('**/base')
        base.setColor(1, 1, 1, 0.5)
        base.setPos(self.avatar, 0, 0, 0)

        self.avatar.loop('neutral')

        tAppearDelay = 0.7
        dAnimHold = 5.1
        dHoseHold = 0.7
        tSprayDelay = 2.8
        track = Parallel()
        toonTrack = Sequence(Wait(tAppearDelay), ActorInterval(self.avatar, 'firehose'), Func(self.avatar.loop, 'neutral'))
        sprayTrack = Sequence(Wait(tSprayDelay), Func(self.release))
        propTrack = Sequence(Func(self.hydrantNode.reparentTo, self.avatar), LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.5, Point3(1, 1, 1.4),
            startScale=Point3(1, 1, 0.01)), LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.3, Point3(1, 1, 0.8), startScale=Point3(1, 1, 1.4)),
            LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1.2), startScale=Point3(1, 1, 0.8)),
            LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1), startScale=Point3(1, 1, 1.2)),
            ActorInterval(self.gag, 'chan', duration=dAnimHold), Wait(dHoseHold - 0.2),
            LerpScaleInterval(self.hydrantScale, 0.2, Point3(1, 1, 0.01), startScale=Point3(1, 1, 1)), Func(cleanupHydrantNode))
        track.append(toonTrack)
        track.append(sprayTrack)
        track.append(propTrack)
        track.start()
        self.hoseTrack = track

    def deleteHoseStuff(self):
        if self.hoseTrack:
            self.hoseTrack.pause()
            self.hoseTrack = None
        if self.hydrant:
            self.hydrant.removeNode()
            self.hydrant = None
        if self.hydrantNode:
            self.hydrantNode.removeNode()
            self.hydrantNode = None
        if self.hydrantScale:
            self.hydrantScale.removeNode()
            self.hydrantScale = None

    def delete(self):
        self.deleteHoseStuff()
        SquirtGag.delete(self)

    def release(self):
        if self.avatar.isEmpty():
            return
        self.sprayRange = self.avatar.getPos(render) + Point3(0, GagGlobals.SELTZER_RANGE, 0)
        self.doSpray(self.sprayScale, self.holdTime, self.sprayScale)
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])

    def getSprayStartPos(self):
        self.sprayJoint = self.gag.find('**/joint_water_stream')
        n = hidden.attachNewNode('pointBehindSprayProp')
        n.reparentTo(self.avatar)
        n.setPos(self.sprayJoint.getPos(self.avatar) + Point3(0, -0.55, 0))
        p = n.getPos(render)
        n.removeNode()
        del n
        return p
