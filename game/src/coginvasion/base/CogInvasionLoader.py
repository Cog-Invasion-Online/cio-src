"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CogInvasionLoader.py
@author Brian Lach
@date November 28, 2014

"""

from direct.showbase import Loader
from direct.directnotify.DirectNotifyGlobal import directNotify

from panda3d.core import Multifile, Filename, VirtualFileSystem, TransparencyAttrib, GeomNode, getModelPath

from src.coginvasion.gui.CIProgressScreen import CIProgressScreen
from src.coginvasion.resourcepack.EnvironmentConfiguration import EnvironmentConfiguration
from src.coginvasion.resourcepack.ResourcePack import ResourcePack
from src.coginvasion.dna.DNALoader import loadDNAFile
from src.coginvasion.globals import CIGlobals
from src.coginvasion.toon import ParticleLoader

import os
import io

class CogInvasionLoader(Loader.Loader):
    notify = directNotify.newCategory('CogInvasionLoader')
    TickPeriod = 0.0

    Phases = ['phase_3', 'phase_3.5', 'phase_4', 'phase_5', 'phase_5.5', 'phase_6', 'phase_7',
              'phase_8', 'phase_9', 'phase_10', 'phase_11', 'phase_12', 'phase_13', 'phase_14',
              'phase_0']

    LegalResourcePackExtensions = ['jpg', 'jpeg', 'png', 'ogg', 'rgb', 'mid', 'midi', 'wav', 'mat']

    def __init__(self, base):
        Loader.Loader.__init__(self, base)
        self.inBulkBlock = None
        self.blockName = None
        self.progressScreen = None
        self.wantAutoTick = False
        self.envConfig = None
        self.envConfigStream = None
        self.resourcePack = None
        return

    def mountMultifile(self, mfFile):
        vfs = VirtualFileSystem.getGlobalPtr()
        vfs.mount(mfFile, ".", VirtualFileSystem.MFReadOnly)

    def mountMultifiles(self, resourcePackName = None):
        rsPackPath = None if not resourcePackName else 'resourcepacks/' + resourcePackName

        # This boolean flag is set false if pack.yaml is not found.
        allowResourcePackLoad = True

        if rsPackPath and os.path.exists(rsPackPath):
            if not os.path.exists(rsPackPath + '/pack.yaml'):
                self.notify.warning('You must have a \'pack.yaml\' configuration in the directory of your resource pack to use it.')
                allowResourcePackLoad = False
            else:
                self.resourcePack = ResourcePack(rsPackPath)
                allowResourcePackLoad = self.resourcePack.digest()

                if allowResourcePackLoad:
                    author = '' if len(self.resourcePack.authors) == 0 else self.resourcePack.authors[0]
                    self.notify.info('Loading Resource Pack %s [%s] by %s...' % (self.resourcePack.name,
                        self.resourcePack.version, author))

                    self.envConfig = self.resourcePack
                    self.notify.info('Using Resource Pack Environment Configuration.')

        # This is a boolean flag that stores if we let the user know that a resource
        # pack directory was not found.
        warnedOfMissingPack = False

        vfs = VirtualFileSystem.getGlobalPtr()

        for phase in self.Phases:
            mf = Multifile()
            mf.setEncryptionPassword(metadata.RESOURCE_ENCRYPTION_PASSWORD)
            mf.openReadWrite(Filename(metadata.PHASE_DIRECTORY + phase + '.mf'))

            # Let's handle the mounting of certain file types from resource packs.
            rsPackMf = None
            loadedRsPackMf = False

            if allowResourcePackLoad:
                if rsPackPath and os.path.exists(rsPackPath):
                    rsPhasePath = '%s/%s.mf' % (rsPackPath, phase)
                    if os.path.exists(rsPhasePath):
                        # This is the phase that exists within the resource pack.
                        rsPackMf = Multifile()
                        rsPackMf.openReadWrite(Filename(rsPhasePath))

                        # Let's remove the unneeded files from the default multifile for this phase.
                        for subFile in mf.getSubfileNames():
                            ext = os.path.splitext(subFile)[1][1:]

                            # This code removes files that are overwritten by the resource pack.
                            if ext in self.LegalResourcePackExtensions and subFile in rsPackMf.getSubfileNames():
                                mf.removeSubfile(subFile)

                            # This code removes illegal files inside of the resource pack multifile.
                            elif not ext in self.LegalResourcePackExtensions and subFile in rsPackMf.getSubfileNames():
                                rsPackMf.removeSubfile(subFile)

                        # Let's flag that we've loaded a resource pack multifile.
                        loadedRsPackMf = True
                elif rsPackPath and not os.path.exists(rsPackPath) and not warnedOfMissingPack:
                    self.notify.warning('Desired resource pack could not be found in the \'resourcepacks\' directory.')
                    warnedOfMissingPack = True
            vfs.mount(mf, '.', 0)

            if loadedRsPackMf:
                vfs.mount(rsPackMf, '.', 0)
                self.notify.info('Mounted %s from resource pack.' % phase)
            else:
                self.notify.info('Mounted %s from default.' % phase)

                if phase == 'phase_3':
                    self.notify.info('Loading Default Environment Configuration...')

                    environmentFilename = Filename("phase_3/etc/environment.yaml")
                    if not vfs.resolveFilename(environmentFilename, getModelPath().getValue()):
                        self.notify.error("Could not find environment config file " + environmentFilename.getFullpath() + " on model-path " + getModelPath().getValue())
                    else:
                        # Make an IO stream to the environment.yaml file.
                        self.envConfigStream = io.BytesIO(vfs.readFile(environmentFilename, False))

                        # Create a new EnvironmentConfiguration object and read the data.
                        self.envConfig = EnvironmentConfiguration(self.envConfigStream)
                        self.envConfig.digest()

                        # Now, close out the stream.
                        self.envConfigStream.close()
                        self.envConfigStream = None

                        self.notify.info('Environment Configuration load complete!')

        self.progressScreen = CIProgressScreen()
        self.notify.info('All phases loaded! Ready to play!')

    def beginBulkLoad(self, name, hood, range, wantGui = 1, autoTick = True):
        self.wantAutoTick = autoTick
        self._loadStartT = globalClock.getRealTime()
        if self.inBulkBlock:
            self.notify.warning("tried to start a block ('%s'), but we're already in block ('%s')" % (name, self.blockName))
            return None
        self.inBulkBlock = 1
        self._lastTickT = globalClock.getRealTime()
        self.blockName = name
        self.progressScreen.begin(hood, range, wantGui)
        base.renderFrames()
        return None

    def endBulkLoad(self, name):
        if not self.inBulkBlock:
            self.notify.warning("attempted to end block ('%s'), but we're not in any block." % (name))
            return None
        if name != self.blockName:
            self.notify.warning("attempted to end block ('%s'), other than the current one ('%s')" % (name, self.blockName))
            return None
        self.inBulkBlock = None
        self.wantAutoTick = False
        self.progressScreen.end()
        base.renderFrames()
        return

    def tick(self):
        if self.inBulkBlock:
            self.progressScreen.tick()
            try:
                base.cr.considerHeartbeat()
            except:
                pass

    def loadDNAFile(self, dnaStore, filename):
        return loadDNAFile(dnaStore, filename)

    def loadModel(self, *args, **kw):
        ret = Loader.Loader.loadModel(self, *args, **kw)
        CIGlobals.fixGrayscaleTextures(ret)

        self.tick()
        return ret

    def loadFont(self, *args, **kw):
        ret = Loader.Loader.loadFont(self, *args, **kw)
        self.tick()
        return ret

    def loadTexture(self, texturePath, alphaPath = None, okMissing = False):
        ret = Loader.Loader.loadTexture(self, texturePath, alphaPath, okMissing=okMissing)
        self.tick()
        if alphaPath:
            self.tick()
        return ret

    def loadSfx(self, soundPath):
        ret = Loader.Loader.loadSfx(self, soundPath)
        self.tick()
        return ret

    def loadMusic(self, soundPath):
        ret = Loader.Loader.loadMusic(self, soundPath)
        self.tick()
        return ret

    def loadParticleEffect(self, ptfPath):
        return ParticleLoader.loadParticleEffect(ptfPath)

    def destroy(self):
        Loader.Loader.destroy(self)
        try:
            self.progressScreen.destroy()
            del self.progressScreen
        except:
            pass
