from DistributedEntity import DistributedEntity

from direct.fsm.FSM import FSM

from src.coginvasion.phys import PhysicsUtils

class DistributedGenerator(DistributedEntity, FSM):
    
    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        FSM.__init__(self, 'DGenerator')
        self.state = 0
        self.runSound = None
        self.powerDownSound = None
        self.powerUpSound = None
        
    def enterPoweringOn(self):
        self.powerUpSound.play()
        
    def exitPoweringOn(self):
        self.powerUpSound.stop()
        
    def enterPowerOn(self):
        self.runSound.play()
        
    def exitPowerOn(self):
        self.runSound.stop()
        
    def enterPoweringOff(self):
        self.powerDownSound.play()
        
    def exitPoweringOff(self):
        self.powerDownSound.stop()
        
    def load(self):
        DistributedEntity.load(self)
        self.powerUpSound = base.loadSfxOnNode("phase_14/audio/sfx/sewer_generator_windup.ogg", self.cEntity.getModelNp())
        self.powerDownSound = base.loadSfxOnNode("phase_14/audio/sfx/sewer_generator_winddown.ogg", self.cEntity.getModelNp())
        self.runSound = base.loadSfxOnNode("phase_14/audio/sfx/sewer_generator_hum.ogg", self.cEntity.getModelNp())
        self.runSound.setLoop(True)
        base.materialData.update(PhysicsUtils.makeBulletCollFromGeoms(self.cEntity.getModelNp()))
        
    def setState(self, state):
        self.state = state
        if state == 0:
            self.request('PowerOn')
        elif state == 1:
            self.request('PowerOff')
        elif state == 2:
            self.request('PoweringOn')
        elif state == 3:
            self.request('PoweringOff')
            
    def disable(self):
        self.request('Off')
        self.state = None
        self.runSound = None
        self.powerDownSound = None
        self.powerUpSound = None
        DistributedEntity.disable(self)