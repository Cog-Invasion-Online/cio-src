# Filename: SuitUtils.py
# Created by:  blach (29Dec15)

from panda3d.core import Point3, Point2

from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, Func

from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
import SuitAttacks

import random

def attack(suit, toon, attackIndex = None):
    suit.b_setAnimState('neutral')
    suit.headsUp(toon)
    if attackIndex is None:
        attack = random.choice(suit.suitPlan.getAttacks())
        attackIndex = SuitAttacks.SuitAttackLengths.keys().index(attack)
    else:
        attack = SuitAttacks.SuitAttackLengths.keys()[attackIndex]
    timestamp = globalClockDelta.getFrameNetworkTime()
    if suit.isDead():
        return None
    suit.sendUpdate('doAttack', [attackIndex, toon.doId, timestamp])
    return attack

def getMoveIvalFromPath(suit, path, elapsedT, isClient, seqName):
    moveIval = Sequence(name = suit.uniqueName(seqName))
    if isClient:
        moveIval.append(Func(suit.animFSM.request, 'walk'))
    for i in xrange(len(path)):
        if i == 0:
            continue
        waypoint = path[i]
        lastWP = path[i - 1]
        moveIval.append(Func(suit.headsUp, Point3(*waypoint)))
        ival = NPCWalkInterval(suit, Point3(*waypoint),
            startPos = Point3(*lastWP),
            fluid = 1, name = suit.uniqueName('doWalkIval' + str(i)),
            duration = (Point2(waypoint[0], waypoint[1]) - Point2(lastWP[0], lastWP[1])).length() * 0.2)
        moveIval.append(ival)
    if isClient:
        moveIval.append(Func(suit.animFSM.request, 'neutral'))
    return moveIval
