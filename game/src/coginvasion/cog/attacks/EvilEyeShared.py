from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_EVIL_EYE
from src.coginvasion.cog.attacks.GenericThrowShared import StateThrow, AttackDuration, PlayRate

Metadata = {
    "Name"  :   "Evil-Eye",
    "ID"    :   ATTACK_EVIL_EYE,
    "ModelPath" :   "phase_5/models/props/evil-eye.bam",
    "ModelScale"    :    11.0,
    "EyeOrigin" : Point3(-0.4, 3.65, 5.01),
    "StateThrow" : StateThrow,
    "ThrowPower" : 75.0,
    "ThrowAfterTime" : 2.81,
    "AttackDuration" : 8.0,
    "PlayRate" : PlayRate,
    "WantLight" : False
}

