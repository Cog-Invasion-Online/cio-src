TempEnts = {
    'TE_EXPLOSION'  : 1,
    'TE_SPLAT'      : 2,
    'TE_DUSTCLOUD'  : 3,
    'TE_BULLET_RICOCHET'   : 4,
    'TE_DECAL_TRACE'        : 5,
    'TE_LASER'      : 6
}

globals().update(TempEnts)

from direct.showbase.PythonUtil import invertDictLossless
TempEntsInverted = invertDictLossless(TempEnts)
