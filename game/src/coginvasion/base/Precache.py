"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Precache.py
@author Brian Lach
@date January 05, 2019

@desc Functions to `precache` assets, aka load into memory and
      pre-render them so when they actually show up in game
      there is little to no chug.
"""

from panda3d.core import OmniBoundingVolume, NodePathCollection
from panda3d.bsp import BSPMaterial

class Precacheable(object):
    
    Precached = False
        
    @classmethod
    def precache(cls):
        if not cls.Precached:
            cls.doPrecache()
            cls.Precached = True
    
    @classmethod
    def doPrecache(cls):
        pass

def precacheScene(scene, reset = True):
    if reset:
        oldp = scene.getParent()

    rHidden = False
    if render.isHidden():
        rHidden = True
        render.show()
        
    stashed = NodePathCollection()
    for np in scene.findAllMatches("**;+s"):
        if np.isStashed():
            stashed.addPath(np)
            np.unstash()
        
    if not scene.isAncestorOf(render):
        # if it's parented to camera,
        # camera will always see it
        scene.reparentTo(render) 
                             
    # this says that the scene takes up infinite space,
    # making it always intersect the view frustum,
    # guaranteed to be rendered
    scene.node().setBounds(OmniBoundingVolume())
    scene.node().setFinal(1)
    
    try:
        scene.premungeScene(base.win.getGsg())
        scene.prepareScene(base.win.getGsg())
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.syncFrame()
        base.audio3d.update()
        base.musicManager.update()
        
        if reset:
            scene.node().setFinal(0)
            scene.node().clearBounds()
            
            scene.reparentTo(oldp)
    
            if rHidden:
                render.hide()
        
        # restash
        for np in stashed:
            np.stash()
    except:
        # The program might have exited prematurely.
        # This will prevent the game from yelling at us.
        pass

    return rHidden
    
def precacheAnimation(actor, anim):
    actor.play(anim)
    base.graphicsEngine.renderFrame()
    base.graphicsEngine.syncFrame()
    
def precacheActor(actor):
    if isinstance(actor, list) or isinstance(actor, tuple):
        # Actor was supplied as a model path and animation dictionary
        from direct.actor.Actor import Actor
        actor = Actor(actor[0], actor[1])
        
    oldp = actor.getParent()
    
    rHidden = precacheScene(actor, False)
    for anim in actor.getAnimNames():
        precacheAnimation(actor, anim)
        
    actor.stop()
    
    actor.node().setFinal(0)
    actor.node().clearBounds()
    actor.reparentTo(oldp)
    if rHidden:
        render.show()

def precacheModel(path):
    mdl = loader.loadModel(path)
    precacheScene(mdl)
    mdl.removeNode()
    
def precacheSound(path):
    loader.loadSfx(path)
    
def precacheMaterial(path):
    BSPMaterial.getFromFile(path)
    
def precacheTexture(path):
    loader.loadTexture(path)
