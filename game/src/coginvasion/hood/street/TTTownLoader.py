"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TTTownLoader.py
@author Brian Lach
@date July 25, 2015

"""

from panda3d.core import TextureStage
from panda3d.bsp import BSPMaterialAttrib

import TownLoader
import TTStreet

from src.coginvasion.globals import CIGlobals

class TTTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TTStreet.TTStreet
        self.streetSong = 'TC_SZ'
        self.interiorSong = 'TC_SZ_activity'
        self.townStorageDNAFile = 'phase_5/dna/storage_TT_town.pdna'
        
        self.brokeShadows = []
        self.shadows = []
        
        self.brokeShadowsOff = True
        
        base.localAvatar.accept('i', self.toggleShadows)
        
    def toggleShadows(self):
        self.brokeShadowsOff = not self.brokeShadowsOff
        shadow = self.shadows if self.brokeShadowsOff else self.brokeShadows
        
        for shadow in self.shadows:
            if self.brokeShadowsOff:
                shadow.show()
            else:
                shadow.hide()
                print 'Hid fixed shadow'
                
            print 'Manual Inserted Shadow Data: '
            
            geomNodes = shadow.findAllMatches('**/+GeomNode')
            for nodepath in geomNodes:
                geomNode = nodepath.node()
                for i in xrange(geomNode.getNumGeoms()):
                    geom = geomNode.getGeom(i)
                    state = geomNode.getGeomState(i)
                
        for shadow in self.brokeShadows:
            if self.brokeShadowsOff:
                shadow.hide()
                print 'Hid broken shadow'
            else:
                shadow.show()
                
            print 'Broken Shadow Data: '
            
            geomNodes = shadow.findAllMatches('**/+GeomNode')
            for nodepath in geomNodes:
                geomNode = nodepath.node()
                for i in xrange(geomNode.getNumGeoms()):
                    geom = geomNode.getGeom(i)
                    state = geomNode.getGeomState(i)
                        

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_5/dna/toontown_central_' + zone4File + '.pdna'
        self.createHood(dnaFile)
        
        print 'Printing tree shit:'
        for obj in render.getChildren():
            if obj and not obj.isEmpty():
                shadows = obj.findAllMatches('**/*shadow*')
                
                self.colorChildren(obj)
                
    def colorChildren(self, parent):
        import random
        for child in parent.getChildren():
            if child and not child.isEmpty():
                color = (random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), 1.0)
                
                
                geomNodes = child.findAllMatches('**/+GeomNode')
                for nodepath in geomNodes:
                    geomNode = nodepath.node()
                    hasTreeTex = False
                    for i in xrange(geomNode.getNumGeoms()):
                        geom = geomNode.getGeom(i)
                        state = geomNode.getGeomState(i)
                        
                        if state.hasAttrib(BSPMaterialAttrib):
                            attrib = state.getAttrib(BSPMaterialAttrib)
                            mat = attrib.getMaterial()
                            
                            if mat:
                                texture = mat.getKeyvalue("$basetexture")
                                print 'Texture: ' + str(texture)
                                
                                if 'drop-shadow' in texture:
                                    nodepath.hide()
                                    self.brokeShadows.append(nodepath)
                                    fixedShadow = loader.loadModel('phase_3/models/props/drop_shadow.bam')
                                    fixedShadow.wrtReparentTo(child)
                                    fixedShadow.setScale(child.getScale())
                                    fixedShadow.setPos(child.getPos(render))
                                    self.shadows.append(fixedShadow)
                                    nodepath.setColorScale(color, 1)
                                    
                                    print 'Colored Child: {0} with: {1}'.format(child.getName(), str(color))
                
                self.colorChildren(child)

        #streetNormal = TextureStage('TTStreetNormal')
        #streetNormal.setMode(TextureStage.MNormal)
        #normalTex = loader.loadTexture("phase_3.5/maps/cobblestone_normal.jpg")
        #for street in self.geom.findAllMatches("**/*street_*_street*"):
        #    print "Applying normal texture to", street.getName()
        #    street.setTexture(streetNormal, normalTex)

    def unload(self):
        TownLoader.TownLoader.unload(self)
