"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Fired.py
@author Brian Lach
@date March 31, 2019

"""

from panda3d.core import Point3, NodePath, ColorBlendAttrib

from direct.interval.IntervalGlobal import Func, ActorInterval, LerpScaleInterval, LerpColorScaleInterval, Sequence, Wait

from src.coginvasion.base.Precache import precacheModel, precacheSound, precacheScene
from src.coginvasion.globals import CIGlobals
from src.coginvasion.attack.BaseAttack import BaseAttack
from src.coginvasion.attack.LobProjectile import LobProjectile
from src.coginvasion.attack.Attacks import ATTACK_FIRED, ATTACK_HOLD_NONE
from Fired_Shared import Fired_Shared
import SuitAttacks

GlowMdl = "phase_14/models/props/lightglow.egg"

FireProj = None
def getFireProj():
    global FireProj
    if not FireProj:
        fireroot = NodePath('fireroot')
        fireroot.setScale(1.25)
        fireroot.setBillboardAxis()
        #glow = loader.loadModel(GlowMdl)
        #glow.reparentTo(fireroot)
        #glow.setTransparency(1)
        #glow.setColorScale(1, 0.5, 0, 0.5)
        #glow.setY(-0.01)
        #glow.setTwoSided(1)
        #glow.setScale(0.85)
        fire = SuitAttacks.getSuitParticle("fire").copyTo(fireroot)
        FireProj = fireroot
    return FireProj

class FiredProjectile(LobProjectile):

    ImpactSoundPath = "phase_14/audio/sfx/SA_hot_air_flame_hit.ogg"
    FlameEmitSfx = "phase_14/audio/sfx/SA_hot_air_flame_emit.ogg"

    def __init__(self, cr):
        LobProjectile.__init__(self, cr)
        self.emitSound = None
        self.scaleIval = None

    def announceGenerate(self):
        LobProjectile.announceGenerate(self)
        self.setLightOff(1)
        self.hide(CIGlobals.ShadowCameraBitmask)
        self.hide(CIGlobals.ReflectionCameraBitmask)

        fireroot = getFireProj().copyTo(self)

        if not self.emitSound:
            self.emitSound = base.loadSfxOnNode(self.FlameEmitSfx, self)
        self.emitSound.play()

        self.scaleIval = LerpScaleInterval(fireroot, 0.2, Point3(1.25), Point3(0.01))
        self.scaleIval.start()

    def disable(self):
        if self.scaleIval:
            self.scaleIval.finish()
        self.scaleIval = None
        if self.emitSound:
            base.audio3d.detachSound(self.emitSound)
        self.emitSound = None
        LobProjectile.disable(self)

    def impact(self, pos, lastPos):
        CIGlobals.makeDustCloud(pos, scale = 0.25,
                                        sound = self.impactSound,
                                        color = (0.2, 0.2, 0.2, 0.6))

class Fired(BaseAttack, Fired_Shared):

    Name = "Fired"
    ID = ATTACK_FIRED
    Hold = ATTACK_HOLD_NONE

    def __init__(self):
        BaseAttack.__init__(self)
        self.glowTrack = None
        self.glow = None

    @classmethod
    def doPrecache(cls):
        super(Fired, cls).doPrecache()
        precacheModel(GlowMdl)
        precacheSound(FiredProjectile.ImpactSoundPath)
        precacheSound(FiredProjectile.FlameEmitSfx)
        precacheScene(SuitAttacks.getSuitParticle("fire"))

    def load(self):
        self.glow = loader.loadModel(GlowMdl)
        self.glow.reparentTo(self.avatar)
        self.glow.setLightOff(1)
        self.glow.setMaterialOff(1)
        self.glow.setP(90)
        self.glow.setTransparency(1)
        self.glow.setDepthWrite(False)
        self.glow.setDepthOffset(1)
        self.glow.setColorScale(1, 0.5, 0, 0)
        self.glow.setScale(3)
        self.glow.hide(CIGlobals.ShadowCameraBitmask)

        self.glowTrack = Sequence(Func(self.glow.show), LerpColorScaleInterval(self.glow, self.EmitFlameIval / 2, (1, 0.5, 0, 0.5),
                                                         (1, 0.5, 0, 0), blendType = 'easeInOut'),
                                  LerpColorScaleInterval(self.glow, self.EmitFlameIval / 2, (1, 0.5, 0, 0),
                                                         (1, 0.5, 0, 0.5), blendType = 'easeInOut'), Func(self.glow.hide))

    def cleanup(self):
        if self.glowTrack:
            self.glowTrack.finish()
        self.glowTrack = None
        if self.glow:
            self.glow.removeNode()
        self.glow = None
        BaseAttack.cleanup(self)
        
    def unEquip(self):
        if not BaseAttack.unEquip(self):
            return False
        
        self.avatar.doingActivity = False
            
        return True

    def onSetAction(self, action):
        if action == self.StateIdle:
            self.avatar.doingActivity = False
        else:
            self.avatar.doingActivity = True

        if action == self.StateAttack:
            self.avatar.pingpong('magic2', 1, None, 32, 50)
            self.setAnimTrack(Sequence(Func(self.glowTrack.start), Wait(self.EmitFlameIval)),
                              startNow = True, looping = True)
        elif action == self.StateBegin:
            self.setAnimTrack(ActorInterval(self.avatar, 'magic2', endFrame = 32),
                              True)
        elif action == self.StateEnd:
            self.setAnimTrack(ActorInterval(self.avatar, 'magic2', startFrame = 50),
                              True)
