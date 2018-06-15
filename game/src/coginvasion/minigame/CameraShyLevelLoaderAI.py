"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CameraShyLevelLoaderAI.py
@author Maverick Liberty
@date November 6, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
import random

class CameraShyLevelLoaderAI:
    notify = directNotify.newCategory('CameraShyLevelLoaderAI')

    levels = ['TT_maze']

    levelData = {
        'TT_maze' : {
            'gameTime' : 150
        },
        'DG_playground' : {
            'gameTime' : 240
        }
    }

    def __init__(self, minigame):
        self.minigame = minigame
        self.level = ""

    # Select a random level.
    def selectLevel(self):
        self.level = random.choice(self.levels)
        self.minigame.d_setLevel(self.level)

    def getGameTime(self, level = None):
        if not level and self.level:
            return self.levelData[self.level]['gameTime']
        elif not level and not self.level:
            self.notify.warning('Attempted to get game time before a level was selected.')
            return 0
        elif level:
            return self.levelData[level]['gameTime']

    def getLevel(self):
        return self.level

    def cleanup(self):
        try:
            self.CameraShyLevelLoaderAI_deleted
        except:
            self.CameraShyLevelLoaderAI_deleted = 1
            self.minigame = None
            self.level = None
            self.levelData = None
            self.levels = None
