from pandac.PandaModules import VBase4, PGButton, TP_normal


CCLocal = 0
CCNoChat = 1
CCNPC = 2
CCSuit = 3
CCToonBuilding = 4
CCSuitBuilding = 5
CCHouseBuilding = 6
CCOtherPlayer = 7
CCFreeChat = 8

CHAT = 0
SPEEDCHAT = 1

CHAT_BALLOON = 0
THOUGHT_BALLOON = 1

cardModel = None
arrowModel = None
chatBalloon3dModel = None
chatBalloon3dWidth = 0
chatBalloon3dHeight = 0
chatBalloon2dModel = None
chatBalloon2dWidth = 0
chatBalloon2dHeight = 0
thoughtBalloonModel = None
thoughtBalloonWidth = 0
thoughtBalloonHeight = 0
noButton = (None, None, None, None)
pageButton = (None, None, None, None)
quitButton = (None, None, None, None)
quitButtonWidth = 0
quitButtonHeight = 0

rolloverSound = None
clickSound = None

me = None
want2dNametags = True
forceOnscreenChat = False
force2dNametags = False
wantActiveNametags = True

nametags = []

def appendNametag(tag):
    global nametags
    nametags.append(tag)

def removeNametag(tag):
    global nametags
    nametags.remove(tag)

def makeTagsReady():
    global nametags
    # Make every single nametag in the nametag pool ready, if it's clickable.
    for tag in nametags:
        if tag.isClickable():
            tag.setClickState(PGButton.SReady)

def makeTagsInactive():
    global nametags
    # Make every single nametag in the nametag pool inactive.
    for tag in nametags:
        tag.setClickState(PGButton.SInactive)

def setCardModel(model):
    global cardModel
    cardModel = loader.loadModel(model)


def setArrowModel(model):
    global arrowModel
    arrowModel = loader.loadModel(model)


def setChatBalloon3dModel(model):
    global chatBalloon3dModel
    global chatBalloon3dWidth
    global chatBalloon3dHeight
    chatBalloon3dModel = loader.loadModel(model)
    chatBalloon3dWidth, chatBalloon3dHeight = getModelWidthHeight(chatBalloon3dModel)


def setChatBalloon2dModel(model):
    global chatBalloon2dModel
    global chatBalloon2dWidth
    global chatBalloon2dHeight
    chatBalloon2dModel = loader.loadModel(model)
    chatBalloon2dWidth, chatBalloon2dHeight = getModelWidthHeight(chatBalloon2dModel)


def setThoughtBalloonModel(model):
    global thoughtBalloonModel
    global thoughtBalloonWidth
    global thoughtBalloonHeight
    thoughtBalloonModel = loader.loadModel(model)
    thoughtBalloonWidth, thoughtBalloonHeight = getModelWidthHeight(thoughtBalloonModel)


def setPageButton(normal, down, rollover, disabled):
    global pageButton
    pageButton = (normal, down, rollover, disabled)


def setQuitButton(normal, down, rollover, disabled):
    global quitButton
    global quitButtonWidth
    global quitButtonHeight
    quitButton = (normal, down, rollover, disabled)
    quitButtonWidth, quitButtonHeight = getModelWidthHeight(normal)


def setRolloverSound(sound):
    global rolloverSound
    rolloverSound = sound


def setClickSound(sound):
    global clickSound
    clickSound = sound


def setMe(nodePath):
    global me
    me = nodePath


def setWant2dNametags(value):
    global want2dNametags
    want2dNametags = value


def setForceOnscreenChat(value):
    global forceOnscreenChat
    forceOnscreenChat = value


def setForce2dNametags(value):
    global force2dNametags
    force2dNametags = value


def setWantActiveNametags(value):
    global wantActiveNametags
    wantActiveNametags = value


def getModelWidthHeight(model):
    tightBounds = model.getTightBounds()
    if tightBounds is None:
        return (0, 0)
    minPoint, maxPoint = tightBounds
    width = maxPoint.getX() - minPoint.getX()
    height = maxPoint.getZ() - minPoint.getZ()
    return (width, height)




