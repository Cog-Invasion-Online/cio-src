from panda3d.core import Point3

from src.coginvasion.attack.Attacks import ATTACK_EVIL_EYE
from src.coginvasion.cog.attacks.GenericThrowShared import StateThrow, ThrowPower, AttackDuration, PlayRate

Name = "Evil-Eye"
ID = ATTACK_EVIL_EYE
ModelPath = "phase_5/models/props/evil-eye.bam"
ModelScale = 11.0
EyeOrigin = Point3(-0.4, 3.65, 5.01)

StateThrow = StateThrow
ThrowPower = ThrowPower
ThrowAfterTime = 2.81
AttackDuration = AttackDuration
PlayRate = PlayRate
WantLight = False
