"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIBase.py
@author Brian Lach
@date 2017-03-13

"""

from direct.showbase.ShowBase import ShowBase
from direct.directnotify.DirectNotifyGlobal import directNotify

class CIBase(ShowBase):
    notify = directNotify.newCategory("CIBase")

    def doOldToontownRatio(self):
        ShowBase.adjustWindowAspectRatio(self, 4. / 3.)

    def doRegularRatio(self):
        ShowBase.adjustWindowAspectRatio(self, self.getAspectRatio())

    def adjustWindowAspectRatio(self, aspectRatio):
        from src.coginvasion.globals import CIGlobals

        if (CIGlobals.getSettingsMgr() is None):
            return

        if (CIGlobals.getSettingsMgr().getSetting("maspr") is True):
            # Go ahead and maintain the aspect ratio if the user wants us to.
            ShowBase.adjustWindowAspectRatio(self, aspectRatio)
        else:
            # The user wants us to keep a 4:3 ratio no matter what (old toontown feels).
            self.doOldToontownRatio()
