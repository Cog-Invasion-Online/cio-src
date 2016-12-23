class MarginVisible:
    def __init__(self):
        self.marginManager = None
        self.visible = False
        self.priority = 0
        self.lastCell = None
        self.cell = None

    def manage(self, marginManager):
        if self.marginManager is not None:
            self.unmanage(self.marginManager)
        self.marginManager = marginManager
        if self.visible:
            self.marginManager.addVisible(self)

    def unmanage(self, marginManager):
        if marginManager != self.marginManager:
            return
        if self.marginManager is None:
            return
        if self.visible:
            self.marginManager.removeVisible(self)
        self.marginManager = None

    def setVisible(self, visible):
        if visible == self.visible:
            return
        self.visible = visible
        if self.marginManager is not None:
            if self.visible:
                self.marginManager.addVisible(self)
            else:
                self.marginManager.removeVisible(self)

    def getVisible(self):
        return self.visible

    def setPriority(self, priority):
        self.priority = priority
        if (self.marginManager is not None) and self.visible:
            self.marginManager.reorganize()

    def getPriority(self):
        return self.priority

    def setLastCell(self, cell):
        self.lastCell = cell

    def getLastCell(self):
        return self.lastCell

    def setCell(self, cell):
        self.cell = cell

    def getCell(self):
        return self.cell

    def marginVisibilityChanged(self):
        pass  # Inheritors should override this method.
