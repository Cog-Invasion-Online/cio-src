ActivityEnum = {
    'ACT_NONE'            : -2,
    'ACT_FINISH'          : -1,
    'ACT_WAKE_ANGRY'      : 0,
    'ACT_SMALL_FLINCH'    : 1,
    'ACT_DIE'             : 2,
    'ACT_GOON_SCAN'       : 3,
    'ACT_VICTORY_DANCE'   : 4,
    'ACT_COG_FLY_DOWN'    : 5,
    'ACT_JUMP'            : 6,
    'ACT_TOON_BOW'        : 7,
    'ACT_SIT'             : 8,
    'ACT_TOON_PRESENT'    : 9,
    'ACT_TOON_POINT'      : 10,
    'ACT_PRESS_BUTTON'    : 11,
    'ACT_IDLE'            : 12,
    'ACT_VP_THROW'        : 13,
    'ACT_VP_STUN'         : 14,
    'ACT_RANGE_ATTACK1'   : 15,
    'ACT_RANGE_ATTACK2'   : 16,
    'ACT_TOON_FALL'       : 17,
    'ACT_STUN'            : 18
}

globals().update(ActivityEnum)

def getActivityByName(enumName):
    return ActivityEnum.get(enumName, -1)

