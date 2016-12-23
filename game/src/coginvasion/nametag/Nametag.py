from direct.task.Task import Task
from pandac.PandaModules import TextNode, VBase4

from src.coginvasion.toon.ChatBalloon import ChatBalloon
import NametagGlobals


class Nametag:
    TEXT_WORD_WRAP = 8
    TEXT_Y_OFFSET = -0.05

    CHAT_TEXT_WORD_WRAP = 12

    PANEL_X_PADDING = 0.2
    PANEL_Z_PADDING = 0.2

    CHAT_BALLOON_ALPHA = 1

    def __init__(self):
        self.avatar = None

        self.panel = None
        self.icon = None
        self.chatBalloon = None

        self.chatButton = NametagGlobals.noButton
        self.chatReversed = False

        self.font = None
        self.chatFont = None

        self.chatType = NametagGlobals.CHAT
        self.chatBalloonType = NametagGlobals.CHAT_BALLOON

        self.nametagColor = NametagGlobals.NametagColors[NametagGlobals.CCOtherPlayer]
        self.chatColor = NametagGlobals.ChatColors[NametagGlobals.CCOtherPlayer]
        self.speedChatColor = self.chatColor[0][1]

        self.nametagHidden = False
        self.chatHidden = False
        self.thoughtHidden = False

        # Create our TextNodes:
        self.textNode = TextNode('text')
        self.textNode.setWordwrap(self.TEXT_WORD_WRAP)
        self.textNode.setAlign(TextNode.ACenter)

        self.chatTextNode = TextNode('chatText')
        self.chatTextNode.setWordwrap(self.CHAT_TEXT_WORD_WRAP)
        self.chatTextNode.setGlyphScale(ChatBalloon.TEXT_GLYPH_SCALE)
        self.chatTextNode.setGlyphShift(ChatBalloon.TEXT_GLYPH_SHIFT)

        # Add the tick task:
        self.tickTaskName = self.getUniqueName() + '-tick'
        self.tickTask = taskMgr.add(self.tick, self.tickTaskName, sort=45)

    def destroy(self):
        if self.tickTask is not None:
            taskMgr.remove(self.tickTask)
            self.tickTask = None

        self.chatTextNode = None
        self.textNode = None

        self.chatFont = None
        self.font = None

        self.chatButton = NametagGlobals.noButton

        if self.chatBalloon is not None:
            self.chatBalloon.removeNode()
            self.chatBalloon = None

        if self.icon is not None:
            self.icon.removeAllChildren()
            self.icon = None

        if self.panel is not None:
            self.panel.removeNode()
            self.panel = None

        self.avatar = None

    def getUniqueName(self):
        return 'Nametag-' + str(id(self))

    def getChatBalloonModel(self):
        pass  # Inheritors should override this method.

    def getChatBalloonWidth(self):
        pass  # Inheritors should override this method.

    def getChatBalloonHeight(self):
        pass  # Inheritors should override this method.

    def tick(self, task):
        return Task.done  # Inheritors should override this method.

    def updateClickRegion(self):
        pass  # Inheritors should override this method.

    def drawChatBalloon(self, model, modelWidth, modelHeight):
        pass  # Inheritors should override this method.

    def drawNametag(self):
        pass  # Inheritors should override this method.

    def setAvatar(self, avatar):
        self.avatar = avatar

    def getAvatar(self):
        return self.avatar

    def setIcon(self, icon):
        self.icon = icon

    def getIcon(self):
        return self.icon

    def setChatButton(self, chatButton):
        self.chatButton = chatButton

    def getChatButton(self):
        return self.chatButton

    def hasChatButton(self):
        if (self.chatBalloonType == NametagGlobals.CHAT_BALLOON) and self.chatHidden:
            return False
        if (self.chatBalloonType == NametagGlobals.THOUGHT_BALLOON) and self.thoughtHidden:
            return False
        return self.chatButton != NametagGlobals.noButton

    def setChatReversed(self, chatReversed):
        self.chatReversed = chatReversed

    def getChatReversed(self):
        return self.chatReversed

    def setFont(self, font):
        self.font = font
        if self.font is not None:
            self.textNode.setFont(self.font)
        self.update()

    def getFont(self):
        return self.font

    def setChatFont(self, chatFont):
        self.chatFont = chatFont
        if self.chatFont is not None:
            self.chatTextNode.setFont(self.chatFont)
        self.update()

    def getChatFont(self):
        return self.chatFont

    def setChatType(self, chatType):
        self.chatType = chatType

    def getChatType(self):
        return self.chatType

    def setChatBalloonType(self, chatBalloonType):
        self.chatBalloonType = chatBalloonType

    def getChatBalloonType(self):
        return self.chatBalloonType

    def setNametagColor(self, nametagColor):
        self.nametagColor = nametagColor

    def getNametagColor(self):
        return self.nametagColor

    def setChatColor(self, chatColor):
        self.chatColor = chatColor

    def getChatColor(self):
        return self.chatColor

    def setSpeedChatColor(self, speedChatColor):
        self.speedChatColor = speedChatColor

    def getSpeedChatColor(self):
        return self.speedChatColor

    def hideNametag(self):
        self.nametagHidden = True

    def showNametag(self):
        self.nametagHidden = False

    def hideChat(self):
        self.chatHidden = True

    def showChat(self):
        self.chatHidden = False

    def hideThought(self):
        self.thoughtHidden = True

    def showThought(self):
        self.thoughtHidden = False

    def applyClickState(self, clickState):
        if self.chatBalloon is not None:
            foreground, background = self.chatColor[clickState]
            if self.chatType == NametagGlobals.SPEEDCHAT:
                background = self.speedChatColor
            if background[3] > self.CHAT_BALLOON_ALPHA:
                background = VBase4(
                    background[0], background[1], background[2],
                    self.CHAT_BALLOON_ALPHA)
            self.chatBalloon.setForeground(foreground)
            self.chatBalloon.setBackground(background)
            self.chatBalloon.setButton(self.chatButton[clickState])
        elif self.panel is not None:
            foreground, background = self.nametagColor[clickState]
            self.setForeground(foreground)
            self.setBackground(background)

    def setText(self, text):
        self.textNode.setText(text)

    def getText(self):
        return self.textNode.getText()

    def setChatText(self, chatText):
        self.chatTextNode.setText(chatText)

    def getChatText(self):
        return self.chatTextNode.getText()

    def setWordWrap(self, wordWrap):
        if wordWrap is None:
            wordWrap = self.TEXT_WORD_WRAP
        self.textNode.setWordwrap(wordWrap)
        self.update()

    def getWordWrap(self):
        return self.textNode.getWordwrap()

    def setChatWordWrap(self, chatWordWrap):
        if (chatWordWrap is None) or (chatWordWrap > self.CHAT_TEXT_WORD_WRAP):
            chatWordWrap = self.CHAT_TEXT_WORD_WRAP
        self.chatTextNode.setWordwrap(chatWordWrap)
        self.update()

    def getChatWordWrap(self):
        return self.chatTextNode.getWordwrap()

    def setForeground(self, foreground):
        self.textNode.setTextColor(foreground)

    def setBackground(self, background):
        if self.panel is not None:
            self.panel.setColor(background)

    def setShadow(self, shadow):
        self.textNode.setShadow(shadow)

    def getShadow(self):
        return self.textNode.getShadow()

    def clearShadow(self):
        self.textNode.clearShadow()

    def update(self):
        if self.chatBalloon is not None:
            self.chatBalloon.removeNode()
            self.chatBalloon = None

        if self.panel is not None:
            self.panel.removeNode()
            self.panel = None

        if self.getChatText():
            if self.chatBalloonType == NametagGlobals.CHAT_BALLOON:
                if not self.chatHidden:
                    model = self.getChatBalloonModel()
                    modelWidth = self.getChatBalloonWidth()
                    modelHeight = self.getChatBalloonHeight()
                    self.drawChatBalloon(model, modelWidth, modelHeight)
                    return
            elif self.chatBalloonType == NametagGlobals.THOUGHT_BALLOON:
                if not self.thoughtHidden:
                    model = NametagGlobals.thoughtBalloonModel
                    modelWidth = NametagGlobals.thoughtBalloonWidth
                    modelHeight = NametagGlobals.thoughtBalloonHeight
                    self.drawChatBalloon(model, modelWidth, modelHeight)
                    return

        if self.getText() and (not self.nametagHidden):
            self.drawNametag()
