"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file KnockKnockGlobals.py
@author Maverick Liberty
@date October 22, 2017

"""

from direct.interval.IntervalGlobal import Sequence, Wait, Func

GREETING = "Knock! Knock!"
QUERY = "Who's there?"

DEF_WAIT = 1.0
DEF_PUNCHLINE_HOLD_TIME = 2.0

Jokes = {
# Joke Id : [Knocker Name, Punchline, (OPTIONAL) Punchline Hold Time]
    0 : ['Quest', "Shouldn't you be working on your Quest?!"],
    1 : ['Orange', "Orange you glad I didn't say Cog?!"],
    2 : ['Boo', 'Stop crying!'],
    3 : ['Canoe', 'Canoe help me with my homework?'] # Add onto loopy lane
}

Laughter = ['Ha Ha Ha', 'Hee Hee', 'Tee Hee', 'Ha Ha']
HealedLaughter = ['BWAH HAH HAH!', 'HO HO HO!', 'HA HA HA!']

Zone2EntertainmentData = {
# Branch Zone Id : [Heal Chance %, Heal Range]
    2300: [10, (1, 5)]
}

Zone2Block2Joke = {
    2303 : {
        1 : 0, 
        2 : 1
    }
}

def generateBasicJoke(avatar, door, knockerName, punchline, punchlineHoldTime, laughFunc):
    seq = Sequence()
    seq.append(Func(door.setChat, GREETING))
    seq.append(Wait(DEF_WAIT))
    seq.append(Func(avatar.setChat, QUERY))
    seq.append(Wait(DEF_WAIT))
    seq.append(Func(door.setChat, ('%s' % knockerName)))
    seq.append(Wait(DEF_WAIT))
    seq.append(Func(avatar.setChat, ('%s who?' % knockerName)))
    seq.append(Wait(DEF_WAIT))
    seq.append(Func(door.setChat, punchline))
    seq.append(Func(laughFunc))
    
    if avatar == base.localAvatar:
        # If we're playing this sequence on ourself, we should let the AI know that we heard the punchline.
        seq.append(Func(door.sendUpdate, 'iHeardPunchline', []))

    seq.append(Wait(punchlineHoldTime))
    return seq
    