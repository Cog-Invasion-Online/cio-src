"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDeathmatchBattle.py
@author Brian Lach
@date April 11, 2019

"""

from src.coginvasion.battle.DistributedBattleZone import DistributedBattleZone
from DeathmatchRules import DeathmatchRules

class DistributedDeathmatchBattle(DistributedBattleZone):

    def makeGameRules(self):
        return DeathmatchRules(self)
        
    def respawn(self):
        self.gameRules.onPlayerRespawn()

    def generate(self):
        DistributedBattleZone.generate(self)
        from src.coginvasion.szboss import AmbientGeneric, FuncWater, Ropes, InfoBgm, EnvLightGlow, EnvParticleSystem, PointSpotlight
        base.bspLoader.linkEntityToClass("func_water", FuncWater.FuncWater)
        base.bspLoader.linkEntityToClass("rope_begin", Ropes.RopeBegin)
        base.bspLoader.linkEntityToClass("rope_keyframe", Ropes.RopeKeyframe)
        base.bspLoader.linkEntityToClass("info_bgm", InfoBgm.InfoBgm)
        base.bspLoader.linkEntityToClass("env_lightglow", EnvLightGlow.EnvLightGlow)
        base.bspLoader.linkEntityToClass("env_particlesystem", EnvParticleSystem.EnvParticleSystem)
        base.bspLoader.linkEntityToClass("point_spotlight", PointSpotlight.PointSpotlight)
