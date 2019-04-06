"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SkyUtil.py
@author Brian Lach
@date July ??, 2014

"""

from panda3d.core import Vec3
from panda3d.bsp import BSPFaceAttrib

from direct.directnotify.DirectNotifyGlobal import directNotify

class SkyUtil:
    
    notify = directNotify.newCategory("SkyUtil")
    
    def __init__(self):
        self.prepared = False
    
    def prepareSky(self, sky):
        if not self.prepared:
            sky.setAttrib(BSPFaceAttrib.makeIgnorePvs(), 1)
            sky.setLightOff(1)
            sky.setFogOff(1)
            #sky.setBin("background", 0)
            #sky.setDepthWrite(False)
            sky.setScale(6)
            if not sky.find('**/cloud1').isEmpty() and not sky.find('**/cloud2').isEmpty():
                sky.find('**/cloud1').setScale(0.6)
                sky.find('**/cloud2').setScale(0.9)
                sky.find('**/cloud1').flattenStrong()
                sky.find('**/cloud2').flattenStrong()
                self.cloud1_int = sky.find('**/cloud1').hprInterval(360, Vec3(60, 0, 0))
                self.cloud2_int = sky.find('**/cloud2').hprInterval(360, Vec3(-60, 0, 0))
            else:
                sky.clearModelNodes()
                sky.flattenStrong()
            self.prepared = True
    
    def startSky(self, sky):
        self.prepareSky(sky)
        if hasattr(self, 'cloud1_int'):
            self.cloud1_int.loop()
            self.cloud2_int.loop()
            
    def stopSky(self):
        if hasattr(self, 'cloud1_int'):
            self.cloud1_int.finish()
            self.cloud2_int.finish()
        
    def pauseSky(self):
        if hasattr(self, 'cloud1_int'):
            self.cloud1_int.pause()
            self.cloud2_int.pause()

    def cleanup(self):
        if hasattr(self, 'cloud1_int'):
            del self.cloud1_int
        if hasattr(self, 'cloud2_int'):
            del self.cloud2_int
        del self.prepared
