"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Geyser.py
@author Maverick Liberty
@date August 17, 2015

"""

from src.coginvasion.gags.SquirtGag import SquirtGag
from src.coginvasion.gags.ChargeUpGag import ChargeUpGag
from src.coginvasion.gags import GagGlobals
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpScaleInterval
from direct.interval.IntervalGlobal import ActorInterval, LerpPosInterval, Parallel
from direct.interval.IntervalGlobal import SoundInterval
from panda3d.core import Point3

class Geyser(SquirtGag, ChargeUpGag):

    def __init__(self):
        SquirtGag.__init__(self, GagGlobals.Geyser, GagGlobals.getProp(5, 'geyser'), GagGlobals.GEYSER_HIT_SFX)
        ChargeUpGag.__init__(self, 24, 10, 50, 0.5, maxCogs = 4)
        self.setImage('phase_3.5/maps/geyser.png')
        self.entities = []
        self.timeout = 3.0

    def start(self):
        SquirtGag.start(self)
        ChargeUpGag.start(self, self.avatar)

    def unEquip(self):
        SquirtGag.unEquip(self)
        ChargeUpGag.unEquip(self)

    def buildGeyser(self):
        def clearNodes(entity, paths):
            for i in xrange(paths.getNumPaths()):
                paths[i].removeNode()

        geyserWater = loader.loadModel(self.model)
        waterRemoveSet = geyserWater.findAllMatches('**/hole')
        waterRemoveSet.addPathsFrom(geyserWater.findAllMatches('**/shadow'))
        clearNodes(geyserWater, waterRemoveSet)

        geyserMound = loader.loadModel(self.model)
        moundRemoveSet = geyserMound.findAllMatches('**/Splash*')
        moundRemoveSet.addPathsFrom(geyserMound.findAllMatches('**/spout'))
        clearNodes(geyserMound, moundRemoveSet)

        entitySet = [geyserWater, geyserMound]
        self.entities.append(entitySet)
        return entitySet

    def removeEntity(self, entity):
        for iEntity in self.entities:
            if iEntity == entity:
                self.entities.remove(iEntity)

    def onActivate(self, ignore, cog):
        self.startEntity(self.buildGeyser(), cog)

    def startEntity(self, entity, cog):
        geyserHold = 1.5
        scaleUpPoint = Point3(1.8, 1.8, 1.8)
        geyserWater = entity[0]
        geyserMound = entity[1]

        def showEntity(entity, cog):
            entity.reparentTo(render)
            entity.setPos(cog.getPos())

        def __getGeyserTrack():
            track = Sequence(
                Func(showEntity, geyserMound, cog),
                Func(showEntity, geyserWater, cog),
                LerpScaleInterval(geyserWater, 1.0, scaleUpPoint, startScale = GagGlobals.PNT3NEAR0),
                Wait(0.5 * geyserHold),
                LerpScaleInterval(geyserWater, 0.5, GagGlobals.PNT3NEAR0, startScale = scaleUpPoint),
                LerpScaleInterval(geyserMound, 0.5, GagGlobals.PNT3NEAR0),
                Func(geyserWater.removeNode),
                Func(geyserMound.removeNode),
                Func(self.removeEntity, entity)
            )
            return track

        def __getCogTrack():
            def handleHit():
                if self.isLocal():
                    cog.sendUpdate('hitByGag', [self.getID()])
            startPos = cog.getPos(render)
            cogFloat = Point3(0, 0, 14)
            cogEndPos = Point3(startPos[0] + cogFloat[0], startPos[1] + cogFloat[1], startPos[2] + cogFloat[2])
            suitType = cog.suitPlan.getSuitType()
            if suitType == 'A':
                startFlailFrame = 16
                endFlailFrame = 16
            else:
                startFlailFrame = 15
                endFlailFrame = 15
            track = Sequence()
            track.append(Func(cog.d_disableMovement))
            track.append(Wait(0.5))
            slipIval = Sequence(
                ActorInterval(cog, 'slip-backward', playRate=0.5, startFrame=0, endFrame=startFlailFrame - 1),
                Func(cog.pingpong, 'slip-backward', fromFrame=startFlailFrame, toFrame=endFlailFrame),
                Wait(0.5),
                Parallel(
                     ActorInterval(cog, 'slip-backward', playRate=1.0, startFrame=endFlailFrame),
                     Func(cog.startRay),
                     Func(handleHit)
                )
            )
            slipUp = LerpPosInterval(cog, 1.1, cogEndPos, startPos = startPos, fluid = 1)
            slipDn = LerpPosInterval(cog, 0.6, startPos, startPos = cogEndPos, fluid = 1)
            geyserMotion = Sequence(slipUp, slipDn)
            track.append(Parallel(slipIval, geyserMotion))
            if cog.getHealth() - self.getDamage() <= 0:
                track.append(Func(cog.d_enableMovement))
            return track

        if entity and cog:
            track = Sequence()
            track.append(Parallel(
                SoundInterval(self.hitSfx, node = self.avatar),
                Parallel(__getGeyserTrack(), __getCogTrack()))
            )
            track.start()

    def release(self):
        ChargeUpGag.release(self)
        self.reset()
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])
            cogs = ChargeUpGag.getSelectedCogs(self)
            for cog in cogs:
                if cog.getHealth() > 0:
                    geyser = self.buildGeyser()
                    self.startEntity(geyser, cog)
                    self.avatar.d_trapActivate(self.getID(), self.avatar.doId, 0, cog.doId)
