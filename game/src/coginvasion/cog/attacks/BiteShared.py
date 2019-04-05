from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_BITE
from src.coginvasion.cog.attacks.GenericThrowShared import StateThrow, ThrowAfterTime, ThrowPower, AttackDuration, PlayRate

Name = "Bite"
ID = ATTACK_BITE
StateThrow = StateThrow
ModelPath = "phase_5/models/props/teeth-mod.bam"
ModelScale = 6.0
ModelAngles = Point3(0.0, 0.0, 180.0)

ThrowAfterTime = ThrowAfterTime
AttackDuration = AttackDuration
ThrowPower = ThrowPower
PlayRate = PlayRate
WantLight = False
