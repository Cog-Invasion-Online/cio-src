from panda3d.core import loadPrcFile
loadPrcFile('config/config_client.prc')

from direct.showbase.ShowBase import ShowBase
base = ShowBase()
from direct.showbase.DirectObject import DirectObject

class A(DirectObject):
    
    def __init__(self):
        self.accept('the_event', self._handleTheEvent)
        
    def _handleTheEvent(self):
        print 'A handled the event!'

a = A()
b = A()
b.ignore('the_event')

messenger.send('the_event')

base.run()
