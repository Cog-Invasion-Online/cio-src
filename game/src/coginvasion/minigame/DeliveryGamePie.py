"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DeliveryGamePie.py
@author Brian Lach
@date July 7, 2017

"""

from pandac.PandaModules import NodePath, VBase4

from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import ProjectileInterval
from direct.actor.Actor import Actor

from src.coginvasion.gags.WholeCreamPie import WholeCreamPie
from src.coginvasion.gags import GagGlobals

class DeliveryGamePie(DirectObject):

    def __init__(self, toon, mg):
        self.mg = mg
        self.toon = toon
        self.splat = Actor(GagGlobals.SPLAT_MDL, {'chan' : GagGlobals.SPLAT_CHAN})
        self.splat.setScale(0.5)
        self.splat.setColor(VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0))
        self.splat.setBillboardPointEye()
        self.gc = WholeCreamPie()
        self.gc.build()
        self.gag = self.gc.getGag()
        self.toon.play('toss', fromFrame = 60, toFrame = 85)
        self.gag.reparentTo(self.toon.find('**/def_joint_right_hold'))
        throwPath = NodePath('ThrowPath')
        throwPath.reparentTo(self.toon)
        throwPath.setScale(render, 1)
        throwPath.setPos(0, 150, -90)
        throwPath.setHpr(90, -90, 90)
        self.gag.wrtReparentTo(render)
        self.gag.setHpr(throwPath.getHpr(render))
        self.track = ProjectileInterval(self.gag, startPos = self.toon.find('**/def_joint_right_hold').getPos(render),
                                   endPos = throwPath.getPos(render), gravityMult = 0.9, duration = 3)
        self.track.start()
        taskMgr.doMethodLater(3, self.__handleThrowTrackDone, 'handleThrowTrackDoneDGP-' + str(hash(self)))

    def splat(self):
        self.mg.pies.remove(self)
        self.track.pause()
        self.splat.play('chan')
        self.splat.reparentTo(render)
        self.splat.setPos(self.gag.getPos(render))
        self.gag.reparentTo(hidden)
        taskMgr.doMethodLater(0.5, self.delSplat, 'Delete Splat' + str(hash(self)))

    def delSplat(self, task):
        self.splat.reparentTo(hidden)
        self.cleanup()

    def __handleThrowTrackDone(self, task):
        self.cleanup()
        return task.done

    def cleanup(self):
        if hasattr(self, 'cleanedUp'):
            return
        self.cleanedUp = 1

        del self.mg
        del self.toon
        self.gc.cleanupGag()
        del self.gc
        self.gag.removeNode()
        del self.gag
        del self.track
        self.splat.cleanup()
        del self.splat
        taskMgr.remove('handleThrowTrackDoneDGP-' + str(hash(self)))
        taskMgr.remove('Delete Splat' + str(hash(self)))

    def __handlePieCollision(self, entry):

        self.splat()
        self.mg.sendUpdate('pieSplat', [self.mg.pies.index(self)])

        intoNP = entry.getIntoNodePath()
        avNP = intoNP.getParent()
        fromNP = entry.getFromNodePath().getParent()

        if fromNP.isEmpty():
            return

        for key in base.cr.doId2do.keys():
            obj = base.cr.doId2do[key]
            if obj.__class__.__name__ == "DistributedDeliveryGameSuit":
                if obj.getKey() == avNP.getKey():
                    self.mg.sendUpdate('hitSuitWithPie', [obj.doId])
