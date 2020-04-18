"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedAvatar.py
@author Brian Lach
@date November 02, 2014

"""

from panda3d.core import TextNode

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.szboss.DistributedEntity import DistributedEntity
from src.coginvasion.avatar.Avatar import Avatar
from src.coginvasion.avatar.AvatarShared import AvatarShared
from src.coginvasion.globals import CIGlobals

from direct.distributed.DistributedSmoothNode import Lag

class DistributedAvatar(DistributedEntity, Avatar):
    notify = directNotify.newCategory("DistributedAvatar")

    EXTRAS = ["IMMUNITY LOSS!", "COMBO BONUS!", "WEAKNESS BONUS!", "MISSED!"]

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr, False)
        Avatar.__init__(self)
        
        # joint name -> [X,Y,Z,H,P,R,TIME]
        self.attachmentInterps = {}
        
    def handleDamage(self, x, y, z):
        pass
        
    def updateAttachment(self, jointName, x, y, z, h, p, r, serverTime):
        #print("Update attachment")
        if jointName in self.attachmentInterps:
            last = self.attachmentInterps[jointName]
        else:
            last = None
        
        now = globalClockDelta.getFrameNetworkTime()
        renderTime = now - Lag
        if last:
            t1 = last[6]
        else:
            t1 = 0.0
        t2 = serverTime
        
        #print(t2, renderTime, t1)
        
        attachment = self.find("**/" + jointName)
        if not attachment.isEmpty():
            if renderTime <= t2 and renderTime >= t1 and last:
                
                total = t2 - t1
                portion = renderTime - t1
                ratio = portion / total
                #print("lerp", t1, t2, renderTime, ratio)
                interpX = CIGlobals.lerp2(last[0], x, ratio)
                interpY = CIGlobals.lerp2(last[1], y, ratio)
                interpZ = CIGlobals.lerp2(last[2], z, ratio)
                interpH = CIGlobals.lerp2(last[3], h, ratio)
                interpP = CIGlobals.lerp2(last[4], p, ratio)
                interpR = CIGlobals.lerp2(last[5], r, ratio)
                attachment.setPosHpr(interpX, interpY, interpZ,
                                     interpH, interpP, interpR)
            else:
                #print("no lerp")
                attachment.setPosHpr(x, y, z, h, p, r)
        
        self.attachmentInterps[jointName] = [x, y, z, h, p, r, serverTime]

    def doSmoothTask(self, task):
        self.smoothPosition()

        if not hasattr(base, 'localAvatar') or self.doId != base.localAvatar.doId:
            self.setSpeed(self.smoother.getSmoothForwardVelocity(),
                          self.smoother.getSmoothRotationalVelocity(),
                          self.smoother.getSmoothLateralVelocity())
        return task.cont

    def b_setMoveBits(self, bits):
        self.sendUpdate('setMoveBits', [bits])
        self.moveBits = bits

    def b_splash(self, x, y, z):
        self.sendUpdate('splash', [x, y, z])
        self.splash(x, y, z)

    def setName(self, name):
        Avatar.setName(self, name)
        
    def getName(self):
        return Avatar.getName(self)

    def setChat(self, chat):
        Avatar.setChat(self, chat)

    def b_setChat(self, chat):
        self.d_setChat(chat)
        self.setChat(chat)

    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        AvatarShared.announceGenerate(self)
        self.setPythonTag('avatar', self.doId)
        self.setParent(CIGlobals.SPHidden)
        self.loadAvatar()

    def generate(self):
        DistributedEntity.generate(self)

    def disable(self):
        self.attachmentInterps = None
        DistributedEntity.disable(self)
        Avatar.disable(self)
        self.detachNode()
        return

    def delete(self):
        DistributedEntity.delete(self)
        Avatar.delete(self)
