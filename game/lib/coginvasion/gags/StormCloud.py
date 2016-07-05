"""

  Filename: StormCloud.py
  Created by: DecodedLogic (30Aug15)

"""

from lib.coginvasion.gags.SquirtGag import SquirtGag
from lib.coginvasion.gags.LocationGag import LocationGag
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.gags import GagUtils
from lib.coginvasion.globals import CIGlobals
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.interval.IntervalGlobal import Parallel, LerpScaleInterval, ParticleInterval
from direct.interval.IntervalGlobal import ActorInterval
from panda3d.core import Point3

class StormCloud(SquirtGag, LocationGag):

    def __init__(self):
        SquirtGag.__init__(self, CIGlobals.StormCloud, GagGlobals.getProp(4, 'stormcloud-mod'), 60,
                           GagGlobals.CLOUD_HIT_SFX, None, GagGlobals.CLOUD_MISS_SFX, None, None, None, None, 1, 1)
        LocationGag.__init__(self, 10, 50)
        LocationGag.setShadowData(self, isCircle = True, shadowScale = 0.75)
        self.setImage('phase_3.5/maps/storm-cloud.png')
        self.entities = []
        self.searchRadius = 6
        self.timeout = 3.0

    def buildEntity(self):
        cloud = Actor(self.model, {'chan' : GagGlobals.getProp(4, 'stormcloud-chan')})
        trickleFx = GagUtils.loadParticle(5, 'trickleLiquidate')
        rainFx01 = GagUtils.loadParticle(5, 'liquidate')
        rainFx02 = GagUtils.loadParticle(5, 'liquidate')
        rainFx03 = GagUtils.loadParticle(5, 'liquidate')
        rainEffects = [rainFx01, rainFx02, rainFx03]
        entity = [cloud, [trickleFx, rainEffects]]
        self.entities.append(entity)
        return cloud, trickleFx, rainEffects, entity

    def destroyEntity(self, ent):
        for entity in self.entities:
            if entity == ent:
                self.entities.remove(entity)

    def startEntity(self, cog):
        if not cog:
            self.completeSquirt()
            return
        scaleUpPoint = Point3(1.5, 1.5, 1.5)
        rainDelay = 1
        effectDelay = 0.3
        cloudHold = 4.7
        tContact = 2.4
        if cog.isDead():
            cloudHold = 1.7
        cloud01, trickleFx, rainEffects, entity = self.buildEntity()
        cloud01.setZ(cog.suitPlan.getNametagZ() + 2)
        cloud01.reparentTo(cog)
        cloud02 = Actor(self.model, {'chan' : GagGlobals.getProp(4, 'stormcloud-chan')})
        cloud02.reparentTo(cloud01)
        def damageCog():
            if self.isLocal():
                cog.sendUpdate('hitByGag', [self.getID()])

        def __getCloudTrack(cloud, useEffect = 1):
            track = Sequence(
                Func(cloud.pose, 'chan', 0),
                LerpScaleInterval(cloud, 1.5, scaleUpPoint, startScale = GagGlobals.PNT3NEAR0),
                Wait(rainDelay)
            )
            if useEffect == 1:
                pTrack = Parallel()
                delay = trickleDuration = cloudHold * 0.25
                trickleTrack = ParticleInterval(trickleFx, cloud, worldRelative=0, duration=trickleDuration, cleanup=True)
                track.append(trickleTrack)
                for i in range(0, 3):
                    dur = cloudHold - 2 * trickleDuration
                    pTrack.append(Sequence(Wait(delay), ParticleInterval(rainEffects[i], cloud, worldRelative=0, duration=dur, cleanup=True)))
                    delay += effectDelay

                pTrack.append(Sequence(
                    Wait(3 * effectDelay),
                    ActorInterval(cloud, 'chan', startTime = 1, duration = cloudHold))
                )
                damageTrack = Sequence()
                if cog.getHealth() - self.getDamage() <= 0:
                    damageTrack.append(Func(cog.d_disableMovement, wantRay = True))
                    damageTrack.append(Func(damageCog))
                else:
                    damageTrack.append(Wait(tContact))
                    damageTrack.append(Func(damageCog))
                pTrack.append(damageTrack)
                track.append(pTrack)
            else:
                track.append(ActorInterval(cloud, 'chan', startTime = 1, duration = cloudHold))
            track.append(LerpScaleInterval(cloud, 0.5, GagGlobals.PNT3NEAR0))
            track.append(Func(GagUtils.destroyProp, cloud))
            return track
        tracks = Parallel()
        soundTrack01 = self.getSoundTrack(1.3, self.avatar)
        soundTrack02 = self.getSoundTrack(3.4, self.avatar)
        tracks.append(soundTrack01)
        tracks.append(soundTrack02)
        cloud01Track = __getCloudTrack(cloud01)
        cloud02Track = __getCloudTrack(cloud02, useEffect = 0)
        tracks.append(cloud01Track)
        tracks.append(cloud02Track)
        tracks.append(Func(self.destroyEntity, entity))
        tracks.start()

    def getClosestCog(self, radius = 6):
        loc = LocationGag.getLocation(self)
        for cog in base.cr.doId2do.values():
            if cog.__class__.__name__ in CIGlobals.SuitClasses:
                if cog.getPlace() == base.localAvatar.zoneId:
                    distance = (cog.getPos(render) - loc).length()
                    if distance <= radius:
                        return cog

    def start(self):
        SquirtGag.start(self)
        LocationGag.start(self, self.avatar)

    def completeSquirt(self):
        if game.process == 'client':
            LocationGag.complete(self)
            self.reset()

    def unEquip(self):
        LocationGag.cleanupLocationSeeker(self)
        SquirtGag.unEquip(self)
        self.completeSquirt()

    def considerSquirt(self):
        cog = self.getClosestCog(self.searchRadius)
        self.startEntity(cog)
        if cog:
            self.avatar.d_trapActivate(self.getID(), self.avatar.doId, 0, cog.doId)
        self.completeSquirt()

    def onActivate(self, ignore, cog):
        self.startEntity(cog)

    def release(self):
        LocationGag.release(self)
        if self.isLocal():
            self.startTimeout()
        actorTrack = LocationGag.getActorTrack(self)
        LocationGag.getSoundTrack(self).start()
        if actorTrack:
            if self.isLocal():
                actorTrack.append(Func(self.considerSquirt))
            actorTrack.start()
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])
