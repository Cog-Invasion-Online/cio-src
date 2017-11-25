########################################
# Filename: ToonGlobals.py
# Created by: DecodedLogic (14Feb16)
########################################

from src.coginvasion.globals import CIGlobals

# First argument is phase, next is type, body part, pant type, and finally model detail.
# Pant type is either: shorts or skirt.
# Type is either: dgs, dgm, or dgl.

BASE_MODEL = "phase_%s/models/char/tt_a_chr_%s_%s_%s_%s.bam"

# These are the animations
# Key is the code name of the animation,
# Value starts with phase number, second
# is the actual file name of the animation.
# If you aren't using the base model, you must
# specify the path of the animation after the file name.

ANIMATIONS = {
    "neutral" : [3, "neutral"],
    "run" : [3, "run"],
    "walk" : [3.5, "walk"],
    "pie" : [3.5, "pie-throw"],
    "fallb" : [4, "slip-backward"],
    "fallf" : [4, "slip-forward"],
    "lose" : [5, "lose"],
    "win" : [3.5, "victory-dance"],
    "squirt" : [5, "water-gun"],
    "zend" : [3.5, "jump-zend"],
    "zstart" : [3.5, "jump-zstart"],
    "zhang" : [3.5, "jump-zhang"],
    "tele" : [3.5, "teleport"],
    "book" : [3.5, "book"],
    "leap": [3.5, "leap_zhang"],
    "jump": [3.5, "jump-zhang"],
    "happy": [3.5, "jump"],
    "shrug": [3.5, "shrug"],
    "hdance": [5, "happy-dance"],
    "wave": [3.5, "wave"],
    "swim": [4, "swim"],
    "toss": [5, "toss"],
    "cringe": [3.5, "cringe"],
    "conked": [3.5, "conked"],
    "catchneutral": [4, "gameneutral"],
    "catchrun": [4, "gamerun"],
    "hold-bottle": [5, "hold-bottle"],
    "push-button" : [3.5, "press-button"],
    "happy-dance" : [5, "happy-dance"],
    "juggle" : [5, "juggle"],
    "shout": [5, "shout"],
    "dneutral": [4, "sad-neutral"],
    "dwalk": [4, "losewalk"],
    "smooch" : [5, "smooch"],
    "conked" : [3.5, "conked"],
    "sound" : [5, "shout"],
    "sprinkle-dust" : [5, "sprinkle-dust"],
    "start-sit" : [4, "intoSit"],
    "sit" : [4, "sit"],
    "water": [3.5, "water"],
    "spit": [5, "spit"],
    "firehose": [5, "firehose"],
    "applause": [4, "applause"],
    "left" : [4, "left"],
    "strafe" : [3, "strafe"],
    "pout" : [6, "badloop-putt"],
    "bow"   :   [4, "bow"],
    "shrug" :   [3.5, "shrug"],
    "bored" :   [4, "bored"],
    "start-dig" : [5.5, "into_dig"],
    "loop-dig" : [5.5, "loop_dig"]
}

# These are the admin tokens
# Key is token id, value is the actual model id.
STAFF_TOKENS = {CIGlobals.DevToken : 500, CIGlobals.ModToken : 300}

def generateBodyPart(toon, bodyPart, partType, partPhase, pantType):
    partAnimations = {}

    # Load the body part.
    mdlPath = BASE_MODEL % (partPhase, partType, pantType, bodyPart,
        str(CIGlobals.getModelDetail(toon.avatarType)))

    if '_-' in mdlPath:
        mdlPath = mdlPath.replace('_-', '-')

    if '__' in mdlPath:
        mdlPath = mdlPath.replace('__', '_')

    toon.loadModel(mdlPath, bodyPart)

    # Load the body part animations.
    for animName in ANIMATIONS:
        animationData = ANIMATIONS[animName]
        animPath = None

        if len(animationData) == 2:
            animPhase = animationData[0]
            animFile = animationData[1]

            # Let's create the path for the animation.
            animPath = BASE_MODEL % (animPhase, partType, pantType,
                bodyPart, animFile)

            if '_-' in animPath:
                animPath = animPath.replace('_-', '-')

            if '__' in animPath:
                animPath = animPath.replace('__', '_')

        partAnimations[animName] = animPath

    toon.loadAnims(partAnimations, bodyPart)
