"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitGlobals.py
@author Maverick Liberty
@date July 31, 2015

"""

from src.coginvasion.cog import Dept
from src.coginvasion.cog.SuitType import SuitType
from panda3d.core import Vec4

# The following are all the suit names

TheBigCheese = 'The Big Cheese'
CorporateRaider = 'Corporate Raider'
HeadHunter = 'Head Hunter'
Downsizer = 'Downsizer'
Micromanager = 'Micromanager'
Yesman = 'Yesman'
PencilPusher = 'Pencil Pusher'
Flunky = 'Flunky'
BigWig = 'Big Wig'
LegalEagle = 'Legal Eagle'
SpinDoctor = 'Spin Doctor'
BackStabber = 'Back Stabber'
AmbulanceChaser = 'Ambulance Chaser'
DoubleTalker = 'Double Talker'
Bloodsucker = 'Bloodsucker'
BottomFeeder = 'Bottom Feeder'
RobberBaron = 'Robber Baron'
LoanShark = 'Loan Shark'
MoneyBags = 'Money Bags'
NumberCruncher = 'Number Cruncher'
BeanCounter = 'Bean Counter'
Tightwad = 'Tightwad'
PennyPincher = 'Penny Pincher'
ShortChange = 'Short Change'
MrHollywood = 'Mr. Hollywood'
TheMingler = 'The Mingler'
TwoFace = 'Two-Face'
MoverShaker = 'Mover & Shaker'
GladHander = 'Glad Hander'
NameDropper = 'Name Dropper'
Telemarketer = 'Telemarketer'
ColdCaller = 'Cold Caller'
VicePresident = 'Senior V.P.'
LucyCrossbill = 'Lucy Crossbill'

# These are names for events.

healthChangeEvent = 'suit%s-hpChangeEvt'
animStateChangeEvent = 'suit%s-animStateChangeEvt'
suitSpawnedEvent = 'suit%s-spawnedEvt'
suitDespawnedEvent = 'suit%s-despawnedEvt'

scaleFactors = {'A' : 6.06, 'B' : 5.29, 'C' : 4.14}

# These are all the animations for suits.

class Anim:

    def __init__(self, phase, fileName, name = None, suitTypes = [SuitType.A, SuitType.B, SuitType.C], deathHoldTime = 0):
        self.name = name
        self.phase = phase
        self.file = fileName
        self.deathHoldTime = deathHoldTime
        self.suitTypes = suitTypes

        if not self.name:
            self.name = self.file

    def getName(self):
        return self.name

    def getPhase(self):
        return self.phase

    def getFile(self):
        return self.file

    def getSuitTypes(self):
        return self.suitTypes

    def getDeathHoldTime(self):
        return self.deathHoldTime

animations = [
    Anim(4, 'neutral'),
    Anim(4, 'walk'),
    Anim(4, 'victory', name = 'win'),
    Anim(4, 'pie-small', name = 'pie', deathHoldTime = 2.0),
    Anim(5, 'landing', name = 'land'),
    Anim(4, 'squirt-small', deathHoldTime = 4.0),
    Anim(5, 'squirt-large', deathHoldTime = 4.9),
    Anim(5, 'soak', deathHoldTime = 6.5),
    Anim(4, 'slip-forward'),
    Anim(4, 'slip-backward'),
    Anim(4, 'flailing', name = 'flail', deathHoldTime = 1.5),
    Anim(5, 'drop', deathHoldTime = 6.0),
    Anim(5, 'anvil-drop', name = 'drop-react', deathHoldTime = 3.5),
    Anim(5, 'throw-object'),
    Anim(5, 'throw-paper'),
    Anim(5, 'glower'),
    Anim(5, 'pickpocket'),
    Anim(7, 'fountain-pen', name = 'fountainpen'),
    Anim(5, 'phone'),
    Anim(5, 'finger-wag', name = 'fingerwag'),
    Anim(5, 'speak'),
    Anim(5, 'lured'),
    Anim(5, 'magic1'),
    Anim(5, 'magic2'),
    Anim(5, 'magic3', suitTypes = [SuitType.A, SuitType.B]),
    Anim(12, 'sit'),
    Anim(12, 'tray-neutral'),
    Anim(12, 'tray-walk'),
    Anim(5, 'golf-club-swing', name = 'golf', suitTypes = [SuitType.A]),
    Anim(5, 'watercooler', suitTypes = [SuitType.C])
]

def getAnimById(animId):
    return animations[animId]

def getAnimId(anim):
    for iAnim in animations:
        if iAnim == anim:
            return animations.index(iAnim)

def getAnimByName(animName):
    for anim in animations:
        if anim.getName() == animName:
            return anim

def getAnimations():
    return animations

def createStunInterval(suit, before, after):
    from direct.actor.Actor import Actor
    from panda3d.core import Point3
    from direct.interval.IntervalGlobal import Sequence, Wait, Func
    
    if not suit or suit.isEmpty() or not suit.headModel or suit.headModel.isEmpty():
        return Sequence(Wait(1.0))

    p1 = Point3(0)
    p2 = Point3(0)
    stars = Actor("phase_3.5/models/props/stun-mod.bam",
                  {"chan": "phase_3.5/models/props/stun-chan.bam"})
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.headModel
    head.calcTightBounds(p1, p2)
    return Sequence(Wait(before), Func(stars.reparentTo, head), Func(stars.setZ, max(0.0, p2[2] - 1.0)),
                    Func(stars.loop, 'chan'), Wait(after), Func(stars.cleanup))

propellerNeutSfx = 'phase_4/audio/sfx/TB_propeller.ogg'
propellerInSfx = 'phase_5/audio/sfx/ENC_propeller_in.ogg'
propellerOutSfx = 'phase_5/audio/sfx/ENC_propeller_out.ogg'
healedSfx = 'phase_3/audio/sfx/health.ogg'

medallionColors = {
    Dept.BOSS : Vec4(0.863, 0.776, 0.769, 1.0),
    Dept.LAW : Vec4(0.749, 0.776, 0.824, 1.0),
    Dept.CASH : Vec4(0.749, 0.769, 0.749, 1.0),
    Dept.SALES : Vec4(0.843, 0.745, 0.745, 1.0)
}

healthColors = (Vec4(0, 1, 0, 1),
    Vec4(1, 1, 0, 1),
    Vec4(1, 0.5, 0, 1),
    Vec4(1, 0, 0, 1),
    Vec4(0.3, 0.3, 0.3, 1))

healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
    Vec4(1, 1, 0.25, 0.5),
    Vec4(1, 0.5, 0.25, 0.5),
    Vec4(1, 0.25, 0.25, 0.5),
    Vec4(0.3, 0.3, 0.3, 0))
