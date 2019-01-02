class Schedule:
    
    def __init__(self, tasks = [], interruptMask = 0):
        self.tasks = tasks
        self.interruptMask = 0
        self.currentTask = 0
        
    def think(self):
        