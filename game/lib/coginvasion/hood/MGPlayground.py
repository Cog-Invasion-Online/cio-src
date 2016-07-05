"""

  Filename: MGPlayground.py
  Created by: blach (05Jan15)

"""

from Playground import Playground
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify

class MGPlayground(Playground):
	notify = directNotify.newCategory("MGPlayground")
