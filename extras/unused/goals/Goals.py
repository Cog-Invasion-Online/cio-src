"""

  Filename: Goals.py
  Created by: blach (31Jan15)

"""

class Goal:
	
	def __init__(self, data):
		self.completed = False
		self.reward = data.get("reward")
		self.goalType = None
		
	def getGoalType(self):
		return self.goalType
		
	def isCompleted(self):
		return self.completed
		
	def getReward(self):
		return self.reward
		
	def setReward(self, reward):
		self.reward = reward

class CogGoal(Goal):
	
	def __init__(self, data):
		self.goalNum = data.get("goalNum")
		self.goalCog = data.get("cog")
		self.progress = data.get("progress")
		Goal.__init__(self, data)
		self.goalType = CIGlobals.Suit
		
	def getCog(self):
		return self.goalCog
		
	def setCogProgress(self, numCogs):
		self.progress = numCogs
		
	def isCompleted(self):
		return self.cogProgress >= self.cogGoal
		
	def getCogProgress(self):
		return self.progress
		
	def getCogGoal(self):
		return self.goalNum
		
class MinigameGoal(Goal):
	
	def __init__(self, data):
		self.event = data.get("event")
		self.game = data.get("game")
		self.value = data.get("value")
		Goal.__init__(self, data)
		self.goalType = CIGlobals.Minigame
		
	def getEvent(self):
		return self.event
		
	def getGame(self):
		return self.game
		
	def getValue(self):
		return self.value
