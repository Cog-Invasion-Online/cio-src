from direct.stdpy import threading
from direct.directnotify.DirectNotifyGlobal import directNotify

from libpandadna import *

DNANotify = directNotify.newCategory('DNALoader')

class DNABulkLoader:
    
    notify = directNotify.newCategory('DNABulkLoader')
    
    def __init__(self, storage, files):
        self.dnaStorage = storage
        self.dnaFiles = files

    def loadDNAFiles(self):
        for dnaFile in self.dnaFiles:
            self.notify.info('Reading DNA file...', dnaFile)
            loadDNABulk(self.dnaStorage, dnaFile)
        del self.dnaStorage
        del self.dnaFiles

def loadDNABulk(dnaStorage, dnaFile):
    dnaLoader = DNALoader()
    dnaLoader.loadDNAFile(dnaStorage, dnaFile)

def loadDNAFile(dnaStorage, dnaFile):
    DNANotify.info('Reading DNA file...', dnaFile)
    dnaLoader = DNALoader()
    node = dnaLoader.loadDNAFile(dnaStorage, dnaFile)
    if not node.isEmpty():
        if node.node().getNumChildren() > 0:
            return node.node()
    return None

def loadDNAFileAI(dnaStorage, dnaFile):
    dnaLoader = DNALoader()
    data = dnaLoader.loadDNAFileAI(dnaStorage, dnaFile)
    return data
