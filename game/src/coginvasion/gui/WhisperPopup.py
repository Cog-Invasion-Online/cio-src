from pandac.PandaModules import TextNode, PGButton, Point3

from src.coginvasion.globals import ChatGlobals
from src.coginvasion.toon.ChatBalloon import ChatBalloon
from src.coginvasion.margins import MarginGlobals
from src.coginvasion.margins.MarginVisible import MarginVisible
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.gui.Clickable2d import Clickable2d


class WhisperQuitButton(Clickable2d):
    CONTENTS_SCALE = 12

    def __init__(self, whisperPopup):
        Clickable2d.__init__(self, 'WhisperQuitButton')

        self.whisperPopup = whisperPopup

        self.contents.setScale(self.CONTENTS_SCALE)
        self.contents.hide()

        self.nodePath = None

        self.update()

    def destroy(self):
        self.ignoreAll()

        if self.nodePath is not None:
            self.nodePath.removeNode()
            self.nodePath = None

        Clickable2d.destroy(self)

    def getUniqueName(self):
        return 'WhisperQuitButton-' + str(id(self))

    def update(self):
        if self.nodePath is not None:
            self.nodePath.removeNode()
            self.nodePath = None

        self.contents.node().removeAllChildren()

        quitButtonNode = NametagGlobals.quitButton[self.clickState]
        self.nodePath = quitButtonNode.copyTo(self.contents)

    def applyClickState(self, clickState):
        if self.nodePath is not None:
            self.nodePath.removeNode()
            self.nodePath = None

        quitButtonNode = NametagGlobals.quitButton[clickState]
        self.nodePath = quitButtonNode.copyTo(self.contents)

    def setClickState(self, clickState):
        self.applyClickState(clickState)

        if self.isHovering() or self.whisperPopup.isHovering():
            self.contents.show()
        elif self.clickState == PGButton.SDepressed:
            self.contents.show()
        else:
            self.contents.hide()

        Clickable2d.setClickState(self, clickState)

    def enterDepressed(self):
        base.playSfx(NametagGlobals.clickSound)

    def enterRollover(self):
        if self.lastClickState != PGButton.SDepressed:
            base.playSfx(NametagGlobals.rolloverSound)

    def updateClickRegion(self):
        if self.nodePath is not None:
            right = NametagGlobals.quitButtonWidth / 2.0
            left = -right
            top = NametagGlobals.quitButtonHeight / 2.0
            bottom = -top

            self.setClickRegionFrame(left, right, bottom, top)


