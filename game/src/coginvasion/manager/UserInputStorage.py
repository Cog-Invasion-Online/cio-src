"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file UserInputStorage.py
@author Maverick Liberty
@date September 23, 2017

"""

import inspect

class Control(object):
    
    def __init__(self, default, alternatives = []):
        self.default = default
        self.alternatives = alternatives
        self.current = default
        
    def __str__(self):
        altsStr = ''
        
        for i in xrange(0, len(self.alternatives)):
            ctrl = self.alternatives[i]
            altsStr += ctrl
            
            if i < len(self.alternatives) - 1:
                altsStr += ','
        
        return 'Default Key: %s, Current Key: %s, Alternatives: [%s]' % (self.default, 
            self.current, self.alternatives)

class UserInputStorage(object):
    
    ViewQuests = Control('z')
    LastGag = Control('q')
    UseGag = Control('mouse1', alternatives = ['f'])
    PrimaryFire = Control('mouse1')
    SecondaryFire = Control('mouse3')
    Reload = Control('r')
    ToggleLoadoutVisibility = Control('e')
    #PreviousTrackGag = Control('z')
    #NextTrackGag = Control('c')
    ToggleGTAControls = Control('escape')
    TakeScreenshot = Control('f9')
    ToggleAspect2D = Control('f2')
    PreviousBookPage = Control('arrow_left')
    NextBookPage = Control('arrow_right')
    PreviousCameraPosition = Control('shift-tab')
    NextCameraPosition = Control('tab')
    LookUp = Control('page_up')
    LookDown = Control('page_down')
    Interact = Control('x')
    Chat = Control('t')
    MoveForward = Control('w')
    MoveBackward = Control('s')
    StrafeLeft = Control('a')
    StrafeRight = Control('d')
    
    # Returns the default control for an action.
    def getDefault(self, ctrl):
        ctrlClass = object.__getattribute__(self, ctrl)
        return ctrlClass.default
    
    # Returns the alternative controls for an action.
    def getAlternatives(self, ctrl):
        ctrlClass = object.__getattribute__(self, ctrl)
        return ctrlClass.alternatives
    
    # Returns the control options for an action.
    # Begins with the default option followed by the alternatives.
    def getControlOptions(self, ctrl):
        alts = self.getAlternatives(ctrl)[:]
        alts.insert(0, self.getDefault(ctrl))
        return alts
    
    # Used to update the current control used to execute an action.
    # Pass the control name as a string followed by the new input.
    def updateControl(self, ctrl, newInput):
        ctrlClass = object.__getattribute__(self, ctrl)
        ctrlClass.current = newInput
        
    def __getattribute__(self, name):
        if hasattr(self, name):
            obj = object.__getattribute__(self, name)
            if isinstance(obj, Control):
                return obj.current
            return obj
        
    def getControls(self):
        attributes = inspect.getmembers(UserInputStorage, lambda a:not(inspect.isroutine(a)))
        controls = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
        return controls
