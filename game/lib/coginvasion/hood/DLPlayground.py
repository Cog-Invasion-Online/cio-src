# Filename: DLPlayground.py
# Creatd by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from Playground import Playground

class DLPlayground(Playground):
    notify = directNotify.newCategory("DLPlayground")
