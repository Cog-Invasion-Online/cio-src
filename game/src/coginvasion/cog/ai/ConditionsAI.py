COND_NONE               = 0
COND_SEE_HATE           = 1 << 0 # see something that you hate
COND_SEE_FEAR           = 1 << 1 # see something that you are afraid of
COND_SEE_DISLIKE        = 1 << 2 # see something that you dislike
COND_SEE_TARGET         = 1 << 3 # target entity is in full view
COND_SEE_FRIEND         = 1 << 12
COND_TARGET_OCCLUDED    = 1 << 4 # target entity occluded by the world
COND_TARGET_TOOFAR      = 1 << 5
COND_LIGHT_DAMAGE       = 1 << 6
COND_HEAVY_DAMAGE       = 1 << 7
COND_NEW_TARGET         = 1 << 8
COND_TARGET_FACING_ME   = 1 << 9
COND_TARGET_DEAD        = 1 << 10
COND_LOW_HEALTH         = 1 << 11
COND_TARGET_CHARGING    = 1 << 13 # target is moving towards me
COND_TASK_FAILED        = 1 << 14
COND_SCHEDULE_DONE      = 1 << 15
COND_CAN_ATTACK         = 1 << 16

AllConditions = [
    COND_SEE_HATE,
    COND_SEE_FEAR,
    COND_SEE_DISLIKE,
    COND_SEE_TARGET,
    COND_SEE_FRIEND,
    COND_TARGET_OCCLUDED,
    COND_TARGET_TOOFAR,
    COND_LIGHT_DAMAGE,
    COND_HEAVY_DAMAGE,
    COND_NEW_TARGET,
    COND_TARGET_FACING_ME,
    COND_TARGET_DEAD,
    COND_LOW_HEALTH,
    COND_TARGET_CHARGING,
    COND_TASK_FAILED,
    COND_SCHEDULE_DONE,
    COND_CAN_ATTACK
]
