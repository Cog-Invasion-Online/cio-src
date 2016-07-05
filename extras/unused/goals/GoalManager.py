"""

  Filename: GoalManager.py
  Created by: blach (01Feb15)

"""

import random, os

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.goals.Goals import *

class GoalManager:
	
	def __init__(self):
		self.currentGoal = None
		
	def generateGoal(self):
		data = {}
		
		# 0-1 = CogGoal
		# 2 = MinigameGoal
		goalType = random.randint(0, 2)
		if goalType in [0, 1]:
			goalClass = CogGoal
			invasionOrSuit = random.randint(0, 4)
			if invasionOrSuit in [0, 1, 2, 3]:
				cogList = []
				for name in CIGlobals.SuitNames.keys():
					cogList.append(name)
				value = random.randint(1, 20)
				data["cog"] = random.choice(cogList)
			else:
				data["cog"] = "invasion"
				value = random.randint(1, 3)
			data["goalNum"] = value
			data["progress"] = 0
		else:
			goalClass = MinigameGoal
			goalData = open("MinigameGoals.txt")
			lines = goalData.readlines()
			if base.localAvatar.getMinigameProgress() >= len(lines):
				goalData.close()
				del goalData
				self.generateGoal()
				return
			line = lines[base.localAvatar.getMinigameProgress()]
			game, event, value = line.split(':')
			data["game"] = game
			data["event"] = event
			data["value"] = value
			data["reward"] = random.randint(1, 4)
		self.currentGoal = goalClass(data)
			
	def getCurrentGoal(self):
		return self.currentGoal
