"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ToonTalker.py
@author Brian Lach
@date July ??, 2014

"""

from src.coginvasion.globals import CIGlobals
from panda3d.core import BillboardEffect, Vec3, Point3
from src.coginvasion.toon.LabelScaler import LabelScaler
from direct.directnotify.DirectNotify import DirectNotify
from src.coginvasion.toon.ChatBalloon import ChatBalloon
import random
import math

notify = DirectNotify().newCategory("ToonTalker")

class ToonTalker:
    THOUGHT_PREFIX = '.'
    LENGTH_FACTOR = 0.6
    MIN_LENGTH = 5
    MAX_LENGTH = 20

    def __init__(self):
        self.avatar = None
        self.nametag = None
        self.autoClearChat = True

    def setAutoClearChat(self, flag):
        self.autoClearChat = flag

    def setAvatar(self, avatar, nametag):
        self.avatar = avatar
        self.nametag = nametag

    def setChatAbsolute(self, chatString = None):
        if not chatString or chatString.isspace() or len(chatString) == 0:
            return

        self.clearChat()
        self.taskId = random.randint(0, 1000000000000000000000000000000)
        if self.nameTag:
            self.getNameTag().hide()

        if self.isThought(chatString):
            chatString = self.removeThoughtPrefix(chatString)
            bubble = loader.loadModel(CIGlobals.ThoughtBubble)
        else:
            length = math.sqrt(len(chatString)) / self.LENGTH_FACTOR
            if length < self.MIN_LENGTH:
                length = self.MIN_LENGTH
            if length > self.MAX_LENGTH:
                length = self.MAX_LENGTH
            bubble = loader.loadModel(CIGlobals.ChatBubble)
            if self.autoClearChat:
                taskMgr.doMethodLater(length, self.clearChatTask, "clearAvatarChat-%s" % (str(self.taskId)))

        if self.avatarType == CIGlobals.Suit:
            font = CIGlobals.getSuitFont()
        else:
            font = CIGlobals.getToonFont()

        self.chatBubble = ChatBalloon(bubble).generate(chatString, font)
        self.chatBubble.setEffect(BillboardEffect.make(Vec3(0,0,1), True, False, 3.0, camera, Point3(0,0,0)))
        if self.nameTag:
            self.chatBubble.setZ(self.getNameTag().getZ())
        else:
            if self.avatarType == CIGlobals.Suit:
                nametagZ = self.suitPlan.getNametagZ()
                self.chatBubble.setZ(nametagZ)

        if self.avatar and hasattr(self.avatar, 'getGhost'):
            if not self.avatar.getGhost() or self.avatar.doId == base.localAvatar.doId:
                self.chatBubble.reparentTo(self)
        else:
            self.chatBubble.reparentTo(self)

        LabelScaler().resize(self.chatBubble)

    def isThought(self, message):
        if message.isspace() or len(message) == 0:
            return False
        if message[0] == self.THOUGHT_PREFIX and not CIGlobals.isNPCToon(self):
            return True
        else:
            return False

    def removeThoughtPrefix(self, message):
        if self.isThought(message):
            return message[len(self.THOUGHT_PREFIX):]
        else:
            notify.warning("attempted to remove a thought prefix on a non-thought message")
            return message

    def clearChatTask(self, task):
        self.clearChat()
        return task.done

    def clearChat(self):
        try:
            self.chatBubble.removeNode()
            del self.chatBubble
        except:
            return
        if self.avatar and hasattr(self.avatar, 'getGhost'):
            if self.nameTag and not self.avatar.getGhost() or self.nameTag and self.avatar.doId == base.localAvatar.doId:
                self.getNameTag().show()
        else:
            if self.nameTag:
                self.getNameTag().show()
        taskMgr.remove("clearAvatarChat-" + str(self.taskId))
