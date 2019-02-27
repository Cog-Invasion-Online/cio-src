"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitUtils.py
@author Brian Lach
@date December 29, 2015

"""

from panda3d.core import Point3, Point2

from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, Func

from src.coginvasion.npc.NPCWalker import NPCWalkInterval
#import SuitAttacks

import random
"""
def attack(suit, toon, attack = None):
    suit.b_setAnimState('neutral')
    suit.headsUp(toon)
    if attack is None:
        attack = random.choice(suit.suitPlan.getAttacks())
    timestamp = globalClockDelta.getFrameNetworkTime()
    if suit.isDead():
        return None
    suit.sendUpdate('doAttack', [attack, toon.doId, timestamp])
    return attack
"""

def getMoveIvalFromPath(suit, path, elapsedT, isClient, seqName):
    baseSpeed = 5.0
    walkMod = suit.suitPlan.getCogClassAttrs().walkMod
    speed = baseSpeed * walkMod

    moveIval = Sequence(name = suit.uniqueName(seqName))
    if isClient:
        moveIval.append(Func(suit.setPlayRate, walkMod, 'walk'))
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
            duration = (Point2(waypoint[0], waypoint[1]) - Point2(lastWP[0], lastWP[1])).length() / speed)
        moveIval.append(ival)
    if isClient:
        moveIval.append(Func(suit.setPlayRate, 1.0, 'walk'))
        moveIval.append(Func(suit.animFSM.request, 'neutral'))
    return moveIval
