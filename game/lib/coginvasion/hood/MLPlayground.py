# Filename: MLPlayground.py
# Created by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from Playground import Playground

class MLPlayground(Playground):
    notify = directNotify.newCategory("MLPlayground")
