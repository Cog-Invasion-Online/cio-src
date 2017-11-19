"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestData.py
@authors Maverick Liberty
@date November 14, 2017

@desc Parses and generates quest data strings used to store and load quest data.

String format:

ACTIVE_QUEST_ID (-1 or value >= 0)
<Quest ID,
Current Objective Index (The index of where the current objective or objectives are),
Tracking Objective Index (-1 if n/a or value >= 0),
[List of the progress of each accessible objective enclosed]

Example: 0 <0,0,1,[30,50,0]>
>

"""

BLOCK_OPENING_CHAR = '<'
BLOCK_CLOSING_CHAR = '>'
OBJECTIVE_BLOCK_OPENING_CHAR = '['
OBJECTIVE_BLOCK_CLOSING_CHAR = ']'

def getDataBlock(stump):
    # Retrieves data enclosed in a < > block and returns it in a list as integers followed
    # by the index of the ending of the block.
    blockOpeningIndex = stump.index(BLOCK_OPENING_CHAR)
    blockClosingIndex = stump.index(BLOCK_CLOSING_CHAR)
    
    subStr = stump[blockOpeningIndex+1:blockClosingIndex]
    objBlockOpeningIndex = subStr.index(',' + OBJECTIVE_BLOCK_OPENING_CHAR)
    
    # Generates a list of all the data enclosed within the block separated by a comma,
    # all the way up to the beginning of the list of accessible objectives.
    data = [int(element) for element in subStr[:objBlockOpeningIndex].split(',')]
    data.append(subStr[objBlockOpeningIndex+2:len(subStr)-1])
    return data, blockClosingIndex

def toDataStump(quests, trackingId = -1, currentObjectives = [], objectiveProgresses = []):
    # Generates a quest data stump for the quest data and returns it.
    # You can specify what the indexes of the current objectives with 'currentObjectives'; and
    # You can specify the progresses of each accessible objective in a list inside of 'objectiveProgresses'.
    dataString = '%d ' % (trackingId)
    
    for index, quest in enumerate(quests):
        sectionString = '<%d,%d,%d,%s>'
        objProgressStr = '['
        
        # This builds the string with the progress of each objective. Ex: [80,5,20]
        if len(objectiveProgresses) == 0 or len(objectiveProgresses) > 0 and len(objectiveProgresses[index]) == 0:
            # Let's use the objective progress inside of the quest.
            for i, objective in enumerate(quest.accessibleObjectives):
                objProgressStr += str(objective.progress)
                if i < len(quest.accessibleObjectives) - 1:
                    objProgressStr += ','
            objProgressStr += ']'
        else:
            # Let's use the values given to us to use instead.
            for i, progress in enumerate(objectiveProgresses[index]):
                objProgressStr += str(progress)
                if i < len(quest.accessibleObjectives) - 1:
                    objProgressStr += ','
            objProgressStr += ']'
            
        # Current Objective Index to use
        curObjIndex = quest.currentObjectiveIndex
        
        if len(currentObjectives) > 0 and 0 <= index <= len(currentObjectives):
            curObjIndex = currentObjectives[index]
        
        # This index is the position of the tracking objective relative to the accessible objectives collection.
        trackObjIndex = -1 if not quest.trackingObjective else quest.accessibleObjectives.index(quest.trackingObjective)
        
        sectionString = sectionString % (quest.id,
            curObjIndex, 
            trackObjIndex,
        objProgressStr)
        
        dataString += sectionString
    return dataString, currentObjectives, objectiveProgresses

def extractDataAsIntegerLists(dataStr, parseDataFunc = None):
    # If passed the parse data function, it will call that on the integer list
    # generated from every quest's data section.
    # Extracts data for quests from a string and returns the active quest id 
    # followed by a list of quest data with integers.
    # Objective progress is enclosed in an integer list within each quest's list.
    questsData = []
    activeQuestId = -1
    
    if not len(dataStr) == 0:
        activeQuestId = int(dataStr[:dataStr.index(' ')])
        
        while BLOCK_CLOSING_CHAR in dataStr:
            questData, cutOffIndex = getDataBlock(dataStr)
            
            # Creates an integer list of the progress of the accessible objectives.
            objProgress = [int(element) for element in questData[3].split(',')]
            questData[3] = objProgress
            questsData.append(questData)
            
            # If a parse function has been specified, we will call it and pass it
            # the newly extracted data.
            if not parseDataFunc is None:
                parseDataFunc(questData)
            
            # Let's remove this section of the data from the string.
            dataStr = dataStr[cutOffIndex+1:]
    return activeQuestId, questsData
    