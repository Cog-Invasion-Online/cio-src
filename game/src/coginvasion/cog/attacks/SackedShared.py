from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_SACKED
from src.coginvasion.cog.attacks.GenericThrowShared import StateThrow, ThrowAfterTime, ThrowPower, AttackDuration, PlayRate

Metadata = {
    "Name" : "Sacked",
    "ID" : ATTACK_SACKED,
    "ModelPath" : "phase_5/models/props/sandbag-mod.bam",
    "ModelAngles" : Point3(0.0, 90.0, 180.0),
    "ModelOrigin" : Point3(0.0, -2.8, 0.3),

    "StateThrow" : StateThrow,
    "ThrowAfterTime" : ThrowAfterTime,
    "AttackDuration" : AttackDuration,
    "ThrowPower" : ThrowPower,
    "PlayRate" : PlayRate
}

