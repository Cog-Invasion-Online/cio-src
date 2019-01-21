"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Setting.py
@author Maverick Liberty
@date January 20, 2019

"""

DATATYPE_TUPLE = tuple
DATATYPE_INT = int
DATATYPE_STR = unicode
DATATYPE_BOOL = bool
DATATYPE_FLOAT = float

SHOWBASE_PREINIT = 0
SHOWBASE_POSTINIT = 1

def getVariants(datatype):
    
    if datatype == DATATYPE_STR:
        return (unicode, str)
    
    return (datatype)
    

class Setting(object):
    
    def __init__(self, manager, name, optionType, default, callback, sunrise, options, description):
        self.name = name
        self._manager = manager
        self.type = optionType
        self.default = default
        self.callback = callback
        self.value = default
        
        # This is when this setting starts taking effect.
        self.sunrise = sunrise
        
        self.options = ["Off", "On"] if options is None and self.type == DATATYPE_BOOL else options
        self.description = description
        
    def __setattr__(self, name, value):
        if name == 'value':
            if hasattr(self, 'value'):
                self.setValue(value)
            else:
                self.__dict__['value'] = value
        else:
            return object.__setattr__(self, name, value)
    
    def setValue(self, value, andCallback = True):
        """ Attempts to set the value of this Setting """
        
        # This is what this setting is currently set to.
        current = self.value
        
        if isinstance(value, getVariants(self.type)):
            # We must update the value attribute like this to avoid
            # recursion if this method was called from our customized
            # __setattr_ function.
            self.__dict__['value'] = value
            
            if andCallback and self.callback:
                # Let's call our callback function if it exists.
                self.callback(value)
            
            try:
                # Let's send out a messenger event to those listening to
                # when this setting changes. This will pass the new value
                # and the previous value.
                messenger.send(self.getEventName(), sentArgs = [value, current])
            except: pass
        else:
            raise ValueError("%s expects a value of type %s, instead it was given a %s."
                             .format(self.name, 
                                     self.type.__class__.__name__, 
                                     value.__class.__name__))
    
    def getValue(self):
        """ Fetches the current value of this Setting """
        return self.value
    
    def getDefault(self):
        """ Fetches the default value of this Setting """
        return self.default
    
    def getCallback(self):
        """ Fetches the callback function of this Setting """
        return self.callback
    
    def getSunrise(self):
        """ Fetches whenever the setting should take effect """
        return self.sunrise
    
    def getOptions(self):
        """ Fetches the options that should be displayed in the book """
        return self.options
    
    def getDescription(self):
        """ Fetches the description of this Setting """
        return self.description
    
    def getEventName(self):
        return "%s-Changed".format(self.name)
