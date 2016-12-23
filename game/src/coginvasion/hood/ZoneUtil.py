from src.coginvasion.globals.CIGlobals import *

def isInInterior(zoneId):
    return int(str(zoneId)[1:]) >= 500 and int(str(zoneId)[1:]) <= 999

def getWhereName(zoneId):
    if str(zoneId)[-3:] == '000':
        return 'playground'
    elif int(str(zoneId)[-3:]) < 400:
        return 'street'
    elif isInInterior(zoneId):
        return 'toonInterior'
    else:
        return 'street'

def getBranchZone(zoneId):
    branchZone = zoneId - zoneId % 100
    if zoneId % 1000 >= 500:
        branchZone -= 500
    return branchZone
    
def getStreetName(zoneId):
    return BranchZone2StreetName[getBranchZone(zoneId)]

def getLoaderName(zoneId):
    if str(getBranchZone(zoneId))[-3:] == '000':
        return 'safeZoneLoader'
    elif int(str(getBranchZone(zoneId))[-3:]) >= 100 and int(str(getBranchZone(zoneId))[-3:]) <= 999:
        return 'townLoader'
    else:
        return None

def isStreetInSameHood(zoneId):
    return str(zoneId)[0] == str(base.localAvatar.zoneId)[0]

def isStreet(zoneId):
    return getWhereName(zoneId) == 'street'

def getCanonicalBranchZone(zoneId):
    return getBranchZone(getCanonicalZoneId(zoneId))

def getCanonicalZoneId(zoneId):
    zoneId = zoneId % 2000
    if zoneId < 1000:
        zoneId = zoneId + ToontownCentralId
    else:
        zoneId = zoneId - 1000 + GoofySpeedwayId
    return zoneId

def getTrueZoneId(zoneId, currentZoneId):
    hoodId = getHoodId(zoneId, street = 1)
    offset = currentZoneId - currentZoneId % 2000
    if hoodId == ToontownCentral and game.process != 'client' or game.process == 'client' and hoodId == ToontownCentral:
        return zoneId - ToontownCentralId + offset
    elif hoodId == GoofySpeedway:
        return zoneId - GoofySpeedwayId + offset + 1000
    return zoneId

def getHoodId(zoneId, street = 0):
    if street:
        if str(zoneId)[0] == '1' and len(str(zoneId)) == 4:
            return DonaldsDock
        elif str(zoneId)[:2] == '10' and len(str(zoneId)) == 5:
            return MinigameArea
        elif str(zoneId)[:2] == '12' and len(str(zoneId)) == 5:
            return CogTropolis
        elif str(zoneId)[0] == '2':
            return ToontownCentral
        elif str(zoneId)[0] == '3':
            return TheBrrrgh
        elif str(zoneId)[0] == '4':
            return MinniesMelodyland
        elif str(zoneId)[0] == '5':
            return DaisyGardens
        elif str(zoneId)[0] == '9':
            return DonaldsDreamland
    else:
        if zoneId < DynamicZonesBegin:
            return ZoneId2Hood.get(zoneId, None)

def getZoneId(hoodId):
    if hoodId == BattleTTC:
        hoodId = ToontownCentral
    return Hood2ZoneId[hoodId]
    
def isOnSameStreet(zoneId):
    return getBranchZone(zoneId) == getBranchZone(base.localAvatar.zoneId)
    
def isOnCurrentPlayground(zoneId):
    return getHoodId(getBranchZone(zoneId)) == getHoodId(base.localAvatar.zoneId, 1)
    
def isLocatedInCurrentPlayground(zoneId):
    return getHoodId(zoneId, 1) == getHoodId(base.localAvatar.zoneId, 1)
    
def isAtSamePlaygroundButDifferentBranch(zoneId):
    return isLocatedInCurrentPlayground(zoneId) and not isOnSameStreet(zoneId)
