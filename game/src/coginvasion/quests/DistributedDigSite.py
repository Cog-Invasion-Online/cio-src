"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDigSite.py
@author Maverick Liberty
@date November 25, 2017

"""

from src.coginvasion.quests.DistributedInspectionSite import DistributedInspectionSite
from direct.interval.IntervalGlobal import Sequence, Parallel, ParallelEndTogether
from direct.interval.IntervalGlobal import LerpPosInterval, LerpColorScaleInterval, LerpHprScaleInterval, Wait
from direct.interval.IntervalGlobal import ProjectileInterval, SoundInterval, LerpScaleInterval, ActorInterval, Func
from direct.interval.Interval import ShowInterval
from panda3d.core import TransparencyAttrib

from src.coginvasion.gui.CutsceneGUI import CutsceneGUI

NO_COLOR = (0.0, 0.0, 0.0, 0.0)
SHOVEL_APPEAR_TIME = 0.75
FADE_SHOVEL_TIME = 1.5
MOUND_INITIAL_SCALE = 0.01
MOUND_MAX_SCALE = 2.5
PACKAGE_MOVE_UP_TIME = 1.5
PACKAGE_MAX_HEIGHT = 3.0
PACKAGE_JUMP_TO_AVATAR_TIME = 1.0
DIG_DURATION = 12.0

class DistributedDigSite(DistributedInspectionSite):
    
    def __init__(self, cr):
        DistributedInspectionSite.__init__(self, cr)
        self.digSfx = None
        self.shovelAppearSfx = None
        self.itemRecoveredSfx = None
        self.track = None
        self.cutscene = None
        
    def announceGenerate(self):
        DistributedInspectionSite.announceGenerate(self)
        self.digSfx = loader.loadSfx('phase_5.5/audio/sfx/burrow.ogg')
        self.digSfx.setPlayRate(0.5)
        
        self.shovelAppearSfx = loader.loadSfx('phase_5/audio/sfx/General_device_appear.ogg')
        self.itemRecoveredSfx = loader.loadSfx('phase_3.5/audio/sfx/ci_s_money_smallBucks.ogg')
        self.cutscene = CutsceneGUI()
        
    def disable(self):
        if self.track:
            self.track.pause()
            self.track = None
        if self.cutscene:
            self.cutscene.unload()
            self.cutscene = None
        self.digSfx = None
        self.shovelAppearSfx = None
        self.itemRecoveredSfx = None
        DistributedInspectionSite.disable(self)
        
    def requestEnter(self):
        if self.canEnter():
            self.track = self.__getDigAndRecoverItemInterval(base.localAvatar)
            self.track.start()
        
    def generatePackage(self):
        # Generates and returns a hidden package.
        package = loader.loadModel('phase_5/models/char/tt_r_prp_ext_piePackage.bam')
        package.setTransparency(TransparencyAttrib.MAlpha)
        package.ls()
        package.hide()
        return package
    
    def __getItemRecoveredInterval(self, package, avatar):
        # Generates the item recovered item. Requires the avatar that dug.
        x, y, z = avatar.getPos(self)

        return Sequence(
            ShowInterval(package),
            ParallelEndTogether(
                # Move the package up
                LerpPosInterval(package, 
                    duration=PACKAGE_MOVE_UP_TIME,
                    pos=(0.0,0.0,PACKAGE_MAX_HEIGHT),
                    startPos=(0.0,0.0,-1),
                    blendType='easeOut'
                ),
                
                # Scale and turn the package.
                LerpHprScaleInterval(package,
                    duration=PACKAGE_MOVE_UP_TIME,
                    hpr=(360.0,0.0,0.0),
                    scale=(1.0,1.0,1.0),
                    blendType='easeInOut'
                )
            ),

            # We have to fix the H or the package won't go to the avatar correctly.
            Func(package.headsUp, avatar),
            ParallelEndTogether(
                ProjectileInterval(package,
                    duration=PACKAGE_JUMP_TO_AVATAR_TIME,
                    startPos=(0.0,0.0,PACKAGE_MAX_HEIGHT),
                    endPos=(x,y,z)
                ),
                
                LerpColorScaleInterval(package,
                    duration=PACKAGE_JUMP_TO_AVATAR_TIME,
                    colorScale=NO_COLOR,
                    blendType='easeOut'
                )
            ),
            
            SoundInterval(self.itemRecoveredSfx, node=avatar, duration=3.0)
        )
    
    def generateMound(self):
        # Generates and returns a hidden mound.
        mound = loader.loadModel('phase_5.5/models/estate/dirt_mound.bam')
        mound.setScale(MOUND_INITIAL_SCALE)
        
        moundShadow = loader.loadModel('phase_3/models/props/drop_shadow.bam')
        moundShadow.reparentTo(self)
        moundShadow.setZ(self.floorMarker.getZ())
        moundShadow.setScale(MOUND_INITIAL_SCALE)
        moundShadow.hide()
        
        mound.hide()
        return mound, moundShadow
    
    def __getEnlargePileInterval(self, mound, startScale, scale, startPos, pos, duration = 1.0):
        # Moves the pile up and scales the mound object.
        return ParallelEndTogether(
            LerpScaleInterval(mound, 
                duration,
                scale,
                startScale=startScale,
                blendType='easeInOut'
            ),

            LerpPosInterval(mound, 
                duration,
                pos,
                startPos=startPos,
                blendType='easeInOut'
            ),
        )
        
    def __getMakePileTrack(self, mound, shadow, avatar):
        scaleIncr = float(MOUND_MAX_SCALE / DIG_DURATION)
        posIncr = float(1.0 / DIG_DURATION)
        track = Sequence(ShowInterval(mound))
        
        scale = MOUND_INITIAL_SCALE
        pos = (0.0, 0.0, -0.25)
        for i in range(int(DIG_DURATION)):
            newScale = (scale + scaleIncr) if (scale + scaleIncr) < MOUND_MAX_SCALE else MOUND_MAX_SCALE
            newPos = (0.0, 0.0, pos[2] + posIncr) if (pos[2] + posIncr) < 1.0 else (0.0, 0.0, 1.0)
            parallelIval = Parallel()

            if (i % 2 == 0) or (i == int(DIG_DURATION) - 1):
                parallelIval.append(SoundInterval(self.digSfx, node=avatar, duration=0.55))

            parallelIval.append(self.__getEnlargePileInterval(mound, 
                scale, newScale, pos, newPos, 1.0))
            track.append(parallelIval)

            scale = newScale
            pos = newPos
    
        return Parallel(track,
            
            Sequence(
                Wait(1.0),
                ShowInterval(shadow),
                LerpScaleInterval(shadow, 
                    DIG_DURATION + 1.0, 
                    MOUND_MAX_SCALE - 1.25, 
                    startScale=MOUND_INITIAL_SCALE, 
                    blendType='easeInOut'
                )
            )
        )
    
    def __getPileFadeAwayInterval(self, mound):
        return LerpColorScaleInterval(mound, 
            duration=FADE_SHOVEL_TIME/2.0,
            colorScale=NO_COLOR,
            blendType='easeOut'
        )
        
    def generateShovel(self):
        # Generates and returns a hidden shovel.
        shovel = loader.loadModel('phase_5.5/models/estate/shovels.bam').find('**/shovelA')
        shovel.setTransparency(TransparencyAttrib.MAlpha)
        shovel.setHpr(-90, 216, 0)
        shovel.setX(0.2)
        shovel.hide()
        return shovel
    
    def __getShovelAppearInterval(self, shovel, avatar):
        # Must pass the shovel and the avatar using the shovel.
        return Parallel(
            Sequence(
                Func(shovel.reparentTo, avatar.find('**/def_joint_right_hold')),
                ShowInterval(shovel),
                SoundInterval(self.shovelAppearSfx, node=avatar, duration=1.0)
            ),
            
            LerpScaleInterval(shovel, 
                duration=SHOVEL_APPEAR_TIME,
                scale=(1.0, 1.0, 1.0),
                startScale=0.01,
                blendType='easeOut'
            )
        )
    
    def __getShovelDisappearInterval(self, shovel):
        return Sequence(
            LerpColorScaleInterval(shovel, 
                duration = FADE_SHOVEL_TIME,
                colorScale = NO_COLOR,
                blendType = 'easeOut'),
            Func(shovel.removeNode)
        )
    
    def __getDigAndRecoverItemInterval(self, avatar):
        shovel = self.generateShovel()

        mound, moundShadow = self.generateMound()
        mound.reparentTo(self)
        
        package = self.generatePackage()
        package.reparentTo(self)
        
        def cleanupObjects():
            mound.removeNode()
            moundShadow.removeNode()
            package.removeNode()
        
        return Parallel(
            Func(self.floorMarker.hide),
            Func(self.text.hide),
            Func(self.cr.playGame.getPlace().fsm.request, 'stop'),
            Func(avatar.headsUp, self),
            Func(self.cutscene.show),
            Func(self.cutscene.takeCameraControlTo, (self.getX() + 4.0, self.getY() + 15.0, self.getZ() + 12.5), (0, 0, 0)),
            Func(base.camera.headsUp, self),
            Func(base.camera.setP, -35),
            Func(self.cutscene.enter),

            ParallelEndTogether(
                ActorInterval(avatar, 'start-dig'),
                self.__getShovelAppearInterval(shovel, avatar)
            ),
                        
            Wait(1.0),
            
            Parallel(
                Sequence(
                    ActorInterval(avatar, 'loop-dig', loop=1, duration=DIG_DURATION + 0.5),
                    Parallel(
                        ActorInterval(avatar, 'start-dig', playRate=-1),
                        self.__getShovelDisappearInterval(shovel)
                    ),
                    ActorInterval(avatar, 'neutral', loop=1)
                ),

                Sequence(
                    Wait(0.25),
                    self.__getMakePileTrack(mound, moundShadow, avatar),
                    self.__getItemRecoveredInterval(package, avatar),
                    self.__getPileFadeAwayInterval(mound),
                    Func(self.floorMarker.show),
                    Func(self.text.show),
                    Func(cleanupObjects),
                    Func(self.cutscene.exit),
                    Func(self.cr.playGame.getPlace().fsm.request, 'walk')
                )
            )
        )
