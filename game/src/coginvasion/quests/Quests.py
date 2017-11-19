"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Quests.py
@author Brian Lach
@date July 30, 2015

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog import SuitGlobals, Dept

from QuestGlobals import Tiers, Any, Anywhere
from Objectives import *
from Rewards import *

VisHQObj = [VisitNPCObjective, 0, 1]

objectives = "objectives"
reward = "reward"
rewards = "rewards"
assignSpeech = "assignSpeech"
finishSpeech = "finishSpeech"
requiredQuests = "rq"
tier = "tier"
finalInTier = "lastQuestInTier"

args = "args"
assigner = "assigner"
objType = "objType"
collection = "collection"
name = "name"

Quests = {

    0: {objectives: [
            {objType: VisitNPCObjective, args: [2003]},
            {objType: CogObjective, args: [SuitGlobals.Flunky, 1, CIGlobals.ToontownCentralId], assigner: 2003}
        ],
        rewards: [(Health, 1)],
        tier: Tiers.TT,
        assignSpeech: (
            "Nice work completing the tutorial!\x07You're probably already exhausted, but " + CIGlobals.NPCToonNames[2003] + " needs"
            " you right away.\x07"
        ),
        finishSpeech: ("Great job, young lad.\x07I see loads of potential in you.\x07One day you will be one of the best Cog busters around!\x07"),
        name: 'Schooled'},
          
    2 : {objectives : [
            {objType : CogObjective, args: [SuitGlobals.BottomFeeder, 8, CIGlobals.ToontownCentralId]}],
         rewards: [(Health, 1)],
         tier: Tiers.TT,
         assignSpeech: ("Those Bottom Feeders sure are running rampant around town recently.\x07Think you could do something about that?\x07"),
         finishSpeech: ("Fantastic!\x07You helped clean the streets of Toontown!\x07This should help you out...\x07"),
         name: "Bottoms Up!"},

    4: {objectives: [
            {objType: VisitNPCObjective, args: [2322]},
            {objType: VisitNPCObjective, args: [2108]},
            {objType: VisitNPCObjective, args: [2322]}
        ],
        rewards: [(Access, CIGlobals.DonaldsDockId)],
        tier: Tiers.TT,
        finalInTier: True,
        assignSpeech: (
               "Something strange is going on at " + CIGlobals.zone2TitleDict[CIGlobals.NPCToonDict[2322][0]][0] + ".\x07"
               "Nobody else has been available to help, and " + CIGlobals.NPCToonNames[2322] + " is in desperate need of someone.\x07"
               "Go see him and find out what the problem is.\x07"),
        finishSpeech: ("What a great friend " + CIGlobals.NPCToonNames[2108] + " is, right?\x07Wow, thank you so much!\x07You know, some of his books are really great. "
                       "There's this one about a clock that--\x07You know what, I should let you be on your way.\x07Here, take this as a reward for your awesome help...\x07"),
        name: 'Strange Occurrences'},
          
    20: {objectives: [
            {objType: CogBuildingObjective, args: [Any, Any, 1, CIGlobals.DaisyGardensId]}
        ],
        rewards: [(GagSlot, 2)],
        tier: Tiers.TT,
        requiredQuests: [0],
        name: 'Pick 1, Pick Anyone!'},
          
    3: {objectives: [
            {objType: VisitNPCObjective, args: [5312]},
            {objType: RecoverItemObjective, args: [7, CIGlobals.DaisyGardensId, 
                'Green Beans', QuestGlobals.getPackageIcon(), SuitGlobals.BeanCounter],
                assigner: 5312
            }
        ],
        rewards: [(Health, 2)],
        tier: Tiers.DG,
        name: 'Eugene and the Bean Stock',
        finishSpeech: ("Thank you so much for returning my beans!\0x7Now, thanks to you, I can continue my business!\0x7Here have this!"),
    },
          
    38: {objectives: [
            {objType: CogBuildingObjective, args: [Any, Any, 1, CIGlobals.ToontownCentralId]},
        ],
        rewards: [(Jellybeans, 50)],
        tier: Tiers.TT,
        name: 'Office Crash',
    }
}

QuestNPCDialogue = {
    0: {1: ("Hello! I'm glad you stopped by.\x07My name is " + CIGlobals.NPCToonNames[2003] + ", PhD in Sillytology.\x07I'm conducting a study"
            " on new Toons to see how much potential they have.\x07Let's see how much potential you have...\x07Go out, defeat a Flunky"
            " and report back immediately!")},

    4: {1: ("Oh, thank goodness you are here!\x07The recipe for my signature whipped cream has gone missing!\x07"
            "I have absolutely no idea where it went.\x07It was right here, on my desk!\x07"
            "I went back to the kitchen to check on an order, and when I got back... it was gone!\x07My restaurant is far too busy today... "
            "there's no way I can leave this spot.\x07I wonder if my friend " + CIGlobals.NPCToonNames[2108] + " knows where it went."
            "\x07Could you please go ask him if he knows where it went?\x07"),
        2: ("Whipped cream recipe, eh?\x07I haven't seen " + CIGlobals.NPCToonNames[2322] + " all day, and I never saw a whipped cream recipe anywhere.\x07Oh, wait! "
            "I remember " + CIGlobals.NPCToonNames[2322] + " emailed me that recipe!\x07It's truly the best whipped cream I've ever had. "
            "I love putting it on waffles.\x07Here, let me print out a copy of the recipe, and you can give it to " + CIGlobals.NPCToonNames[2322] + ".\x07"
            "Okay... here you go!\x07Tell " + CIGlobals.NPCToonNames[2322] + " I said hi!")},
    3: {1: ("Thank goodness you are here!\x07A couple Bean Counters raided my shop last night and stole all the beans I had in storage!\x07Even worse, those Bean Counters plan on making a profit off my precious green beans!\x07Please, whatever you do, stop those Bean Counters!\x07")}
}
