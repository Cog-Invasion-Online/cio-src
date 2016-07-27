# Filename: DistributedTailorNPCToon.py
# Created by:  DecodedLogic (11Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify
import DistributedNPCToon

class DistributedTailorNPCToon(DistributedNPCToon.DistributedNPCToon):
    notify = directNotify.newCategory('DistributedTailorToon')

    def __init__(self, cr):
        DistributedNPCToon.DistributedNPCToon.__init__(self, cr)
        self.clothesGUI = None
        self.avatar = None
        self.oldStyle = None
        self.isBrowsing = 0
        self.button = None
        self.popupInfo = None

    def cleanup(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        if self.clothesGUI:
            self.clothesGUI.exit()
            self.clothesGUI.unload()
            self.clothesGUI = None
            if self.button:
                self.button.destroy()
                del self.button
            self.cancelButton.destroy()
            del self.cancelButton
            del self.gui
            self.counter.show()
            del self.counter
        if self.popupInfo:
            self.popupInfo.destroy()
            self.popupInfo = None

    def disable(self):
        self.cleanup()
        self.avatar = None
        self.oldStyle = None
        DistributedNPCToon.DistributedNPCToon.disable(self)

    def resetTailor(self):
        self.show()
        self.cleanup()
        self.startLookAround()
        self.detachAvatars()
        self.clearMat()
        if self.isLocal():
            self.freeAvatar()

    def isLocal(self):
        return self.avatar == base.localAvatar
