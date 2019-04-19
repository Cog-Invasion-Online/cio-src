from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_CLIPONTIE
from src.coginvasion.cog.attacks.GenericThrowShared import StateThrow, ThrowAfterTime, AttackDuration, PlayRate

Metadata = {
    "Name" : "Clip-On-Tie",
    "ID" : ATTACK_CLIPONTIE,
    "StateThrow" : StateThrow,
    "ModelPath" : "phase_5/models/props/power-tie.bam",
    "ModelScale" : 4,
    "ModelAngles" : Point3(0, 0, 180),

    "ImpactSoundPath" : "phase_5/audio/sfx/SA_powertie_impact.ogg",
    "ThrowSoundPath" : "phase_5/audio/sfx/SA_powertie_throw.ogg",
    "ThrowPower" : 200.0,
    "ThrowAfterTime" : ThrowAfterTime,
    "AttackDuration" : AttackDuration,
    "PlayRate" : PlayRate
}

