ActivityEnum = {
    'ACT_NONE'            : -1,
    'ACT_WAKE_ANGRY'      : 0,
    'ACT_SMALL_FLINCH'    : 1,
    'ACT_DIE'             : 2,
    'ACT_GOON_SCAN'       : 3,
    'ACT_VICTORY_DANCE'   : 4,
    'ACT_COG_FLY_DOWN'    : 5,
    'ACT_JUMP'            : 6,
    'ACT_TOON_BOW'        : 7
}

globals().update(ActivityEnum)

def getActivityByName(enumName):
    return ActivityEnum.get(enumName, -1)