# Foreground, background:
NametagColors = {
    CCLocal: (
        (VBase4(0.3, 0.3, 0.7, 1.0), VBase4(0.9, 0.9, 0.9, 0.5)),   # Normal
        (VBase4(0.3, 0.3, 0.7, 1.0), VBase4(0.2, 0.2, 0.2, 0.5)),  # Down
        (VBase4(0.5, 0.5, 1.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.3, 0.3, 0.7, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    ),
    CCNoChat: (
        (VBase4(0.8, 0.4, 0.0, 1.0), VBase4(0.8, 0.8, 0.8, 0.5)),   # Normal
        (VBase4(1.0, 0.5, 0.5, 1.0), VBase4(0.2, 0.2, 0.2, 0.5)),  # Click
        (VBase4(1.0, 0.5, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.8, 0.4, 0.0, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    ),
    CCNPC: (
        (VBase4(0.0, 0.4, 0.0, 1.0), VBase4(0.9, 0.9, 0.9, 0.5)),   # Normal
        (VBase4(0.0, 0.5, 0.0, 1.0), VBase4(0.2, 0.2, 0.2, 0.5)),  # Down
        (VBase4(0.0, 0.7, 0.2, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.4, 0.0, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    ),
    CCSuit: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(0.9, 0.9, 0.9, 0.5)),   # Normal
        (VBase4(1.0, 1.0, 1.0, 1.0), VBase4(0.2, 0.2, 0.2, 0.5)),  # Down
        (VBase4(0.4, 0.4, 0.4, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0, 0, 0, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    ),
    CCSuitBuilding: (
        (VBase4(0.5, 0.5, 0.5, 1.0), VBase4(0.8, 0.8, 0.8, 0.5)),   # Normal
        (VBase4(0.5, 0.5, 0.5, 1.0), VBase4(0.8, 0.8, 0.8, 0.5)),  # Down
        (VBase4(0.5, 0.5, 0.5, 1.0), VBase4(0.8, 0.8, 0.8, 1.0)),  # Rollover
        (VBase4(0.5, 0.5, 0.5, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    ),
    CCToonBuilding: (
        (VBase4(0.2, 0.6, 0.9, 1.0), VBase4(0.8, 0.8, 0.8, 0.5)),   # Normal
        (VBase4(0.2, 0.6, 0.9, 1.0), VBase4(0.8, 0.8, 0.8, 0.5)),  # Down
        (VBase4(0.2, 0.6, 0.9, 1.0), VBase4(0.8, 0.8, 0.8, 1.0)),  # Rollover
        (VBase4(0.2, 0.6, 0.9, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    ),
    CCHouseBuilding: (
        (VBase4(0.2, 0.6, 0.9, 1.0), VBase4(0.8, 0.8, 0.8, 0.5)),   # Normal
        (VBase4(0.2, 0.2, 0.5, 1.0), VBase4(0.2, 0.2, 0.2, 0.5)),  # Down
        (VBase4(0.5, 0.5, 1.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.6, 0.2, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    ),
    CCOtherPlayer: (
        (VBase4(0.8, 0.4, 0.0, 1.0), VBase4(0.9, 0.9, 0.9, 0.5)),   # Normal
        (VBase4(0.8, 0.4, 0.0, 1.0), VBase4(0.2, 0.2, 0.2, 0.5)),  # Down
        (VBase4(0.8, 0.4, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.8, 0.4, 0.0, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    ),
    CCFreeChat: (
        (VBase4(0.3, 0.3, 0.7, 1.0), VBase4(0.8, 0.8, 0.8, 0.5)),   # Normal
        (VBase4(0.2, 0.2, 0.5, 1.0), VBase4(0.2, 0.2, 0.2, 0.5)),  # Down
        (VBase4(0.5, 0.5, 1.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.3, 0.3, 0.7, 1.0), VBase4(0.8, 0.8, 0.8, 0.5))    # Disabled
    )
}

# Foreground, background:
ChatColors = {
    CCLocal: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(1.0, 0.5, 0.5, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Down
        (VBase4(0.0, 0.6, 0.6, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    ),
    CCNoChat: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(1.0, 0.5, 0.5, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Click
        (VBase4(0.0, 0.6, 0.6, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    ),
    CCNPC: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(1.0, 0.5, 0.5, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Click
        (VBase4(0.0, 0.6, 0.6, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    ),
    CCSuit: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(1.0, 0.5, 0.5, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Down
        (VBase4(0.0, 0.6, 0.6, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    ),
    CCSuitBuilding: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Down
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    ),
    CCToonBuilding: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Down
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    ),
    CCHouseBuilding: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(1.0, 0.5, 0.5, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Down
        (VBase4(0.0, 0.6, 0.6, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    ),
    CCOtherPlayer: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(1.0, 0.5, 0.5, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Down
        (VBase4(0.0, 0.6, 0.6, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    ),
    CCFreeChat: (
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Normal
        (VBase4(1.0, 0.5, 0.5, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Down
        (VBase4(0.0, 0.6, 0.6, 1.0), VBase4(1.0, 1.0, 1.0, 1.0)),  # Rollover
        (VBase4(0.0, 0.0, 0.0, 1.0), VBase4(1.0, 1.0, 1.0, 1.0))   # Disabled
    )
}
