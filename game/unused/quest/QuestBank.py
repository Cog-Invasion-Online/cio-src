########################################
# Filename: QuestBank.py
# Created by: DecodedLogic (18Jul16)
########################################

from src.coginvasion.quest.Quest import Quest
from src.coginvasion.quest.objective.VisitNPCObjective import VisitNPCObjective
from src.coginvasion.quest.objective.CogObjective import CogObjective
from src.coginvasion.quest.objective.DeliverItemObjective import DeliverItemObjective
from src.coginvasion.quest.objective.RecoverItemObjective import RecoverItemObjective
from src.coginvasion.quest.QuestReward import QuestReward
from src.coginvasion.quest import RewardType, QuestGlobals

from collections import OrderedDict

name = 'name'
objectives = 'objectives'
rewards = 'rewards'
assignSpeech = 'assignSpeech'
finishSpeech = 'finishSpeech'
requirements = 'requirements'
tier = 'tier'
finalInTier = 'finalInTier'

Quests = {
    0 : {name : 'Schooled', requirements : [], tier : 0, rewards : {RewardType.LAFF_POINTS : 2},
     objectives: OrderedDict([(
        VisitNPCObjective, {'npcId' : 2003, 'assigner' : QuestGlobals.NOBODY}),
        (CogObjective, {'location' : None, 'assigner' : 2003, 'amount' : 4, 'level' : 2}),
        (VisitNPCObjective, {'npcId' : 2003, 'assigner' : 2003})
     ])
    }
}

QuestNPCDialogue = {
}

# Pass this the dictionary regarding this quest.
# This should be the dictionary followed by the questId (key) in the quests
# dictionary.
def generateQuestFromData(data):
    questId = Quests.values().index(data)
    questName = data.get(name) if name in data.keys() else None
    requirements = data.get(requirements) if requirements in data.keys() else []
    tier = data.get(tier) if tier in data.keys() else -1
    dataRewards = data.get(rewards) if rewards in data.keys() else {}
    dataObjectives = data.get(objectives) if objectives in data.keys() else None
    isFinalInTier = data.get(finalInTier) if finalInTier in data.keys() else False
    objectives = []
    
    # We must have a name and objective for EVERY quest.
    if questName is None or dataObjectives is None:
        raise ValueError('Quest ID %s is not setup correctly! Make sure it has a name & OrderedDict of objectives!' % questId)
        return None
    
    # Let's generate the quest rewards.
    rewards = []
    for rewardType, modifier in dataRewards.items():
        rewards.append(QuestReward(rewardType, modifier))
    
    # Here comes the hard part, loading the objectives...
    for objType, objArgs in dataObjectives.items():
        requiredObjArgs = ['location', 'assigner']
        location = objArgs.get('location') if 'location' in objArgs.keys() else None
        assigner = objArgs.get('assigner') if 'assigner' in objArgs.keys() else []
        objective = None
        
        # This variable is for item tasks.
        itemName = ''
        itemIcon = None
        if objType.__class__ == DeliverItemObjective or objType.__class__ == RecoverItemObjective:
            itemName = objArgs.get('itemName') if 'itemName' in objArgs.keys() else ''
            itemIcon = objArgs.get('itemIcon') if 'itemIcon' in objArgs.keys() else QuestGlobals.getPackageIcon()
            requiredObjArgs.append('itemName')

        # We don't require a location for the VisitNPCObjective,
        # however, we need an NPC id
        if isinstance(objType, VisitNPCObjective):
            npcId = objArgs.get('npcId') if 'npcId' in objArgs.keys() else None
            requiredObjArgs.append('npcId')
            
            if objType.__class__ == VisitNPCObjective:
                objective = VisitNPCObjective(npcId, assigner, location)
            elif objType.__class__ == DeliverItemObjective:
                amount = objArgs.get('amount') if 'amount' in objArgs.keys() else 0
                objective = DeliverItemObjective(npcId, itemName, amount, assigner, location, itemIcon)
        
        # We need an amount for the CogObjective
        if isinstance(objType, CogObjective):
            amount = objArgs.get('amount') if 'amount' in objArgs.keys() else 0
            level = objArgs.get('level') if 'level' in objArgs.keys() else None
            levelRange = objArgs.get('levelRange') if 'levelRange' in objArgs.keys() else None
            name = objArgs.get('name') if 'name' in objArgs.keys() else None
            variant = objArgs.get('variant') if 'variant' in objArgs.keys() else None
            dept = objArgs.get('dept') if 'dept' in objArgs.keys() else None
            requiredObjArgs.append('amount')
            
            if objType.__class__ == CogObjective:
                objective = CogObjective(location, assigner, amount, level, levelRange,
                    name, variant, dept)
            elif objType.__class__ == RecoverItemObjective:
                objective = RecoverItemObjective(amount, itemName, assigner, location,
                    itemIcon, level, levelRange, name, variant, dept)
        
        # Objective variables other than the required ones can be specified here.
        for parameter, argument in objArgs.items():
            if not parameter in requiredObjArgs:
                if objective.hasattr(objective, parameter):
                    objective.setattr(objective, parameter, argument)
                else:
                    raise ValueError('Objective type %s does not have a declared variable named "%s"' % (objective.__class__.__name__, parameter))
                    break
                
        if not objective is None:
            objectives.append(objective)
        else:
            raise ValueError('Objective type %s has not been registered inside of QuestBank #generateQuestFromData()' % objType.__class__.__name__)
    
    if len(objectives) == len(objType.keys()):
        return Quest(name, requirements, tier, questId, rewards, objectives, isFinalInTier = isFinalInTier)
    return None
