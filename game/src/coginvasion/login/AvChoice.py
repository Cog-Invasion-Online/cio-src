"""
  
  Filename: AvChoice.py
  Created by: blach (28Nov14)
  
"""

class AvChoice:
    
    def __init__(self, dna, name, slot, avId, lastHood):
        self.setDNA(dna)
        self.setName(name)
        self.setSlot(slot)
        self.setAvId(avId)
        self.setLastHood(lastHood)
        
    def setDNA(self, dna):
        self.dna = dna
        
    def getDNA(self):
        return self.dna
        
    def setLastHood(self, hood):
        self.lastHood = hood
        
    def getLastHood(self):
        return self.lastHood
        
    def setName(self, name):
        self.name = name
        
    def getName(self):
        return self.name
        
    def setSlot(self, slot):
        self.slot = slot
        
    def getSlot(self):
        return self.slot
        
    def setAvId(self, avId):
        self.avId = avId
        
    def getAvId(self):
        return self.avId
        
    def cleanup(self):
        del self.dna
        del self.slot
        del self.name
        del self.avId
        del self.lastHood
