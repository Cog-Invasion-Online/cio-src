"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitGlobals.py
@author Maverick Liberty
@date July 31, 2015

"""

from src.coginvasion.cog import Dept
from src.coginvasion.cog.SuitType import SuitType
from src.coginvasion.gags import GagGlobals

from panda3d.core import Vec4

# The cog classes
CC_minion        = 0
CC_secretary     = 1
CC_scout         = 2
CC_enforcer      = 3
CC_marshal       = 4
CC_supervisor    = 5

ClassNameById = {
    CC_minion:       'Minion',
    CC_secretary:    'Secretary',
    CC_scout:        'Scout',
    CC_enforcer:     'Enforcer',
    CC_marshal:      'Marshal',
    CC_supervisor:   'Supervisor'
}

def getClassName(id):
    return ClassNameById.get(id, 'Unknown')

class CogClassAttributes:

    def __init__(self, walkMod = 1.0, hpMod = 1.0, dmgMod = 1.0,
                 healer = False, footsteps = True, baseHp = 100,
                 gagRamps = {}, scaleMod = 1.0, voiceMod = 1.0):
        self.walkMod = walkMod
        self.hpMod = hpMod
        self.dmgMod = dmgMod
        self.healer = healer
        self.footsteps = footsteps
        self.baseHp = baseHp
        self.gagRamps = gagRamps
        self.scaleMod = scaleMod
        self.voiceMod = voiceMod

    def getGagDmgRamp(self, gagId):
        return self.gagRamps.get(gagId, 1.0)

classAttrsById = {
    # TODO:
    # Higher level minions can stun toons
    # Drop gags slow their movement greatly
    CC_minion:       CogClassAttributes(walkMod = 2.0, dmgMod = 0.5, scaleMod = 0.5, voiceMod = 1.75, baseHp = 10),

    CC_secretary:    CogClassAttributes(walkMod = 1.8, dmgMod = 0.7, scaleMod = 0.7, voiceMod = 1.5, baseHp = 25, healer = True,
                                       gagRamps = {GagGlobals.Trap: 1.1}),

    CC_scout:        CogClassAttributes(walkMod = 1.3, dmgMod = 1.0, scaleMod = 0.95, voiceMod = 1.1, baseHp = 30,
                                       gagRamps = {GagGlobals.Sound: 0.9, GagGlobals.Squirt: 1.15}, footsteps = False),

    CC_enforcer:     CogClassAttributes(walkMod = 1.2, dmgMod = 1.1, scaleMod = 1.0, voiceMod = 1.0, baseHp = 50),

    # TODO:
    # Can shield supervisor cogs
    CC_marshal:      CogClassAttributes(walkMod = 1.1, dmgMod = 1.2, scaleMod = 1.0, voiceMod = 0.9, baseHp = 75),

    # TODO:
    # Sound gags award a temporary 2-5 second speed boost (they anger them)
    CC_supervisor:   CogClassAttributes(walkMod = 0.9, dmgMod = 1.3, scaleMod = 1.0, voiceMod = 0.8, baseHp = 100,
                                       gagRamps = {GagGlobals.Throw: 1.1})
}

def getClassAttrs(id):
    return classAttrsById.get(id, CogClassAttributes())

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

HealTaunt = "Here, take this med-kit."
Suits = 'Cogs'

GeneralTaunts = ["It's my day off.",
                    "I believe you're in the wrong office.",
                    "Have your people call my people.",
                    "You're in no position to meet with me.",
                    "Talk to my assistant.",
                    "I don't take meetings with Toons.",
                    "I excel at Toon disposal.",
                    "You'll have to go through me first.",
                    "You're not going to like the way I work.",
                    "Let's see how you rate my job performance.",
                    "I'd like some feedback on my performance.",
                    "Surprised to hear from me?",
                    "You've got big trouble on the line."]

FaceoffTaunts = {Bloodsucker: ['Do you have a donation for me?',
       "I'm going to make you a sore loser.",
       "I'm going to leave you high and dry.",
       'I\'m "A Positive" I\'m going to win.',
       '"O" don\'t be so "Negative".',
       "I'm surprised you found me, I'm very mobile.",
       "I'm going to need to do a quick count on you.",
       "You're soon going to need a cookie and some juice.",
       "When I'm through you'll need to lie down.",
       'This will only hurt for a second.',
       "I'm going to make you dizzy.",
       "Good timing, I'm a pint low.",
       "You'll B the opposite of A happy toon when I'm finished with you."],
 TheMingler: ["You don't know who you're mingling with.",
       'Ever mingle with the likes of me?',
       'Good, it takes two to mingle.',
       "Let's mingle.",
       'This looks like a good place to mingle.',
       "Well,isn't this cozy?",
       "You're mingling with defeat.",
       "I'm going to mingle in your business.",
       "Are you sure you're ready to mingle?"],
 MoverShaker: ['Get ready for a shake down.',
        'You had better move out of the way.',
        'Move it or lose it.',
        "I believe it's my move.",
        'This should shake you up.',
        'Prepare to be moved.',
        "I'm ready to make my move.",
        "Watch out toon, you're on shaky ground.",
        'This should be a moving moment.',
        'I feel moved to defeat you.',
        'Are you shaking yet?'],
 HeadHunter: ["I'm way ahead of you.",
        "You're headed for big trouble.",
        "You'll wish this was all in your head.",
        "Oh good, I've been hunting for you.",
        "I'll have your head for this.",
        'Heads up!',
        "Looks like you've got a head for trouble.",
        'Headed my way?',
        'A perfect trophy for my collection.',
        'You are going to have such a headache.',
        "Don't lose your head over me."],
 TheBigCheese: ["Watch out, I'm gouda getcha.",
         'You can call me Jack.',
         'Are you sure?  I can be such a Muenster at times.',
         'Well finally, I was afraid you were stringing me along.',
         "I'm going to cream you.",
         "Don't you think I've aged well?",
         "I'm going to make mozzarella outta ya.",
         "I've been told I'm very strong.",
         'Careful, I know your expiration date.',
         "Watch out, I'm a whiz at this game.",
         'Beating you will be a brieeze.'],
 CorporateRaider: ['RAID!',
        "You don't fit in my corporation.",
        'Prepare to be raided.',
        "Looks like you're primed for a take-over.",
        'That is not proper corporate attire.',
        "You're looking rather vulnerable.",
        'Time to sign over your assets.',
        "I'm on a toon removal crusade.",
        'You are defenseless against my ideas.',
        "Relax, you'll find this is for the best."],
 MrHollywood: ['Are you ready for my take?',
        'Lights, camera, action!',
        "Let's start rolling.",
        'Today the role of defeated toon, will be played by - YOU!',
        'This scene will go on the cutting room floor.',
        'I already know my motivation for this scene.',
        'Are you ready for your final scene?',
        "I'm ready to roll your end credits.",
        'I told you not to call me.',
        "Let's get on with the show.",
        "There's no business like it!",
        "I hope you don't forget your lines."],
 NumberCruncher: ['Looks like your number is up.',
        'I hope you prefer extra crunchy.',
        "Now you're really in a crunch.",
        'Is it time for crunch already?',
        "Let's do crunch.",
        'Where would you like to have your crunch today?',
        "You've given me something to crunch on.",
        'This will not be smooth.',
        'Go ahead, try and take a number.',
        'I could do with a nice crunch about now.'],
 LoanShark: ["It's time to collect on your loan.",
        "You've been on borrowed time.",
        'Your loan is now due.',
        'Time to pay up.',
        'Well you asked for an advance and you got it.',
        "You're going to pay for this.",
        "It's pay back time.",
        'Can you lend me an ear?',
        "Good thing you're here,  I'm in a frenzy.",
        'Shall we have a quick bite?',
        'Let me take a bite at it.'],
 MoneyBags: ['Time to bring in the big bags.',
        'I can bag this.',
        'Paper or plastic?',
        'Do you have your baggage claim?',
        "Remember, money won't make you happy.",
        'Careful, I have some serious baggage.',
        "You're about to have money trouble.",
        'Money will make your world go around.',
        "I'm too rich for your blood.",
        'You can never have too much money!'],
 RobberBaron: ["You've been robbed.",
        "I'll rob you of this victory.",
        "I'm a royal pain!",
        'Hope you can grin and baron.',
        "You'll need to report this robbery.",
        "Stick 'em up.",
        "I'm a noble adversary.",
        "I'm going to take everything you have.",
        'You could call this neighborhood robbery.',
        'You should know not to talk to strangers.'],
 BackStabber: ['Never turn your back on me.',
        "You won't be coming back.",
        'Take that back or else!',
        "I'm good at cutting costs.",
        'I have lots of back up.',
        "There's no backing down now.",
        "I'm the best and I can back that up.",
        'Whoa, back up there toon.',
        'Let me get your back.',
        "You're going to have a stabbing headache soon.",
        'I have perfect puncture.',
        "Don't worry toon, you can always trust me."],
 BigWig: ["Don't brush me aside.",
        'You make my hair curl.',
        'I can make this permanent if you want.',
        "It looks like you're going to have some split ends.",
        "You can't handle the truth.",
        "I think it's your turn to be dyed.",
        "I'm so glad you're on time for your cut.",
        "You're in big trouble.",
        "I'm going to wig out on you.",
        "I'm a big deal little toon."],
 LegalEagle: ["Careful, my legal isn't very tender.",
        'I soar, then I score.',
        "I'm bringing down the law on you.",
        'You should know, I have some killer instincts.',
        "I'm going to give you legal nightmares.",
        "You won't win this battle.",
        'This is so much fun it should be illegal.',
        "Legally, you're too small to fight me.",
        'There is no limit to my talons.',
        "I call this a citizen's arrest.",
        "I've got the court under my wing."],
 SpinDoctor: ["You'll never know when I'll stop.",
        'Let me take you for a spin.',
        'The doctor will see you now.',
        "I'm going to put you into a spin.",
        'You look like you need a doctor.',
        'The doctor is in, the Toon is out.',
        "You won't like my spin on this.",
        'You are going to spin out of control.',
        'Care to take a few turns with me?',
        'I have my own special spin on the subject.'],
 Flunky: ["I'm gonna tell the boss about you!",
       "I may be just a flunky - But I'm real spunky.",
       "I'm using you to step up the corporate ladder.",
       "You're not going to like the way I work.",
       'The boss is counting on me to stop you.',
       "You're going to look good on my resume.",
       "You'll have to go through me first.",
       "Let's see how you rate my job performance.",
       'I excel at Toon disposal.',
       "You're never going to meet my boss.",
       "I'm sending you back to the Playground."],
 PencilPusher: ["I'm gonna rub you out!",
       "Hey, you can't push me around.",
       "I'm No.2!",
       "I'm going to scratch you out.",
       "I'll have to make my point more clear.",
       'Let me get right to the point.',
       "Let's hurry, I bore easily.",
       'I hate it when things get dull.',
       'So you want to push your luck?',
       'Did you pencil me in?',
       'Careful, I may leave a mark.'],
 Yesman: ["I'm positive you're not going to like this.",
        "I don't know the meaning of no.",
        'Want to meet?  I say yes, anytime.',
        'You need some positive enforcement.',
        "I'm going to make a positive impression.",
        "I haven't been wrong yet.",
        "Yes, I'm ready for you.",
        'Are you positive you want to do this?',
        "I'll be sure to end this on a positive note.",
        "I'm confirming our meeting time.",
        "I won't take no for an answer."],
 Micromanager: ["I'm going to get into your business!",
        'Sometimes big hurts come in small packages.',
        'No job is too small for me.',
        "I want the job done right, so I'll do it myself.",
        'You need someone to manage your assets.',
        'Oh good, a project.',
        "Well, you've managed to find me.",
        'I think you need some managing.',
        "I'll take care of you in no time.",
        "I'm watching every move you make.",
        'Are you sure you want to do this?',
        "We're going to do this my way.",
        "I'm going to be breathing down your neck.",
        'I can be very intimidating.',
        "I've been searching for my growth spurt."],
 Downsizer: ["You're going down!",
        'Your options are shrinking.',
        'Expect diminishing returns.',
        "You've just become expendable.",
        "Don't ask me to lay off.",
        'I might have to make a few cutbacks.',
        'Things are looking down for you.',
        'Why do you look so down?'],
 ColdCaller: ['Surprised to hear from me?',
        'You rang?',
        'Are you ready to accept my charges?',
        'This caller always collects.',
        "I'm one smooth operator.",
        "Hold the phone -- I'm here.",
        'Have you been waiting for my call?',
        "I was hoping you'd answer my call.",
        "I'm going to cause a ringing sensation.",
        'I always make my calls direct.',
        'Boy, did you get your wires crossed.',
        'This call is going to cost you.',
        "You've got big trouble on the line."],
 Telemarketer: ['I plan on making this inconvenient for you.',
        'Can I interest you in an insurance plan?',
        'You should have missed my call.',
        "You won't be able to get rid of me now.",
        'This a bad time?  Good.',
        'I was planning on running into you.',
        'I will be reversing the charges for this call.',
        'I have some costly items for you today.',
        'Too bad for you - I make house calls.',
        "I'm prepared to close this deal quickly.",
        "I'm going to use up a lot of your resources."],
 NameDropper: ['In my opinion, your name is mud.',
        "I hope you don't mind if I drop your name.",
        "Haven't we met before?",
        "Let's hurry, I'm having lunch with 'Mr. Hollywood.'",
        "Have I mentioned I know 'The Mingler?'",
        "You'll never forget me.",
        'I know all the right people to bring you down.',
        "I think I'll just drop in.",
        "I'm in the mood to drop some Toons.",
        "You name it, I've dropped it."],
 GladHander: ['Put it there, Toon.',
        "Let's shake on it.",
        "I'm going to enjoy this.",
        "You'll notice I have a very firm grip.",
        "Let's seal the deal.",
        "Let's get right to the business at hand.",
        "Off handedly I'd say, you're in trouble.",
        "You'll find I'm a handful.",
        'I can be quite handy.',
        "I'm a very hands-on kinda guy.",
        'Would you like some hand-me-downs?',
        'Let me show you some of my handiwork.',
        'I think the handwriting is on the wall.',
        "I'll gladly handle your gags for you"],
 ShortChange: ['I will make short work of you.',
        "You're about to have money trouble.",
        "You're about to be overcharged.",
        'This will be a short-term assignment.',
        "I'll be done with you in short order.",
        "You'll soon experience a shortfall.",
        "Let's make this a short stop.",
        "I think you've come up short.",
        'I have a short temper for Toons.',
        "I'll be with you shortly.",
        "You're about to be shorted.",
        "Well, aren't you a little short on your changes?"],
 PennyPincher: ['This is going to sting a little.',
        "I'm going to give you a pinch for luck.",
        "You don't want to press your luck with me.",
        "I'm going to put a crimp in your smile.",
        'Perfect, I have an opening for you.',
        'Let me add my two cents.',
        "I've been asked to pinch-hit.",
        "I'll prove you're not dreaming.",
        'Heads you lose, tails I win.',
        'A Penny for your gags.'],
 Tightwad: ['Things are about to get very tight.',
        "That's Mr. Tightwad to you.",
        "I'm going to cut off your funding.",
        'Is this the best deal you can offer?',
        "Let's get going - time is money.",
        "You'll find I'm very tightfisted.",
        "You're in a tight spot.",
        'Prepare to walk a tight rope.',
        'I hope you can afford this.',
        "I'm going to make this a tight squeeze.",
        "I'm going to make a big dent in your budget."],
 BeanCounter: ['I enjoy subtracting Toons.',
        'You can count on me to make you pay.',
        'Bean there, done that.',
        'I can hurt you where it counts.',
        'I make every bean count.',
        'Your expense report is overdue.',
        'Time for an audit.',
        "Let's step into my office.",
        'Where have you bean?',
        "I've bean waiting for you.",
        "I'm going to bean you."],
 BottomFeeder: ["Looks like you've hit rock bottom.",
        "I'm ready to feast.",
        "I'm a sucker for Toons.",
        'Oh goody, lunch time.',
        'Perfect timing, I need a quick bite.',
        "I'd like some feedback on my performance.",
        "Let's talk about the bottom line.",
        "You'll find my talents are bottomless.",
        'Good, I need a little pick-me-up.',
        "I'd love to have you for lunch."],
 TwoFace: ["It's time to face-off!",
        'You had better face up to defeat.',
        'Prepare to face your worst nightmare!',
        "Face it, I'm better than you.",
        'Two heads are better than one.',
        'It takes two to tango, you wanna tango?',
        "You're in for two times the trouble.",
        'Which face would you like to defeat you?',
        "I'm 'two' much for you.",
        "You don't know who you're facing.",
        'Are you ready to face your doom?',
        "My eyes are on you."],
 DoubleTalker: ["I'm gonna give you double the trouble.",
        'See if you can stop my double cross.',
        'I serve a mean double-\x04DECKER.',
        "It's time to do some double-dealing.",
        'I plan to do some double DIPPING.',
        "You're not going to like my double play.",
        'You may want to double think this.',
        'Get ready for a double TAKE.',
        'You may want to double up against me.',
        'Doubles anyone??'],
 AmbulanceChaser: ["I'm going to chase you out of town!",
        'Do you hear a siren?',
        "I'm going to enjoy this.",
        'I love the thrill of the chase.',
        'Let me give you the run down.',
        'Do you have insurance?',
        'I hope you brought a stretcher with you.',
        'I doubt you can keep up with me.',
        "It's all uphill from here.",
        "You're going to need some urgent care soon.",
        'This is no laughing matter.',
        "I'm going to give you the business."]
}

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
    Anim(5, 'watercooler', suitTypes = [SuitType.C]),
    Anim(5, 'hold-pencil', suitTypes = [SuitType.B]),
    Anim(5, 'rubber-stamp', suitTypes = [SuitType.A, SuitType.C])
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
    
def calculateHP(level):
    return (level + 1) * (level + 2)

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
