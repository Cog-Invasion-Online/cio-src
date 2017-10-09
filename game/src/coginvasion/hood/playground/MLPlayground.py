"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MLPlayground.py
@author Brian Lach
@date July 24, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from Playground import Playground

class MLPlayground(Playground):
    notify = directNotify.newCategory("MLPlayground")
