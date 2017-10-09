"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MGPlayground.py
@author Brian Lach
@date January 05, 2015

"""

from Playground import Playground
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify

class MGPlayground(Playground):
	notify = directNotify.newCategory("MGPlayground")
