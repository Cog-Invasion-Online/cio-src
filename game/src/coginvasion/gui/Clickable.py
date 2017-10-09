from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from panda3d.core import PandaNode, PGButton, NodePath, MouseWatcherRegion


class Clickable(FSM, PandaNode, DirectObject):
    def __init__(self, name):
        FSM.__init__(self, name)
        PandaNode.__init__(self, name)
        DirectObject.__init__(self)

        self.active = True

        self.lastClickState = PGButton.SReady
        self.clickState = PGButton.SReady

        self.__hovering = False

        self.clickEvent = ''
        self.clickExtraArgs = []

        self.contents = NodePath.anyPath(self).attachNewNode('contents')

        # Create a MouseWatcherRegion:
        self.regionName = self.getUniqueName() + '-region'
        self.region = MouseWatcherRegion(self.regionName, 0, 0, 0, 0)
        base.mouseWatcherNode.addRegion(self.region)

        # Accept the mouse events:
        enterPattern = base.mouseWatcherNode.getEnterPattern()
        leavePattern = base.mouseWatcherNode.getLeavePattern()
        buttonDownPattern = base.mouseWatcherNode.getButtonDownPattern()
        buttonUpPattern = base.mouseWatcherNode.getButtonUpPattern()
        self.accept(enterPattern.replace('%r', self.regionName), self.__handleMouseEnter)
        self.accept(leavePattern.replace('%r', self.regionName), self.__handleMouseLeave)
        self.accept(buttonDownPattern.replace('%r', self.regionName), self.__handleMouseDown)
        self.accept(buttonUpPattern.replace('%r', self.regionName), self.__handleMouseUp)

    def destroy(self):
        self.ignoreAll()

        if self.region is not None:
            base.mouseWatcherNode.removeRegion(self.region)
            self.region = None

        if self.contents is not None:
            self.contents.removeNode()
            self.contents = None

    def getUniqueName(self):
        return 'Clickable-' + str(id(self))

    def setActive(self, active):
        self.active = active

    def getActive(self):
        return self.active

    def isClickable(self):
        return self.active

    def isHovering(self):
        return self.__hovering

    def setClickState(self, clickState):
        self.lastClickState = self.clickState
        self.clickState = clickState

        if self.clickState == PGButton.SReady:
            self.request('Ready')
        elif self.clickState == PGButton.SDepressed:
            self.request('Depressed')
        elif self.clickState == PGButton.SRollover:
            self.request('Rollover')
        elif self.clickState == PGButton.SInactive:
            self.request('Inactive')

    def getClickState(self):
        return self.clickState

    def enterReady(self):
        pass

    def enterDepressed(self):
        pass

    def exitDepressed(self):
        if self.isClickable():
            messenger.send(self.clickEvent, self.clickExtraArgs)

    def enterRollover(self):
        pass

    def enterInactive(self):
        pass

    def setClickEvent(self, event, extraArgs=[]):
        self.clickEvent = event
        self.clickExtraArgs = extraArgs

    def setClickRegionFrame(self, left, right, bottom, top):
        self.region.setFrame(left, right, bottom, top)

    def __handleMouseEnter(self, region, button):
        self.__hovering = True
        self.setClickState(PGButton.SRollover)

    def __handleMouseLeave(self, region, button):
        self.__hovering = False
        if self.clickState != PGButton.SDepressed:
            self.setClickState(PGButton.SReady)

    def __handleMouseDown(self, region, button):
        self.setClickState(PGButton.SDepressed)

    def __handleMouseUp(self, region, button):
        if self.__hovering:
            self.setClickState(PGButton.SRollover)
        else:
            self.setClickState(PGButton.SReady)
