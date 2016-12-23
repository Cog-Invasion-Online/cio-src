"""

  Filename: NPCWalker.py
  Created by: blach (02Nov14)

"""

from pandac.PandaModules import Point3

from direct.interval.LerpInterval import LerpPosInterval, LerpQuatInterval
from direct.directnotify.DirectNotifyGlobal import directNotify

class NPCWalkInterval(LerpPosInterval):
    notify = directNotify.newCategory("NPCWalkInterval")

    def __init__(self, nodePath, pos, durationFactor = 0.2,
                startPos = None, other = None, blendType = 'noBlend',
                bakeInStart = 1, fluid = 0, name = None, lookAtTarget = True, duration = None):
        self.nodePath = nodePath
        self.pos = pos
        if type(pos) != type(Point3()):
            self.notify.warning("pos argument must be of type %s, not of type %s"
                            % (type(Point3()), type(pos)))
            return None
        if duration is None:
            _distance = (pos.getXy() - (nodePath.getX(), nodePath.getY())).length()
            duration = _distance * durationFactor
        LerpPosInterval.__init__(self, nodePath, duration, pos, startPos,
                                other, blendType, bakeInStart, fluid, name)
        if lookAtTarget:
            self.nodePath.headsUp(self.pos)

    def setDuration(self, duration):
        self.duration = duration

class NPCLookInterval(LerpQuatInterval):
    notify = directNotify.newCategory("NPCLookInterval")

    def __init__(self, nodePath, lookAtNode, durationFactor = 0.01,
                name = None, blendType = 'noBlend', bakeInStart = 1,
                fluid = 0, other = None, isBackwards = False):
        _oldHpr = nodePath.getHpr()
        #if isBackwards:
        #	_oldHpr.setX(_oldHpr.getXy()[0] - 180)
        nodePath.headsUp(lookAtNode)
        #if isBackwards:
        #	nodePath.setH(nodePath.getH() - 180)
        _newHpr = nodePath.getHpr()
        nodePath.setHpr(_oldHpr)
        _distance = (_newHpr.getXy() - _oldHpr.getXy()).length()
        self.distance = _distance
        duration = _distance * durationFactor
        LerpQuatInterval.__init__(self, nodePath, duration, _newHpr,
                startHpr = _oldHpr, other = other, blendType = blendType,
                bakeInStart = bakeInStart, fluid = fluid, name = name)
