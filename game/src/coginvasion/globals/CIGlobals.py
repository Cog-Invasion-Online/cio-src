"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CIGlobals.py
@author Brian Lach
@date June 17, 2014
@desc This is a file containing generic global variables and methods that don't fit into
any specific package's globals file.

Where to find moved globals:
    - Zone Globals: src.coginvasion.hood -> ZoneUtil.py
    - Gag Globals: src.coginvasion.gags -> GagGlobals.py
    - Disney Character NPC Globals: src.coginvasion.npc -> DisneyCharGlobals.py
    - NPC Globals/Dialogue: src.coginvasion.npc -> NPCGlobals.py
"""

from panda3d.core import BitMask32, LPoint3f, Point3, VirtualFileSystem, ConfigVariableBool, Fog, OmniBoundingVolume
from panda3d.core import Material, PNMImage, Texture, AmbientLight, PointLight, Spotlight, DirectionalLight
from panda3d.core import TextureStage, VBase4, TransparencyAttrib, Vec3, deg2Rad, Point2, DecalEffect, ModelNode, rad2Deg, Vec2

from direct.interval.IntervalGlobal import Sequence, Func, LerpScaleInterval, Wait, Parallel, SoundInterval, ActorInterval

import math

RotateCutOff = 65.0 # for remote avatars only, local avatar uses WalkCutOff
StrafeCutOff = 2.0
WalkCutOff = 0.5
RunCutOff = 8.0
STAND_INDEX = 0
WALK_INDEX = 1
RUN_INDEX = 2
REVERSE_INDEX = 3
STRAFE_RIGHT_INDEX = 4
STRAFE_LEFT_INDEX = 5
GeneralAnimPlayRate = 1.0
BackwardsAnimPlayRate = -1.0
OpenBookFromFrame = 29
OpenBookToFrame = 37
ReadBookFromFrame = 38
ReadBookToFrame = 118
CloseBookFromFrame = 119
CloseBookToFrame = 155
ChatBubble = "phase_3/models/props/chatbox.bam"
ThoughtBubble = "phase_3/models/props/chatbox_thought_cutout.bam"
ToonFont = None
SuitFont = None
MickeyFont = None
MinnieFont = None
FloorOffset = 0.025
NPCWalkSpeed = 0.02
NPCRunSpeed = 0.04

# Use this for overriding the chosen FOV with the original Toontown FOV.
OriginalCameraFov = 52.0
OriginalActionFov = 70.0

DefaultCameraFov = 52.0
DefaultCameraFar = 2500.0
DefaultCameraNear = 1.0
PortalScale = 1.5
SPInvalid = 0
SPHidden = 1
SPRender = 2
SPDonaldsBoat = 3
SPDynamic = 5
AICollisionPriority = 10
AICollMovePriority = 8
Suit = "Cog"
Toon = "Toon"
Suits = "Cogs"
Skelesuit = "Skelecog"
RaceGame = "Race Game"
UnoGame = "Uno Game"
UnoCall = "UNO!"
GunGame = "Toon Battle"
GunGameFOV = 70.0
FactoryGame = "Factory Prowl"
CameraShyGame = "Camera Shy"
EagleGame = "Eagle Summit"
DeliveryGame = "Delivery!"
DodgeballGame = "Winter Dodgeball"

MB_Moving = 1
MB_Crouching = 2
MB_Walking = 4

def getDGIForBlob(blob):
    from direct.distributed.PyDatagram import PyDatagram
    from direct.distributed.PyDatagramIterator import PyDatagramIterator
    dg = PyDatagram(blob)
    dgi = PyDatagramIterator(dg)
    return dgi

def extrude(start, scale, direction):
    return start + (direction * scale)

def angleVectors(angles, forward = False, right = False, up = False):
    """
    Get basis vectors for the angles.
    Each vector is optional.
    """

    if forward or right or up:
        sh = math.sin(deg2Rad(angles[0]))
        ch = math.cos(deg2Rad(angles[0]))
        sp = math.sin(deg2Rad(angles[1]))
        cp = math.cos(deg2Rad(angles[1]))
        sr = math.sin(deg2Rad(angles[2]))
        cr = math.cos(deg2Rad(angles[2]))

    result = []
    if forward:
        forward = Vec3(cp*ch,
                       cp*sh,
                       -sp)
        result.append(forward)
    if right:
        right = Vec3(-1*sr*sp*ch+-1*cr*-sh,
                     -1*sr*sp*sh+-1*cr*ch,
                     -1*sr*cp)
        result.append(right)
    if up:
        up = Vec3(cr*sp*ch+-sr*-sh,
                  cr*sp*sh+-sr*ch,
                  cr*cp)
        result.append(up)

    return result

def vecToYaw(vec):
    return rad2Deg(math.atan2(vec[1], vec[0])) - 90

def angleMod(a):
    return a % 360

def angleDiff(destAngle, srcAngle):

    delta = destAngle - srcAngle

    if destAngle > srcAngle:
        if delta >= 180:
            delta -= 360
    else:
        if delta <= -180:
            delta += 360

    return delta

def putVec3(dg, vec):
    from panda3d.direct import STFloat64
    dg.putArg(vec[0], STFloat64)
    dg.putArg(vec[1], STFloat64)
    dg.putArg(vec[2], STFloat64)

def getVec3(dgi):
    from panda3d.direct import STFloat64
    x = dgi.getArg(STFloat64)
    y = dgi.getArg(STFloat64)
    z = dgi.getArg(STFloat64)
    return Vec3(x, y, z)

def remapVal(val, A, B, C, D):
    if A == B:
        return D if val >= B else C
        
    return C + (D - C) * (val - A) / (B - A)
    
def clamp(val, A, B):
    return max(A, min(B, val))

def preRenderScene(np):
    """
    Uploads the entire scene to the graphics card immediately.

    If the specified node is not part of the scene (render),
    it will be temporarily placed in, rendered, then placed back
    where is was before.
    """

    from src.coginvasion.base.Precache import precacheScene
    precacheScene(np)

def replaceDecalEffectsWithDepthOffsetAttrib(node):
    for np in node.findAllMatches("**"):
        if np.hasEffect(DecalEffect.getClassType()):
            np.clearEffect(DecalEffect.getClassType())
            np.setDepthOffset(1)
            
def moveNodes(fromNode, search, node):
    for np in fromNode.findAllMatches("**/" + search):
        np.wrtReparentTo(node)
        
def moveChildren(fromNode, toNode, removeFrom = False):
    for np in fromNode.getChildren():
        np.wrtReparentTo(toNode)
    if removeFrom:
        fromNode.removeNode()
        
def removeDNACodes(node):
    for np in node.findAllMatches("**"):
        np.clearTag("DNACode")
        np.clearTag("DNARoot")
        np.clearTag("cam")
        
def flattenModelNodes(node):
    for np in node.findAllMatches("**"):
        if np.node().isOfType(ModelNode.getClassType()):
            np.flattenStrong()
            
def clearModelNodesBelow(node):
    for np in node.getChildren():
        np.clearModelNodes()

def isAvatar(obj):
    from src.coginvasion.avatar.AvatarShared import AvatarShared
    return isinstance(obj, AvatarShared)

def isDistributed(obj):
    return hasattr(obj, 'doId')

def getMoveIvalFromPath(np, path, speed):
    from direct.interval.IntervalGlobal import Sequence, Func, LerpPosInterval
    moveIval = Sequence()
    for i in xrange(len(path)):
        if i == 0:
            continue
        waypoint = path[i]
        lastWP = path[i - 1]
        moveIval.append(Func(np.headsUp, Point3(*waypoint)))
        ival = LerpPosInterval(np, pos = Point3(*waypoint),
            startPos = Point3(*lastWP),
            fluid = 1,
            duration = (Point2(waypoint[0], waypoint[1]) - Point2(lastWP[0], lastWP[1])).length() / speed)
        moveIval.append(ival)
    return moveIval

def anglesToVector(angles):
    return Vec3(math.cos(deg2Rad(angles[0])) * math.cos(deg2Rad(angles[1])),
                math.sin(deg2Rad(angles[0])) * math.cos(deg2Rad(angles[1])),
                math.sin(deg2Rad(angles[1])))

patterns = ('%s', 'control-%s', 'shift-control-%s', 'alt-%s',
            'control-alt-%s', 'shift-%s', 'shift-alt-%s')

def acceptWithModifiers(acceptor, event, callback = None, extraArgs = []):
    for pattern in patterns:
        acceptor.accept(pattern % event, callback, extraArgs)

def acceptOnceWithModifiers(acceptor, event, callback = None, extraArgs = []):
    for pattern in patterns:
        acceptor.acceptOnce(pattern % event, callback, extraArgs)
    
def ignoreWithModifiers(acceptor, event):
    for pattern in patterns:
        acceptor.ignore(pattern % event)

def doSceneCleanup():
    from panda3d.core import ModelPool, TexturePool, RenderState, RenderAttrib, TransformState, GeomCacheManager

    ModelPool.garbageCollect()
    TexturePool.garbageCollect()
    RenderState.clearMungerCache()
    RenderState.clearCache()
    RenderState.garbageCollect()
    RenderAttrib.garbageCollect()
    TransformState.clearCache()
    TransformState.garbageCollect()
    GeomCacheManager.getGlobalPtr().flush()
        
    base.graphicsEngine.renderFrame()

def lerpWithRatio(v0, v1, ratio):
    dt = globalClock.getDt()
    amt = 1 - math.pow(1 - ratio, dt * 30.0)
    return lerp(v0, v1, amt)

def lerp(v0, v1, amt):
    return v0 * amt + v1 * (1 - amt)

NoGlowTS = None
NoGlowTex = None
def applyNoGlow(np):
    global NoGlowTS
    global NoGlowTex
    if not NoGlowTS:
        NoGlowTS = TextureStage('noglow')
        NoGlowTS.setMode(TextureStage.MGlow)
    if not NoGlowTex:
        NoGlowTex = loader.loadTexture("phase_3/maps/black.png")
    np.setTexture(NoGlowTS, NoGlowTex)

def applyGlow(np, glowTex):
    ts = TextureStage("glow")
    ts.setMode(TextureStage.MGlow)
    np.setTexture(ts, glowTex)

ShadowTexStage = None
ShadowCasters = []
def setShadowTexStage(stage):
    global ShadowTexStage
    global ShadowCasters
    ShadowTexStage = stage
    staleNodes = []
    for node in ShadowCasters:
        if not node.isEmpty():
            node.setTextureOff(stage)
        else:
            staleNodes.append(node)
    for sn in staleNodes:
        ShadowCasters.remove(sn)

def castShadows(node):
    global ShadowCasters
    node.showThrough(ShadowCameraBitmask)
    if ShadowTexStage:
        node.setTextureOff(ShadowTexStage)
    ShadowCasters.append(node)
    
def uncastShadows(node):
    global ShadowCasters
    node.hide(ShadowCameraBitmask)
    ShadowCasters.remove(node)

# Makes sure that this NodePath is okay (not None and not empty).
def isNodePathOk(np):
    return (np is not None and not np.isEmpty())

def makeDropShadow(scale):
    sh = loader.loadModel("phase_3/models/props/drop_shadow.bam")
    sh.setScale(scale)
    sh.setColor(0, 0, 0, 0.5, 1)
    sh.setBillboardAxis(2)
    sh.flattenMedium()
    return sh

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""" String helper methods """

def makeSingular(noun):
    """ Makes a plural noun singular. """
    pluralSuffixes = ['ies', 'es', 's']
    
    for suffix in pluralSuffixes:
        if noun.endswith(suffix):
            return noun[:-len(suffix)]

    return noun

def makePlural(noun):
    """ Makes a noun string plural. Follows grammar rules with nouns ending in 'y' and 's'. Assumes noun is singular beforehand. """
    withoutLast = noun[:-1]
    
    if noun.endswith('y'):
        return '{0}ies'.format(withoutLast)
    elif noun.endswith('s'):
        return '{0}es'.format(withoutLast)
    else:
        return '{0}s'.format(noun)
    
def makePastTense(noun):
    """ Makes a noun string past tense. """    
    withoutLast = noun[:-1]
    secondToLast = noun[-2:]
    lastChar = noun[-1:]

    if noun.endswith('y'):
        return '{0}ied'.format(withoutLast)
    elif not (noun.endswith('w') or noun.endswith('y')) and secondToLast in getVowels() and lastChar in getConsonants():
        # When a noun ends with a vowel then a consonant, we double the consonant and add -ed."
        return '{0}{1}ed'.format(noun, secondToLast)
    else:
        return '{0}ed'.format(noun)
    
def getVowels():
    """ Returns a list of vowels """
    return ['a', 'e', 'i', 'o', 'u']

def getConsonants():
    """ Returns a list of consonants """
    return ['b', 'c', 'd', 'f', 'g', 
            'h', 'j', 'k', 'l', 'm', 
            'n', 'p', 'q', 'r', 's', 
            't', 'v', 'w', 'x', 'y', 
    'z']

def getAmountString(noun, amount):
    """ Returns a grammatically correct string stating the amount of something. E.g: An elephant horn, 5 packages, etc. """
    
    if amount > 1:
        return "{0} {1}".format(amount, makePlural(noun))
    else:
        firstChar = noun[1:]

        if firstChar in getVowels():
            # If the noun begins with a vowel, we use 'an'.
            return 'An {0}'.format(noun)
        
        return 'A {0}'.format(noun)
    
def isEmptyString(string):
    """ Returns whether or not a string is empty. """
    return not (string and string.strip())


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def makeSplat(pos, color, scale, sound = None):
    from direct.actor.Actor import Actor
    from direct.interval.IntervalGlobal import ActorInterval
    from panda3d.core import AudioSound

    splat = Actor("phase_3.5/models/props/splat-mod.bam", {"chan": "phase_3.5/models/props/splat-chan.bam"})
    splat.setBillboardPointEye()
    splat.setScale(scale)
    splat.setColor(color)
    splat.reparentTo(render)
    splat.setPos(pos)
    splat.setLightOff(1)
    splat.setTransparency(TransparencyAttrib.MDual)
    splat.hide(ShadowCameraBitmask)

    if sound:
        if isinstance(sound, str):
            sound = base.audio3d.loadSfx(sound)
        if isinstance(sound, AudioSound):
            base.audio3d.attachSoundToObject(sound, splat)
            sound.play()

    seq = Sequence(ActorInterval(splat, "chan"), Func(splat.cleanup), Func(splat.removeNode))
    seq.start()
    
ParticleRender = None
def getParticleRender():
    global ParticleRender
    if not ParticleRender:
        ParticleRender = render.attachNewNode('particleRender')
        ParticleRender.setLightOff(1)
        ParticleRender.hide(ShadowCameraBitmask)
    return ParticleRender

def makeExplosion(pos = (0, 0, 0), scale = 1, sound = True, shakeCam = True, duration = 1.0, soundVol = 1.0):
    explosion = loader.loadModel('phase_3.5/models/props/explosion.bam')
    explosion.setScale(scale)
    explosion.reparentTo(render)
    explosion.setBillboardPointEye()
    explosion.setLightOff(1)
    explosion.hide(ShadowCameraBitmask)
    explosion.setPos(pos)

    frames = 10.0
    fps = 24.0
    duration = frames / fps
    explosion.find("**/+SequenceNode").node().play()
    
    from src.coginvasion.toon import ParticleLoader
    smoke = ParticleLoader.loadParticleEffect("phase_14/etc/explosion_smoke.ptf")
    smoke.setScale(scale)
    smoke.setPos(pos)
    smoke.start(render, getParticleRender())
    
    track = Parallel()

    if sound:
        import random

        hlsounds = base.config.GetBool('explosion-hlsounds', False)
        if hlsounds:
            hldir = "phase_14/audio/sfx/"
            snd = base.audio3d.loadSfx(hldir + random.choice(['explode3_hl2', 'explode4_hl2', 'explode5_hl2']) + ".ogg")
        else:
            snd = base.audio3d.loadSfx("phase_3.5/audio/sfx/ENC_cogfall_apart.ogg")

        base.audio3d.attachSoundToObject(snd, explosion)
        
        # explosion aftermaths
        debChoice = random.randint(1, 4)
        if debChoice <= 3:
            debris = base.audio3d.loadSfx("phase_14/audio/sfx/debris{0}.ogg".format(debChoice))
        else:
            debris = base.audio3d.loadSfx("phase_4/audio/sfx/MG_crash_whizz.ogg")
        base.audio3d.attachSoundToObject(debris, explosion)
        
        track.append(SoundInterval(snd, volume = soundVol))
        wait = 0.0791 if not hlsounds else 0.0
        track.append(Sequence(Wait(wait), SoundInterval(debris, volume = soundVol)))

    if shakeCam:
        dist = camera.getDistance(explosion)
        maxDist = 100.0 * scale
        maxIntense = 1.4 * scale
        if dist <= maxDist:
            base.doCamShake(maxIntense - (maxIntense * (dist / maxDist)), duration)
    
    track.append(Sequence(Wait(duration), Func(explosion.removeNode)))
    track.append(Sequence(Wait(duration), Func(smoke.softStop)))
    track.start()

def makeDustCloud(pos, scale = (0.1, 0.9, 1), sound = None, color = (1, 1, 1, 1)):
    from direct.actor.Actor import Actor
    dust = Actor('phase_5/models/props/dust-mod.bam', {'chan' : 'phase_5/models/props/dust-chan.bam'})
    dust.hide(ShadowCameraBitmask)
    objBin = 110
    for cloudNum in range(1, 12):
        cloudName = '**/cloud' + str(cloudNum)
        cloud = dust.find(cloudName)
        cloud.setBin('fixed', objBin)
        cloud.setLightOff(1)
        cloud.setColorScale(color, 1)
        objBin -= 10
    dust.setBillboardPointEye()
    dust.setScale(scale)
    dust.reparentTo(render)
    dust.setPos(pos)
    if sound:
        base.audio3d.attachSoundToObject(sound, dust)
        sound.play()
    dustTrack = Sequence(ActorInterval(dust, "chan"), Func(dust.cleanup))
    dustTrack.start()

def getShinyMaterial(shininess = 250.0):
    mat = Material()
    mat.setSpecular((1, 1, 1, 1))
    mat.setShininess(shininess)

    return mat

def getCharacterMaterial(name = "charMat", shininess = 250, rimColor = (1, 1, 1, 1.0), rimWidth = 10,
                         specular = (1, 1, 1, 1), lightwarp = None):#"phase_3/maps/toon_lightwarp.jpg"):
    mat = Material(name)
    mat.setRimColor(rimColor)
    mat.setRimWidth(rimWidth)
    mat.setSpecular(specular)
    mat.setShininess(shininess)
    mat.setShadeModel(Material.SMHalfLambert)
    if lightwarp and hasattr(mat, 'setLightwarpTexture'):
        mat.setLightwarpTexture(loader.loadTexture(lightwarp))
    return mat

SettingsMgr = None

def calcAttackDamage(distance, baseDmg, maxDist = 40.0):
    """Global formula for calculating attack damage."""

    distanceMod = 1 - min(1.0, distance / maxDist)
    ramp = math.sin(math.asin(distanceMod)) + 0.5
    dmg = baseDmg * ramp

    return int(round(max(1.0, dmg)))

def colorFromRGBScalar255(color):
    """Takes in a tuple of (r, g, b, scalar) (0-255) and returns a
    linear (0-1) color with the scalar applied."""
    
    scalar = color[3]
    return VBase4(color[0] * (scalar / 255.0) / 255.0,
                  color[1] * (scalar / 255.0) / 255.0,
                  color[2] * (scalar / 255.0) / 255.0,
                  1.0)

def getSettingsMgr():
    return SettingsMgr

def makeAmbientLight(name, color):
    amb = AmbientLight(name + "-ambient")
    amb.setColor(color)
    ambient = render.attachNewNode(amb)
    return ambient

def makeDirectionalLight(name, color, angle):
    dir = DirectionalLight(name + "-directional")
    dir.setColor(color)
    dir.setDirection(anglesToVector(angle))
    directional = camera.attachNewNode(dir)
    directional.setCompass()
    #if metadata.USE_REAL_SHADOWS:
        #dir.setShadowCaster(True, 1, 1)
        #dir.showFrustum()
        #dir.getLens().setFilmSize(60, 60)
        #dir.getLens().setNearFar(0.1, 10000)
        
    return directional

def makePointLight(name, color, pos, falloff = 0.3):
    point = PointLight(name + "-point")
    point.setColor(color)
    ATTN_FCTR = 0.03
    point.setAttenuation((1, 0, falloff * ATTN_FCTR))
    pnp = render.attachNewNode(point)
    pnp.setPos(pos)
    if False:
        sm = loader.loadModel("models/smiley.egg.pz")
        sm.reparentTo(pnp)
    return pnp

def makeFog(name, color, expDensity):
    fog = Fog(name + "-fog")
    fog.setColor(color)
    fog.setExpDensity(expDensity)
    return fog

def makeSpotlight(name, color, pos, hpr):
    spot = Spotlight(name + "-spotlight")
    spot.setColor(color)
    if metadata.USE_REAL_SHADOWS:
        spot.setShadowCaster(True, 512, 512)
    snp = render.attachNewNode(spot)
    snp.setHpr(hpr)
    snp.setPos(pos)
    return snp

def isToon(toon):
    from src.coginvasion.toon.DistributedToon import DistributedToon
    return isinstance(toon, DistributedToon)

def isNPCToon(toon):
    from src.coginvasion.toon.DistributedNPCToon import DistributedNPCToon
    return isinstance(toon, DistributedNPCToon)

def isSuit(suit):
    from src.coginvasion.cog.DistributedSuit import DistributedSuit
    return isinstance(suit, DistributedSuit)

def isDisneyChar(char):
    from src.coginvasion.npc.DistributedDisneyChar import DistributedDisneyChar
    return isinstance(char, DistributedDisneyChar)


# A global waiting for others label
WaitForOthersLbl = None

def showWaitForOthers():
    global WaitForOthersLbl

    if WaitForOthersLbl:
        WaitForOthersLbl.show()
    else:
        from direct.gui.DirectGui import DirectLabel
        WaitForOthersLbl = DirectLabel(text="Waiting for others...", relief=None,
                                text_fg=(1,1,1,1), text_scale=0.08, text_shadow=(0,0,0,1))
        WaitForOthersLbl.setBin('unsorted', 1)

def hideWaitForOthers():
    if WaitForOthersLbl:
        WaitForOthersLbl.hide()
                         
ThemeSong = None
holidayTheme = None

def getThemeSong():
    global ThemeSong
    if not ThemeSong:
        ThemeSong = 'ciotheme_shortmellow'
        #themeList = ['ci_theme0', 'ci_theme5']#, 'ci_theme1', 'ci_theme2', 'ci_theme3', 'ci_theme4']
        #import random
        
        #if random.random() < 0.3:
        #    ThemeSong = themeList[1]
        #else:
        #    ThemeSong = themeList[0]
        
        #ThemeSong = random.choice(themeList)

    return ThemeSong

def getHolidayTheme():
    global holidayTheme
    if not holidayTheme:
        holidayTheme = 'ci_holiday_christmas_bgm'
    return holidayTheme

# Helper method to check if two objects are facing each other like so: -> <-
def areFacingEachOther(obj1, obj2):
    h1 = obj1.getH(render) % 360
    h2 = obj2.getH(render) % 360
    return not (-90.0 <= (h1 - h2) <= 90.0)
    
def fixGrayscaleTextures(np):
    for tex in np.findAllTextures():
        if (tex.getFormat() == Texture.F_luminance):
            print "Fixing grayscale texture", tex.getName()
            img = PNMImage()
            tex.store(img)
            img.makeRgb()
            tex.load(img)
            
def getLogoFont(font):
    # Returns a dynamic font in the style of the text from the new logo.
    # Same color as the logo text and has the same outline.
    # Make sure that you set fg to (1, 1, 1, 1), so you don't override the color
    # from this font.
    from panda3d.core import DynamicTextFont
    font = DynamicTextFont(font, 0)
    font.setFg((145 / 255.0, 145 / 255.0, 145 / 255.0, 1.0))
    font.setOutline((0 / 255.0, 0 / 255.0, 0 / 255.0, 1.0), 0.85, 0.175)
    font.setScaleFactor(1)
    return font
   
ToonLogoFont = None
MinnieLogoFont = None

def getToonLogoFont():
    global ToonLogoFont
    if not ToonLogoFont:
        ToonLogoFont = getLogoFont("phase_3/models/fonts/ImpressBT.ttf")
    return ToonLogoFont
    
def getMinnieLogoFont():
    global MinnieLogoFont
    if not MinnieLogoFont:
        MinnieLogoFont = getLogoFont("phase_3/models/fonts/MinnieFont.TTF")
    return MinnieLogoFont
    
def getLogoImage(parent = None, size = 1, pos = (0, 0, 0)):
    from direct.gui.DirectGui import OnscreenImage
    
    if not parent:
        parent = aspect2d
    
    logo = loader.loadTexture("phase_3/maps/CogInvasion_Logo.png")
    logoNode = parent.attachNewNode('logoNode')
    logoNode.setScale(size)
    logoNode.setPos(pos)
    factor = 0.315
    logoImg = OnscreenImage(image = logo, scale = (1.920 * factor, 0, 1.080 * factor), parent = logoNode)
    logoImg.setTransparency(1)
    
    return [logoNode, logoImg]

FloorBitmask = BitMask32(2)
WallBitmask = BitMask32(1)
EventBitmask = BitMask32(3)
CameraBitmask = BitMask32(4)
WeaponBitmask = BitMask32.bit(6)
LocalAvBitmask = BitMask32(7)
StreetVisGroupBitmask = BitMask32(8)

FloorGroup = BitMask32.bit(2)
WallGroup = BitMask32.bit(1)
EventGroup = BitMask32.bit(3)
CameraGroup = BitMask32.bit(4)
ShadowCameraBitmask = BitMask32.bit(5)
WeaponGroup = BitMask32.bit(6)
LocalAvGroup = BitMask32.bit(7)
StreetVisGroup = BitMask32.bit(8)
ViewModelCamMask = BitMask32.bit(15)
CharacterGroup = BitMask32.bit(9)

FloorMask = FloorGroup | StreetVisGroup

# For just colliding with the general world.
WorldGroup = WallGroup | FloorGroup | StreetVisGroup

DialogColor = (1, 1, 0.75, 1)
DefaultBackgroundColor = (0.3, 0.3, 0.3, 1)
PositiveTextColor = (0, 1, 0, 1)
NegativeTextColor = (1, 0, 0, 1)
OrangeTextColor = (1, 0.5, 0, 1)
YellowTextColor = (1, 1, 0, 1)

def getHeadsUpAngle(fromNP, to):
    _oldHpr = fromNP.getHpr()
    fromNP.headsUp(to)
    _newHpr = fromNP.getHpr()
    fromNP.setHpr(_oldHpr)
    return _newHpr

def getLookAtAngle(fromNP, to, offset):
    _oldHpr = fromNP.getHpr()
    fromNP.lookAt(to, offset)
    _newHpr = fromNP.getHpr()
    fromNP.setHpr(_oldHpr)
    return _newHpr

def getHeadsUpQuat(fromNP, to):
    _oldHpr = fromNP.getQuat()
    fromNP.headsUp(to)
    _newHpr = fromNP.getQuat()
    fromNP.setQuat(_oldHpr)
    return _newHpr

def getHeadsUpDistance(fromNP, to):
    _oldHpr = fromNP.getHpr()
    fromNP.headsUp(to)
    _newHpr = fromNP.getHpr()
    fromNP.setHpr(_oldHpr)
    _distance = (_newHpr.getXy() - _oldHpr.getXy()).length()
    return _distance
    
def getHeadsUpDistanceSquared(fromNP, to):
    _oldHpr = fromNP.getHpr()
    fromNP.headsUp(to)
    _newHpr = fromNP.getHpr()
    fromNP.setHpr(_oldHpr)
    _distance = (_newHpr.getXy() - _oldHpr.getXy()).lengthSquared()
    return _distance

# Cog classes that can be damaged by gags.
SuitClasses = ["DistributedSuit", "DistributedTutorialSuit", "DistributedCogOfficeSuit", "DistributedTakeOverSuit"]
ToonClasses = ["DistributedPlayerToon", "DistributedPlayerToonAI"]

DistrictNames = [
    'Boingy Acres',
    'Boingy Bay',
    'Boingy Summit',
    'Boingyboro',
    'Bouncy Summit',
    'Crazy Grove',
    'Crazy Hills',
    'Crazyham',
    'Funnyfield',
    'Giggly Bay',
    'Giggly Grove',
    'Giggly Hills',
    'Giggly Point',
    'Gigglyfield',
    'Gigglyham',
    'Goofy Valley',
    'Goofyport',
    'Kooky Grove',
    'Kookyboro',
    'Loopy Harbor',
    'Nutty Hills',
    'Nutty River',
    'Nutty Summit',
    'Nuttyville',
    'Nuttywood',
    'Silly Rapids',
    'Silly Valley',
    'Sillyham',
    'Toon Valley',
    'Zany Acres'
]

ToonStandableGround = 0.707
if (ConfigVariableBool('want-gta-controls', False)):
    ToonSpeedFactor = 1.25
else:
    ToonSpeedFactor = 1.25
ToonForwardSpeed = 16.0 * ToonSpeedFactor
ToonJumpForce = 24.0
ToonReverseSpeed = 8.0 * ToonSpeedFactor
ToonRotateSpeed = 80.0 * ToonSpeedFactor
ToonForwardSlowSpeed = 6.0
ToonJumpSlowForce = 4.0
ToonReverseSlowSpeed = 2.5
ToonRotateSlowSpeed = 33.0
ErrorCode2ErrorMsg = {}
SecretPlace = "Secret Place"
TryAgain = "Try again?"
NoConnectionMsg = "Could not connect to %s."
DisconnectionMsg = "Your internet connection to the servers has been unexpectedly broken."
#JoinFailureMsg = "There was a problem getting you into " + config.GetString('game-name') + ". Please restart the game."
SuitDefeatMsg = "You have been defeated by the " + Suits + "! Try again?"
ConnectingMsg = "Connecting..."
ServerUnavailable = "The server appears to be temporarily unavailable. Still trying..."
JoiningMsg = "Retrieving server info..."
OutdatedFilesMsg = "Your game files are out of date. Please run the game from the launcher."
ServerLockedMsg = "The server is locked."
NoShardsMsg = "No Cog Invasion Districts are available."
InvalidName = "Sorry, that name will not work."
Submitting = "Submitting..."
AlreadyLoggedInMsg = "You have been disconnected because someone else has logged into this account from another computer."
DistrictResetMsg = "The district you were playing in has been reset. Everybody playing in that district has been logged out."
DialogOk = "OK"
DialogCancel = "Cancel"
DialogNo = "No"
DialogYes = "Yes"
UpdateReg5Min = "The Cog Invasion server will be restarting for an update in 5 minutes."
UpdateReg1Min = "The Cog Invasion server will be restarting for an update in 60 seconds."
UpdateRegClosed = "The Cog Invasion server will be restarting now."
UpdateEmg5Min = "The Cog Invasion server will be closing for an emergency update in 5 minutes."
UpdateEmg1Min = "The Cog Invasion server will be closing for an emergency update in 60 seconds."
UpdateEmgClosed = "The Cog Invasion server is now closing for an emergency update. It shouldn't be too long until the server is back up."

CChar = 'cchar'

ModelPolys = {CChar: {"high": 1200,
                    "medium": 800,
                    "low": 400},
            Toon: {"high": 1000,
                    "medium": 500,
                    "low": 250}}
ModelDetail = None
OkayBtnGeom = None
CancelBtnGeom = None
DefaultBtnGeom = None

def getToonFont():
    global ToonFont
    if not ToonFont:
        ToonFont = loader.loadFont("phase_3/models/fonts/ImpressBT.ttf", lineHeight=1.0)
    return ToonFont

def getSuitFont():
    global SuitFont
    if not SuitFont:
        SuitFont = loader.loadFont("phase_3/models/fonts/vtRemingtonPortable.ttf", pixelsPerUnit=40, spaceAdvance=0.25, lineHeight=1.0)
    return SuitFont

def getMickeyFont():
    global MickeyFont
    if not MickeyFont:
        MickeyFont = loader.loadFont("phase_3/models/fonts/MickeyFont.bam")
    return MickeyFont

def getMinnieFont():
    global MinnieFont
    if not MinnieFont:
        MinnieFont = loader.loadFont("phase_3/models/fonts/MinnieFont.TTF")
    return MinnieFont

def getModelDetail(avatar):
    global ModelDetail
    model_detail = getSettingsMgr().getSetting("model-detail").getValue()
    ModelDetail = ModelPolys[avatar][model_detail]
    return ModelDetail

def getRolloverSound():
    global rolloverSfx
    rolloverSfx = loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg')
    rolloverSfx.setVolume(0.85)
    return rolloverSfx

def getClickSound():
    global clickSfx
    clickSfx = loader.loadSfx('phase_3/audio/sfx/GUI_click.ogg')
    clickSfx.setVolume(0.85)
    return clickSfx

def getOkayBtnGeom():
    global OkayBtnGeom
    if not OkayBtnGeom:
        OkayBtnGeom = (loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam").find('**/ChtBx_OKBtn_UP'),
                    loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam").find('**/ChtBx_OKBtn_DN'),
                    loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam").find('**/ChtBx_OKBtn_Rllvr'))
    return OkayBtnGeom

def getCancelBtnGeom():
    global CancelBtnGeom
    if not CancelBtnGeom:
        CancelBtnGeom = (loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam").find('**/CloseBtn_UP'),
                    loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam").find('**/CloseBtn_DN'),
                    loader.loadModel("phase_3/models/gui/dialog_box_buttons_gui.bam").find('**/CloseBtn_Rllvr'))
    return CancelBtnGeom

def getDefaultBtnGeom():
    global DefaultBtnGeom
    if not DefaultBtnGeom:
        btn = loader.loadModel("phase_3/models/gui/quit_button.bam")
        DefaultBtnGeom = (btn.find('**/QuitBtn_UP'),
                    btn.find('**/QuitBtn_DN'),
                    btn.find('**/QuitBtn_RLVR'))
    return DefaultBtnGeom

def makeOkayButton(text = "Okay", parent = None, text_scale = 0.045, text_pos = (0, -0.075),
                     geom_scale = 0.75, extraArgs = [], command = None, pos = (0, 0, 0)):
    from direct.gui.DirectGui import DirectButton
    if not parent:
        parent = aspect2d
    btn = DirectButton(text = text, geom = getOkayBtnGeom(),
                       parent = parent, pos = pos, text_scale = text_scale, text_pos = text_pos,
                       command = command, extraArgs = extraArgs, relief = None, geom_scale = geom_scale)
    return btn

def makeCancelButton(text = "Cancel", parent = None, text_scale = 0.045, text_pos = (0, -0.075),
                     geom_scale = 0.75, extraArgs = [], command = None, pos = (0, 0, 0)):
    from direct.gui.DirectGui import DirectButton
    if not parent:
        parent = aspect2d
    btn = DirectButton(text = text, geom = getCancelBtnGeom(),
                       parent = parent, pos = pos, text_scale = text_scale, text_pos = text_pos,
                       command = command, extraArgs = extraArgs, relief = None, geom_scale = geom_scale)
    return btn

def makeDirectionalBtn(direction, parent = None, pos = (0, 0, 0), command = None, extraArgs = []):
    """
    direction:
    0) left
    1) right
    """
    from direct.gui.DirectGui import DirectButton

    if not parent:
        parent = aspect2d

    if direction == 0:
        hpr = (180, 0, 0)
    else:
        hpr = (0, 0, 0)

    gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')
    btn = DirectButton(parent = parent, relief = None, geom = (gui.find('**/Horiz_Arrow_UP'),
                                                               gui.find('**/Horiz_Arrow_DN'),
                                                               gui.find('**/Horiz_Arrow_Rllvr'),
                                                               gui.find('**/Horiz_Arrow_UP')),
                       hpr = hpr, pos = pos, command = command, extraArgs = extraArgs)
    return btn

def makeDefaultScrolledListBtn(text = "", text_scale = 0.07, text_align = None, text1_bg = None, text2_bg = None, text3_fg = None,
                               textMayChange = 0, command = None, extraArgs = [], text_pos = (0, 0, 0), parent = None):
    from direct.gui.DirectGui import DirectButton
    from panda3d.core import TextNode, Vec4

    if not text_align:
        text_align = TextNode.ALeft
    if not text1_bg:
        text1_bg = Vec4(0.5, 0.9, 1, 1)
    if not text2_bg:
        text2_bg = Vec4(1, 1, 0, 1)
    if not text3_fg:
        text3_fg = Vec4(0.4, 0.8, 0.4, 1)
    if not parent:
        parent = aspect2d

    btn = DirectButton(
        relief=None, text=text, text_scale=text_scale,
        text_align=text_align, text1_bg=text1_bg, text2_bg=text2_bg,
        text3_fg=text3_fg, textMayChange=textMayChange, command=command,
        extraArgs=extraArgs, text_pos = text_pos, parent = parent
    )
    return btn

def makePulseEffectInterval(guiElement, defScale, minScale, maxScale, d1, d2):
    seq = Sequence()
    seq.append(LerpScaleInterval(guiElement, d1, maxScale, minScale, blendType = 'easeOut'))
    seq.append(LerpScaleInterval(guiElement, d2, defScale, maxScale, blendType = 'easeInOut'))
    return seq

def makeDefaultScrolledList(listXorigin = -0.02, listFrameSizeX = 0.625, listZorigin = -0.96, listFrameSizeZ = 1.04, items = [],
                            arrowButtonScale = 1.3, itemFrameXorigin = -0.237, itemFrameZorigin = 0.365, buttonXstartOffset = 0.293,
                            pos = (0, 0, 0), itemFrame_relief = None, itemFrame_scale = 1.0, numItemsVisible = 15, forceHeight = 0.075, parent = None,
                            itemFrame_borderWidth = (0.01, 0.01), itemFrame_frameColor = (0.85, 0.95, 1, 1)):
    from direct.gui.DirectGui import DirectScrolledList, DGG
    from panda3d.core import Vec4

    gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui.bam')

    buttonXstart = itemFrameXorigin + buttonXstartOffset
    if not itemFrame_relief:
        itemFrame_relief = DGG.SUNKEN
    if not parent:
        parent = aspect2d
    list = DirectScrolledList(
        relief=None,
        pos=pos,
        incButton_image=(gui.find('**/FndsLst_ScrollUp'),
            gui.find('**/FndsLst_ScrollDN'),
            gui.find('**/FndsLst_ScrollUp_Rllvr'),
            gui.find('**/FndsLst_ScrollUp')),
        incButton_relief=None,
        incButton_scale=(arrowButtonScale, arrowButtonScale, -arrowButtonScale),
        incButton_pos=(buttonXstart, 0, itemFrameZorigin - 0.999),
        incButton_image3_color=Vec4(1, 1, 1, 0.2),
        decButton_image=(gui.find('**/FndsLst_ScrollUp'),
            gui.find('**/FndsLst_ScrollDN'),
            gui.find('**/FndsLst_ScrollUp_Rllvr'),
            gui.find('**/FndsLst_ScrollUp')),
        decButton_relief=None,
        decButton_scale=(arrowButtonScale, arrowButtonScale, arrowButtonScale),
        decButton_pos=(buttonXstart, 0, itemFrameZorigin + 0.125),
        decButton_image3_color=Vec4(1, 1, 1, 0.2),
        itemFrame_pos=(itemFrameXorigin, 0, itemFrameZorigin),
        itemFrame_scale=itemFrame_scale,
        itemFrame_relief=itemFrame_relief,
        itemFrame_frameSize=(listXorigin,
            listXorigin + listFrameSizeX,
            listZorigin,
            listZorigin + listFrameSizeZ),
        itemFrame_frameColor=itemFrame_frameColor,
        itemFrame_borderWidth=itemFrame_borderWidth,
        numItemsVisible=numItemsVisible,
        forceHeight=forceHeight,
        items=items, parent = parent)
    return list

# It's about time this was made.
def makeDefaultBtn(text = "", text_pos = (0, -0.015), text_scale = 0.045, geom_scale = (0.6, 0.75, 0.75), geom_sx = None,
                   geom_sy = None, geom_sz = None, command = None, extraArgs = [], pos = (0, 0, 0), hpr = (0, 0, 0),
                   scale = 1.0, parent = None, relief = None, font = None, fitToText = False):

    from direct.gui.DirectGui import DirectButton

    if not parent:
        # We have to put this here and not in the arguments because ShowBase hasn't created aspect2d yet when it loads CIGlobals.
        parent = aspect2d

    if not font:
        font = getToonFont()
    
    if geom_sx is not None:
        geom_scale = (geom_sx, geom_scale[1], geom_scale[2])
    if geom_sy is not None:
        geom_scale = (geom_scale[0], geom_sy, geom_scale[2])
    if geom_sz is not None:
        geom_scale = (geom_scale[0], geom_scale[1], geom_sz)


    btn = DirectButton(text = text, text_pos = text_pos, text_scale = text_scale, geom_scale = geom_scale, command = command, text_font = font,
                       extraArgs = extraArgs, pos = pos, hpr = hpr, scale = scale, parent = parent, relief = relief, geom = getDefaultBtnGeom(),
                       )

    return btn

def getExitButton(cmd = None, extraArgs = [], pos = (0, 0, 0)):
    from direct.gui.DirectGui import DirectButton

    gui = loader.loadModel('phase_3.5/models/gui/inventory_gui.bam')
    up = gui.find('**/InventoryButtonUp')
    down = gui.find('**/InventoryButtonDown')
    rlvr = gui.find('**/InventoryButtonRollover')
    exitButton = DirectButton(image = (up, down, rlvr), relief = None,
                              text = 'Exit', text_fg = (1, 1, 0.65, 1),
                              text_pos=(0, -0.23), text_scale = 0.8,
                              image_scale = (11, 1, 11), pos = pos,
                              scale = 0.15, command = cmd, extraArgs = extraArgs,
                              image_color = (1, 0, 0, 1))
    return exitButton

ShadowScales = {Suit: 0.375,
                Toon: 0.375,
                CChar: 0.425}

def __fetchGagKey():
    gagKey = None
    if 'base' in globals() and hasattr(base, 'inputStore'):
        gagKey = base.inputStore.UseGag.upper()
    else:
        from src.coginvasion.manager.UserInputStorage import UserInputStorage
        tempStorage = UserInputStorage()
        gagKey = tempStorage.UseGag
    return gagKey

ToonTips = [
    "Try to use weaker Gags when around weaker Cogs to conserve Jellybeans.",
    "You can use the Gags page in your Shticker Book to change the Gags you can use.",
    "Press '{0}' to use a Gag! You can change that setting in your Shticker Book.".format(__fetchGagKey()),
    "You can click on other Toons to make friends with them!",
    "The Friends List is unlimited for now!",
    "Any blank spots you see on the Gags page in your Shticker Book represent Gags that are not implemented yet.",
    "Be sure to report a bug or crash when you run into one!",
    "Play Minigames at the Minigame Area to earn more Jellybeans!",
    "The only Minigame that works as single player is UNO.",
    "Different Minigames give different amounts of jellybeans.",
    "You can choose between Capture the Flag, King of the Hill, and Casual Mode in Toon Battle!",
    "You can choose between the Pistol, Shotgun, and the Sniper in Toon Battle!",
    "You can play with up to 7 other Toons in Toon Battle!",
    "You can choose between the Blue Bloodsuckers and the Red Robber Barons in Toon Battle!",
    "Wild Cards in UNO allow you to choose any color you want.",
    "When playing the Race Game, try to not press the same arrow key more than once, without pressing the other one.",
    "In the Race Game, everytime your Power Bar hits the top, your Boost Bar starts to fill!",
    "In the Race Game, press CONTROL to use Boost when the bar is full.",
    "Winning Toon Battle gives the most Jellybeans!",
    "It takes 5 seconds for your Camera to recharge in Camera Shy.",
    "Pictures only register in Camera Shy if the view finder is green.",
    "Waltz right in to any Gag Shop around Toontown to restock your gags!",
    "Level 12 Cogs can do up to 36 damage!",
    "Each area has different level Cogs.",
    "When taking over Cog Office Buildings, make sure to have a full Laff Meter!",
    "You can go to the Minigame Area by using your Shticker Book.",
    "You can change your screen resolution on the Options page in your Shticker Book.",
    "You can change whether you play the game in fullscreen or in a window using the Options page in your Shticker Book.",
    "You can turn Anti-Aliasing off and on using the Options Page in your Shticker Book.",
    "You can turn Anisotropic Filtering off and on using the Options page in your Shticker Book.",
    "You can change the way the game looks using the Options Page in the Shticker Book.",
    "You can switch Districts by using the Districts Page in your Shticker Book.",
    "You can see the population of the District you are in on the Districts Page in your Shticker Book.",
    "You must wait until a used Gag has completed before being able to use another one.",
    "Use Toon-Up gags to heal fellow Toons at any time!",
    "Use Squirt or Throw gags on fellow Toons to heal them up!",
    "Some gags such as Drop and Trap gags require you to use your mouse to aim."]
