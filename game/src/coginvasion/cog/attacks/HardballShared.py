from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_HARDBALL
from src.coginvasion.cog.attacks.GenericThrowShared import ThrowAfterTime, AttackDuration, PlayRate, ThrowPower, StateThrow

Metadata = {
    "Name" : "Hardball",
    "ID" : ATTACK_HARDBALL,
    "StateThrow" : StateThrow,
    "ModelScale" : 10.0,
    "ModelPath" : "phase_5/models/props/baseball.bam",
    "ModelOrigin" : Point3(0.0, 0.0, -0.5),

    "ThrowSoundPath" : "phase_5/audio/sfx/SA_hardball_throw_only.ogg",
    "ThrowAfterTime" : ThrowAfterTime,
    "AttackDuration" : AttackDuration,
    "ThrowPower" : ThrowPower,
    "PlayRate" : PlayRate,

    "WantLight" : False
}
