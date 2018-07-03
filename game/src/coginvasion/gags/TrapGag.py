"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TrapGag.py
@author Maverick Liberty
@date July 08, 2015

"""

from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
import abc
import datetime

class TrapGag(Gag):

    def __init__(self, name, model, damage, hitSfx, anim = None, doesAutoRelease = True):
        Gag.__init__(self, name, model, GagType.TRAP, hitSfx, anim = anim)
        self.hitSfx = None
        self.entity = None
        self.timeout = 3.0
        if game.process == 'client':
            self.hitSfx = base.audio3d.loadSfx(hitSfx)

    def build(self):
        super(TrapGag, self).build()
        
        now = datetime.datetime.now()
        debrisName = 'TrapDebris-{0}'.format(now.strftime("%H:%M"))
        self.gag.setName(debrisName)
        
        return self.gag

    @abc.abstractmethod
    def buildCollisions(self):
        if not self.gag:
            return

    @abc.abstractmethod
    def activate(self):
        pass

    @abc.abstractmethod
    def onCollision(self, entry):
        pass

    @abc.abstractmethod
    def d_doCollision(self):
        pass

    def delete(self):
        super(TrapGag, self).delete()

    def unEquip(self):
        super(TrapGag, self).unEquip()
        if self.gag:
            self.cleanupGag()

    @abc.abstractmethod
    def startTrap(self):
        super(TrapGag, self).start()

    def throw(self):
        pass

    def release(self):
        super(TrapGag, self).release()
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])
        if not self.gag: return

    def getHandle(self):
        return self
    
    def getGag(self):
        if not self.gag:
            return self.entity
        return Gag.getGag(self)
