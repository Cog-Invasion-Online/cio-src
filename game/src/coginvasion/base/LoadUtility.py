"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LoadUtility.py
@author Brian Lach
@date April 18, 2015

"""

from panda3d.core import ConfigVariableBool

class LoadUtility:

    def __init__(self, callback):
        self.callback = callback
        self.models = []

    def load(self):
        if ConfigVariableBool("load-stuff", True):
            for modelFile in self.models:
                loader.loadModel(modelFile)
                loader.progressScreen.tick()
        self.done()

    def done(self):
        self.callback()
        self.destroy()

    def destroy(self):
        self.models = None
        self.callback = None
