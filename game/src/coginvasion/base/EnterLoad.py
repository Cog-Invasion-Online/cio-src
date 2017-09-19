"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file EnterLoad.py
@author Brian Lach
@date April 18, 2015

"""

import FileUtility
from LoadUtility import LoadUtility

class EnterLoad(LoadUtility):

    def __init__(self, callback):
        LoadUtility.__init__(self, callback)
        phasesToScan = ["phase_3.5/models"]
        self.models = FileUtility.findAllModelFilesInVFS(phasesToScan)

    def load(self):
        loader.beginBulkLoad('localAvatarEnterGame', 'localAvatarEnterGame', len(self.models), 0, False)
        LoadUtility.load(self)

    def done(self):
        LoadUtility.done(self)
        loader.endBulkLoad('localAvatarEnterGame')
