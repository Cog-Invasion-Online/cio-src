from direct.task.Task import Task
from panda3d.core import VBase4, PandaNode

from lib.coginvasion.margins.MarginVisible import MarginVisible
import NametagGlobals
from Nametag2d import Nametag2d
from Nametag3d import Nametag3d


class NametagGroup:
    CHAT_TIMEOUT_MIN = 4.0
    CHAT_TIMEOUT_MAX = 12.0
    CHAT_STOMP_DELAY = 0.0

    def __init__(self):
        self.avatar = None
        self.active = True
        self.objectCode = None

        self.chatButton = NametagGlobals.noButton
        self.chatReversed = False

        self.font = None
        self.chatFont = None

        self.shadow = None

        self.marginManager = None
        self.visible3d = True

        self.chatType = NametagGlobals.CHAT
        self.chatBalloonType = NametagGlobals.CHAT_BALLOON

        self.nametagColor = NametagGlobals.NametagColors[NametagGlobals.CCOtherPlayer]
        self.chatColor = NametagGlobals.ChatColors[NametagGlobals.CCOtherPlayer]
        self.speedChatColor = VBase4(1, 1, 1, 1)

        self.wordWrap = 8
        self.chatWordWrap = 10

        self.text = ''

        self.chatPages = []
        self.chatPageIndex = 0
        self.chatTimeoutTask = None
        self.chatTimeoutTaskName = self.getUniqueName() + '-timeout'

        self.stompChatText = ''
        self.stompTask = None
        self.stompTaskName = self.getUniqueName() + '-stomp'

        self.icon = PandaNode('icon')

        self.nametag2d = Nametag2d()
        self.nametag3d = Nametag3d()

        self.nametags = set()
        self.add(self.nametag2d)
        self.add(self.nametag3d)

        # Add the tick task:
        self.tickTaskName = self.getUniqueName() + '-tick'
        self.tickTask = taskMgr.add(self.tick, self.tickTaskName, sort=45)

    def destroy(self):
        if self.marginManager is not None:
            self.unmanage(self.marginManager)

        if self.tickTask is not None:
            taskMgr.remove(self.tickTask)
            self.tickTask = None

        self.clearChatText()

        for nametag in list(self.nametags):
            self.remove(nametag)

        self.nametag2d = None
        self.nametag3d = None

        if self.icon is not None:
            self.icon.removeAllChildren()
            self.icon = None

        self.chatFont = None
        self.font = None

        self.chatButton = NametagGlobals.noButton

        self.avatar = None

    def getUniqueName(self):
        return 'NametagGroup-' + str(id(self))

    def tick(self, task):
        if (self.avatar is None) or (self.avatar.isEmpty()):
            return Task.cont

        chatText = self.getChatText()
        if (NametagGlobals.forceOnscreenChat and
            chatText and
            self.chatBalloonType == NametagGlobals.CHAT_BALLOON):
            visible3d = False
        elif self.avatar == NametagGlobals.me:
            if (chatText and
                self.chatBalloonType == NametagGlobals.CHAT_BALLOON and
                not base.cam.node().isInView(self.avatar.getPos(base.cam))):
                visible3d = False
            else:
                visible3d = True
        elif NametagGlobals.force2dNametags:
            visible3d = False
        elif (not NametagGlobals.want2dNametags and
              ((not chatText) or (self.chatBalloonType != NametagGlobals.CHAT_BALLOON))):
            visible3d = True
        elif self.avatar.isHidden():
            visible3d = False
        else:
            visible3d = base.cam.node().isInView(self.avatar.getPos(base.cam))

        if visible3d != self.visible3d:
            self.visible3d = visible3d
            if self.nametag2d is not None:
                self.nametag2d.setVisible(not visible3d)

        return Task.cont

    def setAvatar(self, avatar):
        self.avatar = avatar
        for nametag in self.nametags:
            nametag.setAvatar(self.avatar)

    def getAvatar(self):
        return self.avatar

    def setActive(self, active):
        self.active = active
        for nametag in self.nametags:
            nametag.setActive(self.active)

    def getActive(self):
        return self.active

    def setObjectCode(self, objectCode):
        self.objectCode = objectCode

    def getObjectCode(self):
        return self.objectCode

    def setChatButton(self, chatButton):
        self.chatButton = chatButton
        for nametag in self.nametags:
            nametag.setChatButton(self.chatButton)

    def getChatButton(self):
        return self.chatButton

    def hasChatButton(self):
        return self.chatButton != NametagGlobals.noButton

    def setChatReversed(self, reversed):
        self.chatReversed = reversed
        for nametag in self.nametags:
            nametag.setChatReversed(reversed)

    def getChatReversed(self):
        return self.chatReversed

    def setFont(self, font):
        self.font = font
        for nametag in self.nametags:
            nametag.setFont(self.font)

    def getFont(self):
        return self.font

    def setChatFont(self, chatFont):
        self.chatFont = chatFont
        for nametag in self.nametags:
            nametag.setChatFont(self.chatFont)

    def getChatFont(self):
        return self.chatFont

    def setShadow(self, shadow):
        self.shadow = shadow
        for nametag in self.nametags:
            nametag.setShadow(self.shadow)

    def getShadow(self):
        return self.shadow

    def clearShadow(self):
        self.shadow = None
        for nametag in self.nametags:
            nametag.clearShadow()

    def setChatType(self, chatType):
        self.chatType = chatType
        for nametag in self.nametags:
            nametag.setChatType(self.chatType)

    def getChatType(self):
        return self.chatType

    def setChatBalloonType(self, chatBalloonType):
        self.chatBalloonType = chatBalloonType
        for nametag in self.nametags:
            nametag.setChatBalloonType(self.chatBalloonType)

    def getChatBalloonType(self):
        return self.chatBalloonType

    def setNametagColor(self, nametagColor):
        self.nametagColor = nametagColor
        for nametag in self.nametags:
            nametag.setNametagColor(self.nametagColor)

    def getNametagColor(self):
        return self.nametagColor

    def setChatColor(self, chatColor):
        self.chatColor = chatColor
        for nametag in self.nametags:
            nametag.setChatColor(self.chatColor)

    def getChatColor(self):
        return self.chatColor

    def setSpeedChatColor(self, speedChatColor):
        self.speedChatColor = speedChatColor
        for nametag in self.nametags:
            nametag.setSpeedChatColor(self.speedChatColor)

    def getSpeedChatColor(self):
        return self.speedChatColor

    def setWordWrap(self, wordWrap):
        self.wordWrap = wordWrap
        for nametag in self.nametags:
            nametag.setWordWrap(self.wordWrap)

    def getWordWrap(self):
        return self.wordWrap

    def setChatWordWrap(self, chatWordWrap):
        self.chatWordWrap = chatWordWrap
        for nametag in self.nametags:
            nametag.setChatWordWrap(self.chatWordWrap)

    def getChatWordWrap(self):
        return self.chatWordWrap

    def setText(self, text):
        self.text = text
        for nametag in self.nametags:
            nametag.setText(self.text)
            nametag.update()

    def getText(self):
        return self.text

    def getNumChatPages(self):
        return len(self.chatPages)

    def setChatPageIndex(self, chatPageIndex):
        if chatPageIndex >= self.getNumChatPages():
            return

        self.chatPageIndex = chatPageIndex
        for nametag in self.nametags:
            nametag.setChatText(self.chatPages[self.chatPageIndex])
            nametag.update()

    def getChatPageIndex(self):
        return self.chatPageIndex

    def setChatText(self, chatText, timeout=False):
        # If we are currently displaying chat text, we need to "stomp" it. In
        # other words, we need to clear the current chat text, pause for a
        # brief moment, and then display the new chat text:
        if self.getChatText():
            self.clearChatText()
            self.stompChatText = chatText
            self.stompTask = taskMgr.doMethodLater(
                self.CHAT_STOMP_DELAY, self.__chatStomp, self.stompTaskName,
                extraArgs=[timeout])
            return

        self.clearChatText()

        self.chatPages = chatText.split('\x07')
        self.setChatPageIndex(0)

        if timeout:
            delay = len(self.getChatText()) * 0.5
            if delay < self.CHAT_TIMEOUT_MIN:
                delay = self.CHAT_TIMEOUT_MIN
            elif delay > self.CHAT_TIMEOUT_MAX:
                delay = self.CHAT_TIMEOUT_MAX
            self.chatTimeoutTask = taskMgr.doMethodLater(
                delay, self.clearChatText, self.chatTimeoutTaskName)

    def getChatText(self):
        if self.chatPageIndex >= self.getNumChatPages():
            return ''
        return self.chatPages[self.chatPageIndex]

    def clearChatText(self, task=None):
        if self.stompTask is not None:
            taskMgr.remove(self.stompTask)
            self.stompTask = None

        self.stompChatText = ''

        if self.chatTimeoutTask is not None:
            taskMgr.remove(self.chatTimeoutTask)
            self.chatTimeoutTask = None

        self.chatPages = []
        self.chatPageIndex = 0

        for nametag in self.nametags:
            nametag.setChatText('')
            nametag.update()

        if task is not None:
            return Task.done

    def getStompChatText(self):
        return self.stompChatText

    def setIcon(self, icon):
        self.icon = icon
        for nametag in self.nametags:
            nametag.setIcon(self.icon)

    def getIcon(self):
        return self.icon

    def setNametag2d(self, nametag2d):
        if self.nametag2d is not None:
            self.remove(self.nametag2d)
            self.nametag2d = None

        if nametag2d is None:
            return

        self.nametag2d = nametag2d
        self.add(self.nametag2d)

    def getNametag2d(self):
        return self.nametag2d

    def setNametag3d(self, nametag3d):
        if self.nametag3d is not None:
            self.remove(self.nametag3d)
            self.nametag3d = None

        if nametag3d is None:
            return

        self.nametag3d = nametag3d
        self.add(self.nametag3d)

    def getNametag3d(self):
        return self.nametag3d

    def add(self, nametag):
        self.nametags.add(nametag)
        nametag.setAvatar(self.avatar)
        nametag.setActive(self.active)
        nametag.setClickEvent(self.getUniqueName())
        nametag.setChatButton(self.chatButton)
        nametag.setFont(self.font)
        nametag.setChatFont(self.chatFont)
        nametag.setChatType(self.chatType)
        nametag.setChatBalloonType(self.chatBalloonType)
        nametag.setNametagColor(self.nametagColor)
        nametag.setChatColor(self.chatColor)
        nametag.setSpeedChatColor(self.speedChatColor)
        nametag.setWordWrap(self.wordWrap)
        nametag.setChatWordWrap(self.chatWordWrap)
        nametag.setText(self.text)
        nametag.setChatText(self.getChatText())
        nametag.setIcon(self.icon)
        nametag.update()
        # Add this nametag to the global nametag pool.
        NametagGlobals.appendNametag(nametag)

    def remove(self, nametag):
        nametag.destroy()
        self.nametags.remove(nametag)
        # Remove this nametag from the global nametag pool.
        NametagGlobals.removeNametag(nametag)

    def updateAll(self):
        for nametag in self.nametags:
            nametag.update()

    def manage(self, marginManager):
        if self.marginManager is not None:
            self.unmanage(self.marginManager)
        self.marginManager = marginManager
        for nametag in self.nametags:
            if isinstance(nametag, MarginVisible):
                nametag.manage(self.marginManager)

    def unmanage(self, marginManager):
        if marginManager != self.marginManager:
            return
        if self.marginManager is None:
            return
        self.marginManager = marginManager
        for nametag in self.nametags:
            if isinstance(nametag, MarginVisible):
                nametag.unmanage(self.marginManager)

    def hideNametag(self):
        for nametag in self.nametags:
            nametag.hideNametag()

    def showNametag(self):
        for nametag in self.nametags:
            nametag.showNametag()

    def hideChat(self):
        for nametag in self.nametags:
            nametag.hideChat()

    def showChat(self):
        for nametag in self.nametags:
            nametag.showChat()

    def hideThought(self):
        for nametag in self.nametags:
            nametag.hideThought()

    def showThought(self):
        for nametag in self.nametags:
            nametag.showThought()

    def __chatStomp(self, timeout=False):
        self.setChatText(self.stompChatText, timeout=timeout)
        self.stompChatText = ''
