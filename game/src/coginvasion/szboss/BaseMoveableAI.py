from direct.fsm.FSM import FSM

class BaseMoveable(FSM):

    Start = 0
    StartToEnd = 1
    End = 2
    EndToStart = 3

    def __init__(self):
        FSM.__init__(self, 'BaseMoveableAI')
        self.state = self.Start
        self.wait = 0.0
        self.moveDuration = 0.0
        
    def 