########################################
# Filename: DistributedAvatar.py
# Created by: blach (02Nov14)
########################################

from pandac.PandaModules import TextNode

from direct.actor.DistributedActor import DistributedActor
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectLabel
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait, Func

from src.coginvasion.avatar.Avatar import Avatar
from src.coginvasion.globals import CIGlobals

class DistributedAvatar(DistributedActor, Avatar):
    notify = directNotify.newCategory("DistributedAvatar")

    def __init__(self, cr):
        try:
            self.DistributedAvatar_initialized
            return
        except:
            self.DistributedAvatar_initialized = 1
        Avatar.__init__(self)
        DistributedActor.__init__(self, cr)
        self.health = 0
        self.maxHealth = 0
        self.healthLabel = None
        self.healthLabelTrack = None
        self.place = 0
        self.hood = None
        return

    def setHood(self, hood):
        self.hood = hood

    def getHood(self):
        return self.hood

    def setupHealthLabel(self):
        self.healthLabel = DirectLabel(text = "", text_fg = CIGlobals.PositiveTextColor,
                                    scale = 0.75, relief = None, text_decal = True,
                                    text_font = CIGlobals.getMickeyFont(), text_align = TextNode.ACenter)
        self.healthLabel.reparentTo(self)
        self.healthLabel.setBillboardPointEye()
        self.healthLabel.stash()

    def showAndMoveHealthLabel(self):
        self.unstashHpLabel()
        self.stopMovingHealthLabel()
        x = self.nametag3d.getX()
        y = self.nametag3d.getY()
        z = self.nametag3d.getZ()
        moveTrack = LerpPosInterval(self.healthLabel,
                                duration = 0.5,
                                pos = (x, y, z + 0.5),
                                startPos = (x, y, z - 2),
                                blendType = 'easeOut')
        self.healthLabelTrack = Sequence(moveTrack, Wait(1.0), Func(self.stashHpLabel))
        self.healthLabelTrack.start()

    def stopMovingHealthLabel(self):
        if self.healthLabelTrack != None:
            self.healthLabelTrack.pause()
            self.healthLabelTrack = None

    def stashHpLabel(self):
        self.healthLabel.stash()

    def unstashHpLabel(self):
        self.healthLabel.unstash()

    def announceHealth(self, level, hp):
        if level == 1:
            self.healthLabel["text_fg"] = CIGlobals.PositiveTextColor
            self.healthLabel['text'] = "+%s" % hp
        else:
            textFg = CIGlobals.NegativeTextColor
            if level == 2:
                textFg = CIGlobals.OrangeTextColor
            elif level == 3:
                textFg = CIGlobals.YellowTextColor
            self.healthLabel["text_fg"] = textFg
            self.healthLabel['text'] = "-%s" % hp
        self.showAndMoveHealthLabel()

    def setHealth(self, health):
        self.health = health

    def getHealth(self):
        return self.health

    def isDead(self):
        return self.health <= 0

    def setName(self, name):
        Avatar.setName(self, name)

    def setChat(self, chat):
        Avatar.setChat(self, chat)

    def d_setChat(self, chat):
        self.sendUpdate("setChat", [chat])

    def b_setChat(self, chat):
        self.d_setChat(chat)
        self.setChat(chat)

    def setMaxHealth(self, health):
        self.maxHealth = health

    def getMaxHealth(self):
        return self.maxHealth

    def setPlace(self, place):
        self.place = place

    def getPlace(self):
        return self.place

    def announceGenerate(self):
        DistributedActor.announceGenerate(self)
        self.setPythonTag('avatar', self.doId)
        self.setupHealthLabel()
        self.setParent(CIGlobals.SPHidden)
        self.setBlend(frameBlend = True)

    def generate(self):
        DistributedActor.generate(self)

    def disable(self):
        DistributedActor.disable(self)
        self.stopMovingHealthLabel()
        self.detachNode()
        return

    def delete(self):
        DistributedActor.delete(self)
        self.health = None
        self.maxHealth = None
        self.healthLabel = None
        self.healthLabelTrack = None
        self.hood = None
        self.place = None
