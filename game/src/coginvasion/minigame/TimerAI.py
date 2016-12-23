"""
  
  Filename: TimerAI.py
  Created by: blach (19Oct14)
  
"""

from direct.interval.IntervalGlobal import Sequence, Wait, Func

class TimerAI:
	
	def __init__(self):
		try:
			self.TimerAI_initialized
			return
		except:
			self.TimerAI_initialized = 1
		self.time = 0
		self.initTime = 0
		self.zeroCommand = None
		self.timerSeq = None
		return
		
	def setInitialTime(self, initTime):
		self.initTime = initTime
		
	def getInitialTime(self):
		return self.initTime
		
	def setZeroCommand(self, command):
		self.zeroCommand = command
		
	def getZeroCommand(self):
		return self.zeroCommand
		
	def b_setTimerTime(self, time):
		self.time = time
		self.d_setTimerTime(time)
		
	def startTiming(self):
		seq = Sequence()
		for second in range(self.initTime):
			seq.append(Func(self.b_setTimerTime, self.initTime - second))
			seq.append(Wait(1.0))
		if self.zeroCommand != None:
			seq.append(Func(self.zeroCommand))
		seq.start()
		self.timerSeq = seq
		
	def stopTiming(self):
		if self.timerSeq:
			self.timerSeq.pause()
			self.timerSeq = None
			
	def disable(self):
		self.stopTiming()
		self.time = None
		self.initTime = None
		self.zeroCommand = None
		self.timerSeq = None
		return
