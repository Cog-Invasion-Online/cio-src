from direct.showbase.DirectObject import DirectObject

class Useable:
    
    def __init__(self):
        self.useIval = 0.09
        self.using = False
        
    def stopUse(self):
        self.using = False
        
    def use(self):
        pass
        
    def startUse(self):
        self.using = True
        
    def canUse(self):
        return True