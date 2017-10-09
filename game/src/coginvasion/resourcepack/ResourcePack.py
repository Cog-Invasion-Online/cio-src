"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ResourcePack.py
@author Maverick Liberty
@date 27-09-17

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from EnvironmentConfiguration import EnvironmentConfiguration
from EnvironmentConfiguration import Modifier
from EnvironmentConfiguration import stringList, stringValue, anyValue

from yaml import load

class ResourcePack(EnvironmentConfiguration):
    notify = directNotify.newCategory('ResourcePack')
    
    ConfigModifiers = {
        'name' : [Modifier(stringValue), 'name'],
        'author' : [Modifier(stringValue), 'authors'],
        'authors' : [Modifier(stringList), 'authors'],
        'version' : [Modifier(anyValue), 'version'] 
    }
    
    def __init__(self, path):
        EnvironmentConfiguration.__init__(self, configPath = (path + '/pack.yaml'), section = 'environment')
        self.name = None
        self.authors = []
        self.version = None
        self.path = path
        
    def digest(self):
        """ Returns true/false depending on if the resource pack can be loaded or not """
        with open(self.configPath, 'r') as stream:
            data = load(stream)
            EnvironmentConfiguration.processData(self, data)
            
            for key in data:
                if not isinstance(data[key], dict) and key in self.ConfigModifiers.keys():
                    entry = self.ConfigModifiers.get(key)
                    modifier = entry[0]
                    
                    returnedData = modifier.digest(data[key])
                    
                    if key == 'author':
                        self.authors.append(returnedData)
                    else:
                        setattr(self, entry[1], returnedData)
                elif key != 'environment':
                    self.notify.warning('Unexpected key %s was found.' % key)
                    
            if not self.name or not self.version:
                self.notify.warning('Must have a name and a version defined in its descriptor file.')
                return False
            return True