class WhisperPopup(Clickable2d, MarginVisible):
    CONTENTS_SCALE = 0.25

    TEXT_MAX_ROWS = 6
    TEXT_WORD_WRAP = 8

    QUIT_BUTTON_SHIFT = (0.42, 0, 0.42)

    WHISPER_TIMEOUT_MIN = 10
    WHISPER_TIMEOUT_MAX = 20

    def __init__(self, text, font, whisperType, timeout=None):
        Clickable2d.__init__(self, 'WhisperPopup')
        MarginVisible.__init__(self)

        self.text = text
        self.font = font
        self.whisperType = whisperType
        if timeout is None:
            self.timeout = len(text) * 0.33
            if self.timeout < self.WHISPER_TIMEOUT_MIN:
                self.timeout = self.WHISPER_TIMEOUT_MIN
            elif self.timeout > self.WHISPER_TIMEOUT_MAX:
                self.timeout = self.WHISPER_TIMEOUT_MAX
        else:
            self.timeout = timeout

        self.active = False

        self.senderName = ''
        self.fromId = 0
        self.isPlayer = 0

        self.contents.setScale(self.CONTENTS_SCALE)

        self.whisperColor = ChatGlobals.WhisperColors[self.whisperType]

        self.textNode = TextNode('text')
        self.textNode.setWordwrap(self.TEXT_WORD_WRAP)
        self.textNode.setTextColor(self.whisperColor[PGButton.SInactive][0])
        self.textNode.setFont(self.font)
        self.textNode.setText(self.text)

        self.chatBalloon = None
        self.quitButton = None

        self.timeoutTaskName = self.getUniqueName() + '-timeout'
        self.timeoutTask = None

        self.quitEvent = self.getUniqueName() + '-quit'
        self.accept(self.quitEvent, self.destroy)

        self.setPriority(MarginGlobals.MP_high)
        self.setVisible(True)

        self.update()

        self.accept('MarginVisible-update', self.update)

    def destroy(self):
        self.ignoreAll()

        if self.timeoutTask is not None:
            taskMgr.remove(self.timeoutTask)
            self.timeoutTask = None

        if self.chatBalloon is not None:
            self.chatBalloon.removeNode()
            self.chatBalloon = None

        if self.quitButton is not None:
            self.quitButton.destroy()
            self.quitButton = None

        self.textNode = None

        Clickable2d.destroy(self)

    def getUniqueName(self):
        return 'WhisperPopup-' + str(id(self))

    def update(self):
        if self.chatBalloon is not None:
            self.chatBalloon.removeNode()
            self.chatBalloon = None

        if self.quitButton is not None:
            self.quitButton.destroy()
            self.quitButton = None

        self.contents.node().removeAllChildren()

        self.draw()

        if self.cell is not None:
            # We're in the margin display. Reposition our content, and update
            # the click region:
            self.reposition()
            self.updateClickRegion()
        else:
            # We aren't in the margin display. Disable the click region if one
            # is present:
            if self.region is not None:
                self.region.setActive(False)

    def draw(self):
        if self.isClickable():
            foreground, background = self.whisperColor[self.clickState]
        else:
            foreground, background = self.whisperColor[PGButton.SInactive]
        self.chatBalloon = ChatBalloon(
            NametagGlobals.chatBalloon2dModel,
            NametagGlobals.chatBalloon2dWidth,
            NametagGlobals.chatBalloon2dHeight, self.textNode,
            foreground=foreground, background=background,
            is2d=True
        )
        self.chatBalloon.reparentTo(self.contents)

        # Calculate the center of the TextNode:
        left, right, bottom, top = self.textNode.getFrameActual()
        center = self.contents.getRelativePoint(
            self.chatBalloon.textNodePath,
            ((left+right) / 2.0, 0, (bottom+top) / 2.0))

        # Translate the chat balloon along the inverse:
        self.chatBalloon.setPos(self.chatBalloon, -center)

        # Draw the quit button:
        #self.quitButton = WhisperQuitButton(self)
        #quitButtonNodePath = self.contents.attachNewNode(self.quitButton)

        # Move the quit button to the top right of the TextNode:
        #quitButtonNodePath.setPos(self.contents.getRelativePoint(
        #    self.chatBalloon.textNodePath, (right, 0, top)))

        # Apply the quit button shift:
        #quitButtonNodePath.setPos(quitButtonNodePath, self.QUIT_BUTTON_SHIFT)

        # Allow the quit button to close this whisper:
        #self.quitButton.setClickEvent(self.quitEvent)

    def manage(self, marginManager):
        MarginVisible.manage(self, marginManager)

        base.playSfx(base.cr.whisperNoise)

        self.timeoutTask = taskMgr.doMethodLater(
            self.timeout, self.unmanage, self.timeoutTaskName, [marginManager])

    def unmanage(self, marginManager):
        MarginVisible.unmanage(self, marginManager)

        self.destroy()

    def setClickable(self, senderName, fromId, isPlayer=0):
        self.senderName = senderName
        self.fromId = fromId
        self.isPlayer = isPlayer
        self.setClickEvent('clickedWhisper', extraArgs=[senderName, fromId, isPlayer])
        self.setActive(True)

    def applyClickState(self, clickState):
        if self.chatBalloon is not None:
            foreground, background = self.whisperColor[clickState]
            self.chatBalloon.setForeground(foreground)
            self.chatBalloon.setBackground(background)

    def setClickState(self, clickState):
        if self.isClickable():
            self.applyClickState(clickState)
        else:
            self.applyClickState(PGButton.SInactive)

        #if self.isHovering() or self.quitButton.isHovering():
        #    self.quitButton.contents.show()
        #elif self.quitButton.getClickState() == PGButton.SDepressed:
        #    self.quitButton.contents.show()
        #else:
        #    self.quitButton.contents.hide()

        Clickable2d.setClickState(self, clickState)

    def enterDepressed(self):
        if self.isClickable():
            base.playSfx(NametagGlobals.clickSound)

    def enterRollover(self):
        if self.isClickable() and (self.lastClickState != PGButton.SDepressed):
            base.playSfx(NametagGlobals.rolloverSound)

    def updateClickRegion(self):
        if self.chatBalloon is not None:
            right = self.chatBalloon.width / 2.0
            left = -right
            top = self.chatBalloon.height / 2.0
            bottom = -top

            self.setClickRegionFrame(left, right, bottom, top)
            self.region.setActive(True)
        else:
            if self.region is not None:
                self.region.setActive(False)

        if self.quitButton is not None:
            self.quitButton.updateClickRegion()

    def marginVisibilityChanged(self):
        if self.cell is not None:
            # We're in the margin display. Reposition our content, and update
            # the click region:
            self.reposition()
            self.updateClickRegion()
        else:
            # We aren't in the margin display. Disable the click region if one
            # is present:
            if self.region is not None:
                self.region.setActive(False)

    def reposition(self):
        if self.contents is None:
            return

        origin = Point3()

        self.contents.setPos(origin)

        if self.chatBalloon is not None:
            self.chatBalloon.removeNode()
            self.chatBalloon = None

        if self.quitButton is not None:
            self.quitButton.destroy()
            self.quitButton = None

        self.contents.node().removeAllChildren()

        if (self.cell in base.leftCells) or (self.cell in base.rightCells):
            text = self.text.replace('\x01WLDisplay\x01', '').replace('\x02', '')
            textWidth = self.textNode.calcWidth(text)
            if (textWidth / self.TEXT_WORD_WRAP) > self.TEXT_MAX_ROWS:
                self.textNode.setWordwrap(textWidth / (self.TEXT_MAX_ROWS-0.5))
        else:
            self.textNode.setWordwrap(self.TEXT_WORD_WRAP)

        self.draw()

        left, right, bottom, top = self.textNode.getFrameActual()
        if self.cell in base.bottomCells:
            # Move the origin to the bottom center of the chat balloon:
            origin = self.contents.getRelativePoint(
                self.chatBalloon.textNodePath, ((left+right) / 2.0, 0, bottom))
        elif self.cell in base.leftCells:
            # Move the origin to the left center of the chat balloon:
            origin = self.contents.getRelativePoint(
                self.chatBalloon.textNodePath, (left, 0, (bottom+top) / 2.0))
        elif self.cell in base.rightCells:
            # Move the origin to the right center of the chat balloon:
            origin = self.contents.getRelativePoint(
                self.chatBalloon.textNodePath, (right, 0, (bottom+top) / 2.0))

        self.contents.setPos(self.contents, -origin)
