from pandac.PandaModules import NodePath


class MarginCell(NodePath):
    def __init__(self):
        NodePath.__init__(self, 'cell')

        self.active = False
        self.content = None
        self.contentNodePath = None

    def setActive(self, active):
        if not active:
            self.setContent(None)

        self.active = active

    def getActive(self):
        return self.active

    def setContent(self, content):
        if self.content is not None:
            self.content.setCell(None)
            self.content.marginVisibilityChanged()
            self.content = None

        if self.contentNodePath is not None:
            self.contentNodePath.removeNode()
            self.contentNodePath = None

        if content is not None:
            content.setLastCell(self)
            content.setCell(self)
            self.contentNodePath = self.attachNewNode(content)
            content.marginVisibilityChanged()

        self.content = content

    def getContent(self):
        return self.content
