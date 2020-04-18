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

from panda3d.core import OmniBoundingVolume, NodePathCollection, CardMaker, Point2, NodePath, TextNode
from libpandabsp import BSPMaterial, BSPFaceAttrib

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
    
    # Always render if it's a BSP level, even if outside of PVS
    scene.setAttrib(BSPFaceAttrib.makeIgnorePvs(), 1)
    
    try:
        scene.premungeScene(base.win.getGsg())
        scene.prepareScene(base.win.getGsg())
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.syncFrame()
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
        print "precacheScene failed"
        
    scene.clearAttrib(BSPFaceAttrib)

    return rHidden
    
def precacheAnimation(actor, anim):
    actor.play(anim)
    base.graphicsEngine.renderFrame()
    base.graphicsEngine.renderFrame()
    base.graphicsEngine.syncFrame()
    
def precacheActor(actor):
    #print "precacheActor:", actor
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
    snd = loader.loadSfx(path)
    if snd:
        snd.play()
        snd.stop()

def __renderQuad(mat = None, tex = None):
    # Build a simple quad that uses the material
    cm = CardMaker('materialCard')
    cm.setFrame(-1, 1, -1, 1)
    cm.setHasUvs(True)
    cm.setUvRange(Point2(0, 0), Point2(1, 1))
    cardNp = NodePath(cm.generate())

    if mat:
        cardNp.setBSPMaterial(mat, 1)
    elif tex:
        cardNp.setTexture(tex, 1)

    # Render it!
    precacheScene(cardNp)

    cardNp.removeNode()
    
def precacheMaterial(path):
    mat = BSPMaterial.getFromFile(path)
    if not mat:
        return
    __renderQuad(mat = mat)

def precacheTexture(path):
    tex = loader.loadTexture(path)
    __renderQuad(tex = tex)
    
def precacheFont(path):
    if isinstance(path, str):
        font = loader.loadFont(path)
    else:
        font = path
    tn = TextNode('tn')
    tn.setText("The quick brown fox jumps over the lazy dog.")
    tn.setFont(font)
    gnnp = NodePath(tn.generate())
    precacheScene(gnnp)
    gnnp.removeNode()
    
def precacheOther(classname, importPath):
    exec("from %s import %s" % (importPath, classname))
    exec("%s.precache()" % classname)
