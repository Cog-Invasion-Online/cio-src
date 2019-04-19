from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_HALF_WINDSOR
from src.coginvasion.cog.attacks.GenericThrowShared import ThrowAfterTime, AttackDuration, PlayRate, ThrowPower, StateThrow

Metadata = {
    "Name" : "Half Windsor",
    "ID" : ATTACK_HALF_WINDSOR,
    "StateThrow" : StateThrow,
    "ModelPath" : "phase_5/models/props/half-windsor.bam",
    "ModelScale" : 6.0,
    "ModelAngles" : Point3(90.0, 0.0, 90.0),
    "ModelOrigin" : Point3(0.0, -1.6, -1.0),

    "ThrowAfterTime" : ThrowAfterTime,
    "AttackDuration" : AttackDuration,
    "ThrowPower" : ThrowPower,
    "ThrowSoundPath" : "phase_5/audio/sfx/SA_powertie_throw.ogg",
    "PlayRate" : PlayRate,
    "WantLight" : False,
}

