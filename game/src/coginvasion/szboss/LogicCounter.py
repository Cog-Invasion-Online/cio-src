from Entity import Entity

class LogicCounter(Entity):

    def __init__(self, air = None, dispatch = None):
        Entity.__init__(self)
        self.startVal = 0
        self.maxVal = 1
        self.minVal = 0
        self.val = 0
        
    def cleanup(self):
        self.startVal = None
        self.maxVal = None
        self.minVal = None
        self.val = None
        Entity.cleanup(self)
        
    def CountUp(self):
        print "CountUp"
        
        if self.val == self.maxVal:
            return
            
        oldVal = self.val
        self.val += 1
        if oldVal == self.minVal:
            self.dispatchOutput("OnLoseMin")
            print "Lost min"
        if self.val == self.maxVal:
            self.dispatchOutput("OnHitMax")
            print "hit max"
        
    def CountDown(self):
        print "CountDown"
        
        if self.val == self.minVal:
            return
            
        oldVal = self.val
        self.val -= 1
        if oldVal == self.maxVal:
            self.dispatchOutput("OnLoseMax")
            print "lost max"
        if self.val == self.minVal:
            self.dispatchOutput("OnHitMin")
            print "hit min"
        
    def load(self):
        self.cEntity = self.bspLoader.getCEntity(self.entnum)
        Entity.load(self)
        self.startVal = self.bspLoader.getEntityValueInt(self.entnum, "startVal")
        self.maxVal = self.bspLoader.getEntityValueInt(self.entnum, "maxVal")
        self.minVal = self.bspLoader.getEntityValueInt(self.entnum, "minVal")
        
        self.val = self.startVal
        
        print "Load logic_counter"