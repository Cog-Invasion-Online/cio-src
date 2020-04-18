"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file DistributedToonAI.py
@author Brian Lach/Maverick Liberty
@date October 12, 2014

Revamped on June 15, 2018

"""

from panda3d.core import Point3, PerspectiveLens, LensNode, NodePath, Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

from src.coginvasion.avatar.Activities import ACT_DIE, ACT_VICTORY_DANCE, ACT_TOON_BOW, ACT_JUMP, ACT_TOON_POINT, ACT_TOON_PRESENT, ACT_PRESS_BUTTON, ACT_TOON_FALL
from src.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from src.coginvasion.avatar.AvatarTypes import *
from src.coginvasion.cog.ai.RelationshipsAI import *
from src.coginvasion.globals import CIGlobals
import ToonGlobals
import ToonDNA

import random

class DistributedToonAI(DistributedAvatarAI, ToonDNA.ToonDNA):
    notify = directNotify.newCategory('DistributedToonAI')
    
    LMHead = 0
    LMCage = 1
    LMOff = 2
    
    AvatarType = AVATAR_TOON
    Relationships = {
        AVATAR_TOON     :   RELATIONSHIP_FRIEND,
        AVATAR_SUIT     :   RELATIONSHIP_HATE,
        AVATAR_CCHAR    :   RELATIONSHIP_FRIEND
    }
    
    ClosedDuration = 0.15
    MaxPupilLook = 0.7 # dot
    EyeLookType_Auto = 0
    EyeLookType_Manual = 1

    def __init__(self, air):
        try:
            self.DistributedToonAI_initialized
            return
        except:
            self.DistributedToonAI_initialized = 1
        DistributedAvatarAI.__init__(self, air)
        ToonDNA.ToonDNA.__init__(self)
        self.avatarType = CIGlobals.Toon
        self.anim = "Happy"
        
        self.lookMode = 2 # LMOff
        
        # Eyes stuff
        self.eyeLensNP = None
        self.eyeTarget = None
        self.targetIsNew = True
        self.lastEyeTarget = None
        self.eyeTargetLastPos = Point3(0)
        self.eyeTargetBoredTime = 0.0
        self.eyeTargetLastMove = 0
        self.eyeTargetTime = 0
        self.eyeStateTime = 0
        self.eyeState = ToonGlobals.EyeStateOpened
        self.eyesOpenDuration = 5
        self.eyeLookType = self.EyeLookType_Auto

        self.activities = {ACT_DIE: 7.0, ACT_VICTORY_DANCE: 5.125,
                           ACT_TOON_BOW: 4.0, ACT_JUMP: 2.5,
                           ACT_TOON_POINT: 10.0, ACT_TOON_PRESENT: 10.0,
                           ACT_PRESS_BUTTON: 10.0, ACT_TOON_FALL: 2.5}

        return
        
    def onActivityFinish(self):
        self.b_setAnimState("Happy")
        
    def b_setAnimState(self, anim):
        self.sendUpdate('setAnimState', [anim, globalClockDelta.getFrameNetworkTime()])
        self.anim = anim
        
    def b_setLookMode(self, mode):
        self.setLookMode(mode)
        self.sendUpdate('setLookMode', [mode])
        
    def setDNAStrand(self, strand):
        ToonDNA.ToonDNA.setDNAStrand(self, strand)
        
        animal = self.getAnimal()
        bodyScale = ToonGlobals.BodyScales[animal]
        headScale = ToonGlobals.HeadScales[animal][2]
        shoulderHeight = ToonGlobals.LegHeightDict[self.getLegs()] * bodyScale + ToonGlobals.TorsoHeightDict[self.getTorso()] * bodyScale
        
        self.setHitboxData(0, 1, shoulderHeight + ToonGlobals.HeadHeightDict[self.getHead()] * headScale)
        
        if self.arePhysicsSetup():
            self.setupPhysics()
            
        if self.eyeLensNP:
            self.eyeLensNP.setZ(self.getHeight() * 0.85)

    def b_setDNAStrand(self, strand):
        self.d_setDNAStrand(strand)
        self.setDNAStrand(strand)
        
    def d_setDNAStrand(self, strand):
        self.sendUpdate('setDNAStrand', [strand])

    def setLookMode(self, mode):
        self.lookMode = mode

    def getLookMode(self):
        return self.lookMode

    def setAnimState(self, anim, timestamp = 0):
        self.anim = anim

    def getAnimState(self):
        return [self.anim, 0.0]

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        
        if not self.eyeLensNP:
            lens = PerspectiveLens()
            lens.setMinFov(180.0 / (4./3.))
            node = LensNode('toonEyes', lens)
            node.activateLens(0)
            self.eyeLensNP = self.attachNewNode(node)
            self.eyeLensNP.setZ(self.getHeight() - 0.5)
            self.eyeLensNP.setY(-1)
            
        self.setEyesOpenDuration()
        
        taskMgr.add(self.__eyesLookTask, self.taskName("eyesLookTask"))

    def delete(self):
        taskMgr.remove(self.taskName("eyesLookTask"))
        if self.eyeLensNP:
            self.eyeLensNP.removeNode()
        self.eyeLensNP = None
        self.anim = None
        self.eyeLookType = None
        
        DistributedAvatarAI.delete(self)
        
    ##########################################################################################
    # Eyes look-around stuff
    
    def hasEyeTarget(self):
        if isinstance(self.eyeTarget, NodePath):
            return CIGlobals.isNodePathOk(self.eyeTarget)
            
        return self.eyeTarget is not None
        
    def getDotToPupilTarget(self, target = None):
        if not target:
            target = self.eyeTarget
            
        if isinstance(target, NodePath):
            toTarget = (target.getPos(render) - self.eyeLensNP.getPos(render)).normalized()
        else:
            return 1.0
        fwd = self.eyeLensNP.getQuat(render).getForward()
        
        return fwd.dot(toTarget)
        
    def setEyesOpenDuration(self):
        self.eyesOpenDuration = random.uniform(0.5, 7.0)
        
    def setEyeState(self, state):
        self.eyeState = state
        self.eyeStateTime = globalClock.getFrameTime()
        self.sendUpdate('setEyeState', [state])
        
    def getEyeState(self):
        return self.eyeState
        
    def openEyes(self):
        self.setEyeState(ToonGlobals.EyeStateOpened) # opened
        
    def blink(self):
        self.setEyeState(ToonGlobals.EyeStateClosed) # closed
        
    def d_lookPupilsMiddle(self):
        self.sendUpdate('lookPupilsMiddle')
        
    def clearEyeTarget(self):
        self.lastEyeTarget = self.eyeTarget
        self.eyeTarget = None
        self.eyeTargetTime = 0
        self.eyeTargetLastMove = 0
        self.eyeTargetLastPos = Point3(0)
        
    def setEyeLookType(self, elt):
        self.eyeLookType = elt
        
    def setEyeTarget(self, target):
        self.lastEyeTarget = self.eyeTarget
        self.targetIsNew = True
        self.eyeTarget = target
        self.eyeTargetTime = globalClock.getFrameTime()
        self.eyeTargetLastMove = self.eyeTargetTime
        if isinstance(target, NodePath):
            self.eyeTargetLastPos = target.getPos(render)
        else:
            self.eyeTargetLastPos = target
        # How long until we get bored of this eye target?
        self.eyeTargetBoredTime = random.uniform(6.0, 10.0)
        
        # Blink when we get a new eye target, so our eyes don't strangely teleport
        self.blink()
        if isinstance(target, DistributedNodeAI):
            self.sendUpdate('lookEyesAtObject', [target.doId])
        else:
            self.sendUpdate('lookEyesAt', [[target[0], target[1], target[2]]])
        
    def __eyesLookTask(self, task):
        
                  
        now = globalClock.getFrameTime()
        
        eyeStateElapsed = now - self.eyeStateTime
        # Should we blink?
        if self.eyeState == ToonGlobals.EyeStateClosed and eyeStateElapsed >= self.ClosedDuration:
            self.openEyes()
        elif self.eyeState == ToonGlobals.EyeStateOpened and eyeStateElapsed >= self.eyesOpenDuration:
            self.blink()
           
        if self.hasEyeTarget():
            if self.targetIsNew:
                self.d_lookPupilsMiddle()
                self.targetIsNew = False

            pDot = self.getDotToPupilTarget()
            # did our eye target move?
            if isinstance(self.eyeTarget, NodePath):
                targetIsPoint = False
                # actual objects are more interesting, look longer
                boredTime = self.eyeTargetBoredTime * 2
                currTargetPos = self.eyeTarget.getPos(self.eyeLensNP)
            else:
                targetIsPoint = True
                boredTime = self.eyeTargetBoredTime * 0.5
                currTargetPos = self.eyeTarget
            
            if pDot < self.MaxPupilLook or not self.eyeLensNP.node().isInView(currTargetPos):
                # Target no longer in line-of-sight
                if self.eyeLookType == self.EyeLookType_Auto:
                    self.clearEyeTarget()
                return task.cont
            
            if self.eyeLookType == self.EyeLookType_Auto:
                if not targetIsPoint:
                    if (currTargetPos - self.eyeTargetLastPos).lengthSquared() > 0.01:
                        self.eyeTargetLastMove = now
                    elif (now - self.eyeTargetLastMove) > boredTime * 0.5:
                        # We get bored twice as fast if our eye target is not moving
                        self.clearEyeTarget()
                        return task.cont
                    
                if (now - self.eyeTargetTime) > boredTime:
                    self.clearEyeTarget()
                    return task.cont

            self.eyeTargetLastPos = currTargetPos
        else:
            # find a new eye target
            target = None
            
            avOrPoint = random.randint(0, 1)
            if avOrPoint == 0:
                visible = []
                avs = list(self.air.avatars[CIGlobals.getZoneId(self)])
                for avatar in avs:
                    if avatar == self.lastEyeTarget or avatar == self:
                        continue
                    apos = avatar.getPos(self.eyeLensNP)
                    pDot = self.getDotToPupilTarget(avatar)
                    if pDot >= self.MaxPupilLook and self.eyeLensNP.node().isInView(apos):
                        visible.append(avatar)
                if len(visible):
                    target = random.choice(visible)
                
            if not target:
                target = random.choice([Vec3(0, 25, 0),
                                        Vec3(10, 25, 0),
                                        Vec3(10, 25, 10),
                                        Vec3(0, 25, 10),
                                        Vec3(0, 25, -10),
                                        Vec3(-10, 25, -10),
                                        Vec3(-10, 25, 10),
                                        Vec3(-10, 25, 0),
                                        Vec3(10, 25, -10)])
                                        
            self.setEyeTarget(target)
            
        return task.cont
